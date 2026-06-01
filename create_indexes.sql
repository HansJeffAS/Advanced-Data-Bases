CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Índices de tablas normales
CREATE INDEX IF NOT EXISTS idx_alumnos_saldo
    ON alumnos(saldo);

CREATE INDEX IF NOT EXISTS idx_asignaturas_profesor_id
    ON asignaturas(profesor_id);

CREATE INDEX IF NOT EXISTS idx_asignaturas_precio
    ON asignaturas(precio);

CREATE INDEX IF NOT EXISTS idx_asignaturas_max_alumnos
    ON asignaturas(max_alumnos);

CREATE INDEX IF NOT EXISTS idx_matriculas_alumno_id
    ON matriculas(alumno_id);

CREATE INDEX IF NOT EXISTS idx_matriculas_asignatura_id
    ON matriculas(asignatura_id);

CREATE INDEX IF NOT EXISTS idx_matriculas_fecha_matricula
    ON matriculas(fecha_matricula);

-- Índices de tablas de auditoria
CREATE INDEX IF NOT EXISTS idx_alumnos_audit_stamp
    ON alumnos_audit(stamp);

CREATE INDEX IF NOT EXISTS idx_profesores_audit_stamp
    ON profesores_audit(stamp);

CREATE INDEX IF NOT EXISTS idx_asignaturas_audit_stamp
    ON asignaturas_audit(stamp);

CREATE INDEX IF NOT EXISTS idx_alumnos_audit_operation
    ON alumnos_audit(operation);

CREATE INDEX IF NOT EXISTS idx_profesores_audit_operation
    ON profesores_audit(operation);

CREATE INDEX IF NOT EXISTS idx_asignaturas_audit_operation
    ON asignaturas_audit(operation);

-- Índices GIN en tablas normales
CREATE INDEX IF NOT EXISTS idx_gin_alumnos_nombre
    ON alumnos USING GIN(nombre gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_gin_alumnos_email
    ON alumnos USING GIN(email_alumno gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_gin_profesores_nombre
    ON profesores USING GIN(nombre gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_gin_profesores_email
    ON profesores USING GIN(email_profesor gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_gin_asignaturas_nombre
    ON asignaturas USING GIN(nombre gin_trgm_ops);

-- Índices GIN en tablas de auditoria
CREATE INDEX IF NOT EXISTS idx_gin_alumnos_audit_nombre
    ON alumnos_audit USING GIN(nombre gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_gin_alumnos_audit_email
    ON alumnos_audit USING GIN(email_alumno gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_gin_profesores_audit_nombre
    ON profesores_audit USING GIN(nombre gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_gin_profesores_audit_email
    ON profesores_audit USING GIN(email_profesor gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_gin_asignaturas_audit_nombre
    ON asignaturas_audit USING GIN(nombre gin_trgm_ops);
