import os
import yaml
import pandas as pd


def ingest_data(steam_path: str = None, twitch_path: str = None,
                config_path: str = "config/pipeline_config.yaml",
                output_dir: str = None):
    """Ingesta de datos desde CSV. Si no se proveen rutas, las lee desde
    `config/pipeline_config.yaml`.

    Guarda copias en la carpeta de `raw_data` configurada.
    """
    # Cargar configuración
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
    else:
        cfg = {}

    raw_dir = cfg.get("paths", {}).get("raw_data", "data/raw/")
    files = cfg.get("files", {})

    # Determinar rutas finales
    steam_file = steam_path or os.path.join(raw_dir, files.get("steam_dataset", "steam_app_data.csv"))
    twitch_file = twitch_path or os.path.join(raw_dir, files.get("twitch_dataset", "Twitch_game_data.csv"))

    # Normalizar directorio de salida
    output_dir = output_dir or raw_dir
    os.makedirs(output_dir, exist_ok=True)

    # Leer CSVs
    steam_df = pd.read_csv(steam_file, encoding="latin1", low_memory=False)
    twitch_df = pd.read_csv(twitch_file, encoding="latin1", low_memory=False)

    # Guardar copias procesadas de raw
    steam_df.to_csv(os.path.join(output_dir, "steam_raw.csv"), index=False)
    twitch_df.to_csv(os.path.join(output_dir, "twitch_raw.csv"), index=False)

    print("✔ Ingesta completada. Archivos guardados en:", output_dir)
    return steam_df, twitch_df


if __name__ == "__main__":
    ingest_data()
