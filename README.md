#  Proyecto Steam — Pipeline de Análisis Steam + Twitch

##  Resumen
Este proyecto implementa un **pipeline de datos end-to-end** para correlacionar métricas de juegos de Steam  
(metadatos, precios, etc.) con métricas sociales extraídas de Twitch (horas vistas, promedio de espectadores, etc.).

El objetivo es analizar qué factores están asociados al rendimiento y popularidad de los videojuegos en ambas plataformas.

##  Estructura del repositorio

Proyecto_Steam/
├─ config/              # Configuración del pipeline
│  └─ pipeline_config.yaml
├─ data/
│  ├─ raw/              # Datos originales (CSV) – gestionados con Git LFS
│  └─ processed/        # Salidas del pipeline (merge, análisis, reportes)
├─ src/
│  ├─ data_ingestion.py       # Carga de datos
│  ├─ data_transformation.py  # Limpieza y transformación
│  ├─ data_validation.py      # Validaciones de consistencia
│  ├─ analysis.py             # Análisis estadísticos (Spearman, Kruskal-Wallis)
│  └─ orchestrator.py         # Ejecuta el pipeline completo
├─ tests/               # Pruebas unitarias
└─ requirements.txt

##  Requisitos

- Python **3.10+**
- Paquetes incluidos en `requirements.txt`
- **Git LFS** para manejar los CSV grandes

## 🛠 Instalación local (Windows PowerShell)

### 1. Crear entorno virtual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. (Opcional) Instalar Git LFS
```powershell
git lfs install
```

##  Datos grandes (Git LFS)

Los archivos ubicados en `data/raw/` se manejan con Git LFS.  
Clonado recomendado:

```powershell
git lfs install
git clone https://github.com/OscarSantiagoMerino/Proyecto_Steam.git
cd Proyecto_Steam
git lfs pull
```

Si no deseas usar LFS, el pipeline puede configurarse para leer los datos desde almacenamiento externo.

##  Ejecutar el pipeline

Con los datos en `data/raw/`, correr:

```powershell
python src/orchestrator.py
```

Esto ejecuta:
- Ingesta de datos  
- Transformación  
- Validación  
- Análisis estadístico  

Los resultados quedan en `data/processed/`.

##  Tests

```powershell
pytest -q
```

o:

```powershell
python run_tests_custom.py
```

##  CI/CD (GitHub Actions)

El workflow ubicado en:

```
.github/workflows/ci.yaml
```

realiza:

- Checkout con soporte LFS
- Instalación del entorno
- Ejecución del pipeline y tests
- Publicación de artefactos (logs, resultados)

##  Recomendaciones

- Monitorea tu cuota de LFS (GitHub → Billing).
- Si no deseas almacenar CSV pesados, puedes:
  - Usar Azure Blob, AWS S3 o GitHub Releases
  - Descargar los datos en CI desde una URL segura
- Si necesitas:
  - `requirements-dev.txt`
  - formateo/lint (Black, Ruff)
  - despliegue automático

puedo ayudarte a configurarlo.

##  Contacto

mantenido por **OscarSantiagoMerino**.
