import os
import yaml
from data_ingestion import ingest_data
from data_transformation import transform_data
from data_validation import validate_data
from analysis import run_analysis


def run_pipeline(config_path: str = "config/pipeline_config.yaml"):
    print("Iniciando pipeline Steam + Twitch...")

    # Leer configuración
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
    else:
        cfg = {}

    paths = cfg.get("paths", {})
    raw_dir = paths.get("raw_data", "data/raw/")
    processed_dir = paths.get("processed_data", "data/processed/")
    files = cfg.get("files", {})

    steam_file = os.path.join(raw_dir, files.get("steam_dataset", "steam_app_data.csv"))
    twitch_file = os.path.join(raw_dir, files.get("twitch_dataset", "Twitch_game_data.csv"))

    # 1. INGESTA
    steam_df, twitch_df = ingest_data(steam_file, twitch_file, config_path=config_path)

    # 2. TRANSFORMACIÓN
    merged_df = transform_data(steam_df, twitch_df, config_path=config_path,
                               output_dir=processed_dir)

    # 3. VALIDACIÓN
    errors = validate_data(merged_df)
    if errors:
        print("Pipeline detenido por errores de validación:")
        for e in errors:
            print(" -", e)
        return

    # 4. ANÁLISIS
    run_analysis(merged_df, config_path=config_path)

    print("Pipeline completado con éxito.")


if __name__ == "__main__":
    run_pipeline()
