# Consolidación y visualización de datos de marketing y ventas de un centro de psicología online

Trabajo final del curso **Herramientas para Inteligencia Artificial** (Maestría en IA Aplicada, UCSM–UTPL).

El notebook integra dos datasets, uno en **CSV** y otro en una **base de datos SQLite**, los limpia, los une y los visualiza con **Matplotlib**, **Bokeh** y **PyGWalker**:

- **CSV, datos reales:** exports de Google Search Console, Google Analytics 4 y Meta (Facebook e Instagram) de un centro de psicología online. Son datos agregados, sin información de personas.
- **SQLite, datos sintéticos:** ventas (pacientes y sesiones) generadas con `generar_datos.py`. Las ventas reales contienen datos de pacientes y no se publican.

📄 **El informe completo está en la [Wiki](../../wiki) del repositorio.**

## Contenido

| Archivo / carpeta | Qué es |
|---|---|
| `datos/inicial/*.csv` | **Dataset inicial 1 (CSV):** 5 exports reales (795 filas) |
| `datos/ventas.db` | **Dataset inicial 2 (SQLite):** tablas `canales`, `pacientes` y `sesiones` |
| `sql/01_crear_tablas.sql` | Crea las tres tablas |
| `sql/02_insertar_datos.sql` | Inserta los datos |
| `sql/03_consultas.sql` | Consultas con `JOIN` entre las tablas |
| `generar_datos.py` | Genera las ventas sintéticas, escribe los `.sql` y crea la base de datos |
| `trabajo_final.ipynb` | **Notebook con todos los pasos** |
| `datos/final/consolidado_diario.csv` | **Dataset final:** una fila por día con todas las fuentes |
| `datos/final/consolidado_por_canal.csv` | **Dataset final:** visitas, pacientes e ingresos por canal |
| `graficos/` | Visualizaciones exportadas (PNG y HTML interactivos) |

## Cómo replicarlo

Requisitos: **Python 3.11 o superior**.

```bash
# 1. Clonar el repositorio
git clone <URL-de-este-repo>
cd <carpeta-del-repo>

# 2. Crear y activar un entorno virtual
python -m venv env
env\Scripts\activate          # Windows
# source env/bin/activate     # macOS / Linux

# 3. Instalar las librerías
pip install -r requirements.txt

# 4. (Opcional) Volver a crear la base de datos desde cero
python generar_datos.py

# 5. Abrir el notebook
jupyter lab trabajo_final.ipynb
```

En JupyterLab: **Run → Run All Cells**. El notebook lee `datos/`, ejecuta `sql/03_consultas.sql`, guarda los gráficos en `graficos/` y escribe el dataset final en `datos/final/`.

También funciona en **Google Colab**: clonar con `!git clone <URL>`, instalar con `!pip install -r requirements.txt` y ejecutar todas las celdas.

> El explorador de **PyGWalker** solo se ve al ejecutar el notebook; la vista previa de GitHub no lo muestra.
