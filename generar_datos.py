"""Crea la base de datos SQLite de ventas (sintética) del trabajo final.

Los datos de marketing son REALES y ya vienen en datos/inicial/ (exports de Google Search Console,
Google Analytics 4 y Meta). Las ventas no se pueden publicar porque contienen datos de pacientes,
así que este script las SIMULA:

- Escenario: un centro de psicología online entre el 03-feb-2026 y el 13-nov-2026
  (el mismo periodo que los datos reales de Search Console).
- Los pacientes que llegan por Google siguen el ritmo de los clics reales de cada día, y los que llegan
  por Instagram o Facebook aumentan los días después de una publicación real. El resto de canales llega
  con un ritmo constante.
- Cada paciente compra un plan y asiste a sesiones semanales.

Escribe sql/01_crear_tablas.sql y sql/02_insertar_datos.sql y los ejecuta para crear datos/ventas.db.

Uso:  python generar_datos.py
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).parent
INICIAL = RAIZ / "datos" / "inicial"
gen = np.random.default_rng(2026)  # semilla fija: siempre salen los mismos datos

INICIO, FIN = pd.Timestamp("2026-02-03"), pd.Timestamp("2026-11-13")
dias = pd.date_range(INICIO, FIN, freq="D")

# id, nombre, tipo, pacientes nuevos promedio por día
CANALES = [
    (1, "Google", "Buscador", 0.45),
    (2, "Asistente de IA", "ChatGPT y similares", 0.35),
    (3, "Instagram", "Red social", 0.30),
    (4, "Facebook", "Red social", 0.15),
    (5, "Recomendación", "Boca a boca", 0.90),
    (6, "Directo", "WhatsApp o web directa", 0.55),
]
# plan: (probabilidad, precio por sesión, sesiones mín, sesiones máx)
PLANES = {
    "Consulta suelta": (0.30, 120, 1, 2),
    "Paquete 4 sesiones": (0.25, 110, 4, 4),
    "Paquete 8 sesiones": (0.25, 100, 8, 8),
    "Terapia continua": (0.20, 100, 10, 30),
}

# ---------- 1. Ritmo diario de llegada por canal (usa los datos reales) ----------
clics = (pd.read_csv(INICIAL / "gsc_rendimiento_diario.csv", parse_dates=["Fecha"])
         .set_index("Fecha")["Clics"].reindex(dias, fill_value=0))


def dias_de_publicacion(archivo):
    fechas = pd.to_datetime(pd.read_csv(archivo)["Hora de publicación"], format="%m/%d/%Y %H:%M").dt.normalize()
    efecto = pd.Series(0.0, index=dias)
    for f in fechas:  # cada publicación sube la llegada durante 3 días
        efecto[(efecto.index >= f) & (efecto.index < f + pd.Timedelta(days=3))] += 1
    return efecto


ig = dias_de_publicacion(INICIAL / "meta_instagram.csv")
fb = dias_de_publicacion(INICIAL / "meta_facebook.csv")

ritmo = {
    "Google": 0.45 * (0.3 + 0.7 * clics / clics.mean()),
    "Instagram": 0.30 * (0.6 + 0.8 * ig),
    "Facebook": 0.15 * (0.6 + 0.8 * fb),
}

# ---------- 2. Pacientes ----------
filas = []
for _, nombre, _, base in CANALES:
    lam = ritmo.get(nombre, pd.Series(base, index=dias))
    llegadas = gen.poisson(1.15 * lam.values)  # 1.15: escala del escenario simulado
    for dia, n in zip(dias, llegadas):
        filas += [(dia, nombre)] * int(n)

pacientes = pd.DataFrame(filas, columns=["fecha_primera_sesion", "canal"]).sort_values("fecha_primera_sesion")
pacientes = pacientes.reset_index(drop=True)
pacientes.insert(0, "id_paciente", [f"P{i:04d}" for i in range(1, len(pacientes) + 1)])
id_canal = {c[1]: c[0] for c in CANALES}
pacientes["id_canal"] = pacientes["canal"].map(id_canal)

nombres_plan = list(PLANES)
prob = np.array([PLANES[p][0] for p in nombres_plan])
prob_ia = np.array([0.15, 0.25, 0.35, 0.25])  # quienes llegan por IA compran más paquetes
pacientes["plan"] = [gen.choice(nombres_plan, p=prob_ia if c == "Asistente de IA" else prob) for c in pacientes["canal"]]
pacientes["tipo_terapia"] = gen.choice(["Individual", "Pareja", "Familiar", "Infantil"], len(pacientes), p=[0.62, 0.22, 0.08, 0.08])

# ---------- 3. Sesiones (una fila por sesión atendida) ----------
sesiones = []
for p in pacientes.itertuples():
    _, precio, smin, smax = PLANES[p.plan]
    n = int(gen.integers(smin, smax + 1))
    for k in range(n):
        fecha = p.fecha_primera_sesion + pd.Timedelta(days=7 * k + int(gen.integers(0, 3)))
        if fecha > FIN:
            break
        sesiones.append((p.id_paciente, fecha.strftime("%Y-%m-%d"), precio))
sesiones = pd.DataFrame(sesiones, columns=["id_paciente", "fecha", "monto"])
sesiones.insert(0, "id_sesion", [f"S{i:05d}" for i in range(1, len(sesiones) + 1)])
pacientes["fecha_primera_sesion"] = pacientes["fecha_primera_sesion"].dt.strftime("%Y-%m-%d")

# ---------- 4. Escribir los .sql y crear la base de datos ----------
crear = """-- Base de datos de ventas (sintética) de un centro de psicología online · SQLite
DROP TABLE IF EXISTS sesiones;
DROP TABLE IF EXISTS pacientes;
DROP TABLE IF EXISTS canales;

