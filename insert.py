from __future__ import annotations

import psycopg

import random
import csv
import json
from faker import Faker

import time
import os
from tools import fake
from config import load_config

def insert_alumnos():
    cantidad_lote = 100
    lotes = 1
    tiempo_total = 0.0

    print(f"Insertando { lotes } lotes de alumnos...")    

    # Borramos el archivo si existe de una ejecución anterior fallida
    if os.path.exists('temp_data.csv'):
        os.remove('temp_data.csv')

    # Generación de todos los lotes
    for i in range(1, lotes + 1):
        start_time = time.perf_counter()
        # Insertamos lote, usando array_insert=[] para que no se acumulen los datos
        alumnos_raw = fake.generate_rows(cantidad_lote, locale="es_ES", attrs=["name", "email"], seed=123 + i, array_insert=[])

        # Añadimos saldo aleatorio entre 50 y 1500 €
        alumnos = [(nombre, email, round(random.uniform(50.0, 1500.0), 2)) for nombre, email in alumnos_raw]

        # Se añaden al final del CSV
        with open('temp_data.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Escribimos los datos
            writer.writerows(alumnos)
        
        end_time = time.perf_counter()
        tiempo_lote = end_time - start_time
        print(f"Tiempo de generación del lote {i}: { tiempo_lote }s") # VERBOSE

        # Sumamos al tiempo total
        tiempo_total += tiempo_lote

    cfg = load_config()

    print(f"Insertando datos a la base de datos con COPY...") # VERBOSE
    start_time = time.perf_counter()
    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            with open('temp_data.csv', 'r', encoding='utf-8') as f:
                with cur.copy("COPY alumnos(nombre, email_alumno, saldo) FROM STDIN WITH (FORMAT csv)") as copy:
                    while data := f.read(8192):
                        copy.write(data)
    end_time = time.perf_counter()
    tiempo_copy = end_time - start_time
    print(f"Tiempo de inserción COPY: { tiempo_copy }s") # VERBOSE
    tiempo_total += tiempo_copy
    
    if os.path.exists("temp_data.csv"):
        os.remove("temp_data.csv")
    
    print(f"Tiempo total de la inserción de { lotes } lotes: {tiempo_total:.4f}s") # VERBOSE
    return

def insert_profesores():
    cantidad_lote = 100
    lotes = 1
    tiempo_total = 0.0

    print(f"Insertando { lotes } lotes de profesores...")

    if os.path.exists('temp_profesores.csv'):
        os.remove('temp_profesores.csv')

    # Generación de todos los lotes
    for i in range(1, lotes + 1):
        start_time = time.perf_counter()
        # Insertamos lote
        profesores = fake.generate_rows(cantidad_lote, locale="es_ES", attrs=["name", "email"], seed=123 + i, array_insert=[])

        with open('temp_profesores.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(profesores)

        end_time = time.perf_counter()
        tiempo_lote = end_time - start_time
        print(f"Tiempo de generación del lote {i}: { tiempo_lote }s") # VERBOSE

        # Sumamos al tiempo total
        tiempo_total += tiempo_lote
    
    cfg = load_config()

    print(f"Insertando datos a la base de datos con COPY...") # VERBOSE
    start_time = time.perf_counter()
    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            with open('temp_profesores.csv', 'r', encoding='utf-8') as f:
                with cur.copy("COPY profesores(nombre, email_profesor) FROM STDIN WITH (FORMAT csv)") as copy:
                    while data := f.read(8192):
                        copy.write(data)
    end_time = time.perf_counter()
    tiempo_copy = end_time - start_time
    print(f"Tiempo de inserción COPY: { tiempo_copy }s") # VERBOSE
    tiempo_total += tiempo_copy
    
    if os.path.exists('temp_profesores.csv'):
        os.remove('temp_profesores.csv')

    print(f"Tiempo total de los { lotes } lotes: {tiempo_total:.4f}s") # VERBOSE
    return

def insert_asignaturas() -> int:
    cantidad_lote = 110
    lotes = 1
    tiempo_total = 0.0
    used_ids = []

    print(f"Insertando { lotes } lotes de asignaturas...")

    profesores_count_sql = "SELECT COUNT(*) FROM profesores"
    cfg = load_config()

    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            cur.execute(profesores_count_sql)
            count_profesores = cur.fetchone()[0]

    if os.path.exists('temp_asignaturas.csv'):
        os.remove('temp_asignaturas.csv')

    fake_en = Faker("en_US")

    # Generación de todos los lotes
    for i in range(1, lotes + 1):
        start_time = time.perf_counter()
        fake_en.seed_instance(123 + i)

        asignaturas_raw = fake.generate_rows(cantidad_lote, locale="es_ES", attrs=["company"], seed=123 + i, max_rand_number=count_profesores, used_ids=used_ids, array_insert=[])
        
        # Añadimos precio (entre 50 y 800 €) y max_alumnos (entre 5 y 50)
        asignaturas = []
        for profesor_id, nombre_es in asignaturas_raw:
            nombre_en = fake_en.company()
            asignaturas.append((
                profesor_id, 
                json.dumps({"es": nombre_es, "en": nombre_en}), 
                round(random.uniform(50.0, 800.0), 2), 
                random.randint(5, 50)
            ))

        with open('temp_asignaturas.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(asignaturas)

        end_time = time.perf_counter()
        tiempo_lote = end_time - start_time
        print(f"Tiempo de generación del lote {i}: { tiempo_lote }s") # VERBOSE

        # Sumamos al tiempo total
        tiempo_total += tiempo_lote

    print(f"Insertando datos a la base de datos con COPY...") # VERBOSE
    start_time = time.perf_counter()
    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            with open('temp_asignaturas.csv', 'r', encoding='utf-8') as f:
                with cur.copy("COPY asignaturas(profesor_id, nombre, precio, max_alumnos) FROM STDIN WITH (FORMAT csv)") as copy:
                    while data := f.read(8192):
                        copy.write(data)
    end_time = time.perf_counter()
    tiempo_copy = end_time - start_time
    print(f"Tiempo de inserción COPY: { tiempo_copy }s") # VERBOSE
    tiempo_total += tiempo_copy
    
    if os.path.exists('temp_asignaturas.csv'):
        os.remove('temp_asignaturas.csv')
    
    print(f"Tiempo total de los { lotes } lotes: {tiempo_total:.4f}s") # VERBOSE
    return

def insert_matriculas() -> int:
    cantidad_lote = 100
    lotes = 1
    tiempo_total = 0.0

    print(f"Insertando { lotes } lotes de matrículas...")

    asignaturas_count_sql = "SELECT COUNT(*) FROM asignaturas"
    alumnos_count_sql = "SELECT COUNT(*) FROM alumnos"
    cfg = load_config()

    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            # Obtener el ID máximo de asignaturas y alumnos
            cur.execute(asignaturas_count_sql)
            max_asignaturas = cur.fetchone()[0]

            cur.execute(alumnos_count_sql)
            max_alumnos = cur.fetchone()[0]

    if os.path.exists('temp_matriculas.csv'):
        os.remove('temp_matriculas.csv')

    for i in range(1, lotes + 1):
        start_time = time.perf_counter()
        
        # Generamos el lote completo en memoria
        lote_matriculas = []
        for _ in range(cantidad_lote):
            # Elegimos un alumno y asignatura al azar entre 1 y el máximo
            id_asig_rand = random.randint(1, max_asignaturas)
            id_alum_rand = random.randint(1, max_alumnos)
            lote_matriculas.append((id_asig_rand, id_alum_rand))

        with open('temp_matriculas.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(lote_matriculas)

        end_time = time.perf_counter()
        tiempo_lote = end_time - start_time
        print(f"Tiempo de generación del lote {i}: { tiempo_lote }s") # VERBOSE

        tiempo_total += tiempo_lote
    
    print(f"Insertando datos a la base de datos con COPY...") # VERBOSE
    start_time = time.perf_counter()
    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            with open('temp_matriculas.csv', 'r', encoding='utf-8') as f:
                with cur.copy("COPY matriculas(asignatura_id, alumno_id) FROM STDIN WITH (FORMAT csv)") as copy:
                    while data := f.read(8192):
                        copy.write(data)
    end_time = time.perf_counter()
    tiempo_copy = end_time - start_time
    print(f"Tiempo de inserción COPY: { tiempo_copy }s") # VERBOSE
    tiempo_total += tiempo_copy
    
    if os.path.exists('temp_matriculas.csv'):
        os.remove('temp_matriculas.csv')

    print(f"Tiempo total de los { lotes } lotes: {tiempo_total:.4f}s") # VERBOSE
    return tiempo_total

if __name__ == "__main__":
    insert_alumnos()
    insert_profesores()
    insert_asignaturas()
    insert_matriculas()