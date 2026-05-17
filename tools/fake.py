from __future__ import annotations

from faker import Faker

import random

def demo_basics() -> None:
    # Locale = "idioma + reglas culturales" de los datos generados (nombres, direcciones, etc.)
    fake_en = Faker()            # default (en_US)
    fake_es = Faker("es_ES")     # español (España)

    # Semilla (seed) = hace el experimento reproducible: misma entrada -> misma salida
    Faker.seed(0)
    fake_en.seed_instance(0)
    fake_es.seed_instance(0)

    print("EN:", fake_en.name(), "-", fake_en.safe_email())
    print("ES:", fake_es.name(), "-", fake_es.safe_email())

def generate_rows(n: int = 10_000, locale: str = "es_ES", attrs: list = [], seed: int = 0, max_rand_number: int = 0, used_ids: list = [], array_insert: list = []) -> list[tuple[str, str]]:
    """Generate rows (name, email) without printing inside the loop.

    Generación por lotes = producir datos en memoria (o por chunks) para luego insertarlos en bloque.
    No imprimimos 10k/1M líneas: eso distorsiona tiempos y hace el experimento inútil.
    """
    Faker.seed(seed)
    fake = Faker(locale)
    fake.seed_instance(seed)

    rows: list[tuple[str, str]] = []
    for _ in range(n):
        row = []

        if max_rand_number > 0:
            rand = random.randint(1, max_rand_number)

            # Me aseguro de que el id no esté repetido
            while rand in used_ids:
                rand = random.randint(1, max_rand_number)
            
            row.append(rand)
            

        for attr in attrs:
            if hasattr(fake, attr):
                metodo = getattr(fake, attr)
                row.append(metodo())
        
        array_insert.append(tuple(row))
        
    return array_insert