CREATE TABLE canales (
    id_canal INTEGER PRIMARY KEY,
    nombre   TEXT NOT NULL UNIQUE,
    tipo     TEXT NOT NULL
);

CREATE TABLE pacientes (
    id_paciente          TEXT PRIMARY KEY,
    id_canal             INTEGER NOT NULL REFERENCES canales(id_canal),
    fecha_primera_sesion TEXT NOT NULL,
    plan                 TEXT NOT NULL,
    tipo_terapia         TEXT NOT NULL
);

CREATE TABLE sesiones (
    id_sesion   TEXT PRIMARY KEY,
    id_paciente TEXT NOT NULL REFERENCES pacientes(id_paciente),
    fecha       TEXT NOT NULL,
    monto       REAL NOT NULL CHECK (monto > 0)
);
"""


def valor_sql(v):
    return str(v) if isinstance(v, (int, float, np.integer, np.floating)) else "'" + str(v).replace("'", "''") + "'"


def inserts(tabla, df):
    return [f"INSERT INTO {tabla} VALUES (" + ", ".join(valor_sql(v) for v in fila) + ");" for fila in df.itertuples(index=False)]


lineas = ["-- Inserta los datos sintéticos en las tres tablas", "BEGIN TRANSACTION;", ""]
lineas += [f"INSERT INTO canales VALUES ({i}, {valor_sql(n)}, {valor_sql(t)});" for i, n, t, _ in CANALES]
lineas += [""] + inserts("pacientes", pacientes[["id_paciente", "id_canal", "fecha_primera_sesion", "plan", "tipo_terapia"]])
lineas += [""] + inserts("sesiones", sesiones) + ["", "COMMIT;", ""]
insertar = "\n".join(lineas)

(RAIZ / "sql").mkdir(exist_ok=True)
(RAIZ / "sql" / "01_crear_tablas.sql").write_text(crear, encoding="utf-8", newline="\n")
(RAIZ / "sql" / "02_insertar_datos.sql").write_text(insertar, encoding="utf-8", newline="\n")

(RAIZ / "datos" / "mentiva.db").unlink(missing_ok=True)  # base anterior, ya no se usa
db = RAIZ / "datos" / "ventas.db"
db.unlink(missing_ok=True)
with sqlite3.connect(db) as con:
    con.executescript(crear)
    con.executescript(insertar)
    conteo = [con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("canales", "pacientes", "sesiones")]

print(f"Base de datos datos/ventas.db: {conteo[0]} canales, {conteo[1]} pacientes, {conteo[2]} sesiones")
print(f"Ingresos simulados: S/ {sesiones['monto'].sum():,.0f}")
