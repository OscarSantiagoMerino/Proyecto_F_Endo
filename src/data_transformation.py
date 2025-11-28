import os
import json
import yaml
import pandas as pd
import unidecode


def extract_genre(x):
    try:
        obj = json.loads(x.replace("'", '"'))
        return obj[0]["description"]
    except:
        return None


def normalize_genre(g):
    if not isinstance(g, str):
        return "Desconocido"

    g_clean = unidecode.unidecode(g).lower().strip()

    mapper = {
        "action": "Acción",
        "adventure": "Aventura",
        "casual": "Casual",
        "simulation": "Simulación",
        "sport": "Deportes",
        "rpg": "RPG",
        "strategy": "Estrategia",
        "indie": "Indie",
        "racing": "Carreras",
        "multiplayer": "MMO",
        "massively": "MMO",
        "free to play": "Free To Play",
        "sexual": "Contenido Adulto",
        "early access": "Acceso Anticipado",
    }

    for key, value in mapper.items():
        if key in g_clean:
            return value

    return g_clean.capitalize()


def extract_price(val):
    try:
        return float(val.split("'final': ")[1].split(",")[0]) / 100
    except:
        return None


def transform_data(steam_df, twitch_df, config_path: str = "config/pipeline_config.yaml",
                   output_dir: str = None):
    """Transforma y normaliza los datasets de Steam y Twitch.

    Si `output_dir` no está provisto, se lee desde la configuración.
    """
    # Leer config si existe
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
    else:
        cfg = {}

    processed_dir = output_dir or cfg.get("paths", {}).get("processed_data", "data/processed/")
    os.makedirs(processed_dir, exist_ok=True)

    # ---- Steam ----
    if "genres" in steam_df.columns:
        steam_df["genre"] = steam_df["genres"].apply(extract_genre)
        steam_df["genre"] = steam_df["genre"].apply(normalize_genre)
    else:
        steam_df["genre"] = None

    if "name" in steam_df.columns:
        steam_df["game"] = steam_df["name"].astype(str).str.lower()
    else:
        steam_df["game"] = None

    if "price_overview" in steam_df.columns:
        steam_df["price"] = steam_df["price_overview"].apply(extract_price)
    else:
        steam_df["price"] = None

    # Rellenar 'genres' con la columna normalizada 'genre' cuando falte
    if "genres" in steam_df.columns:
        steam_df["genres"] = steam_df["genres"].fillna(steam_df["genre"])

    # Si el juego es gratuito y no tenemos precio, asignar 0
    if "is_free" in steam_df.columns:
        try:
            steam_df.loc[steam_df["is_free"] == True, "price"] = \
                steam_df.loc[steam_df["is_free"] == True, "price"].fillna(0)
        except Exception:
            pass

    # Eliminar filas que sigan sin 'price' o sin 'genres'
    critical_cols = [c for c in ["price", "genres"] if c in steam_df.columns]
    if critical_cols:
        steam_df = steam_df.dropna(subset=critical_cols).copy()

    # ---- Twitch ----
    twitch_df.columns = twitch_df.columns.str.lower()
    if "game" in twitch_df.columns:
        twitch_df["game"] = twitch_df["game"].astype(str).str.lower()
    else:
        twitch_df["game"] = None

    for col in ["hours_watched", "avg_viewers"]:
        if col in twitch_df.columns:
            twitch_df[col] = pd.to_numeric(twitch_df[col], errors="coerce")
        else:
            twitch_df[col] = None

    # ---- LIMPIEZA: eliminar filas sin nombre/juego ----
    if "name" in steam_df.columns:
        steam_df = steam_df[steam_df["name"].notna()].copy()
    if "game" in twitch_df.columns:
        twitch_df = twitch_df[twitch_df["game"].notna()].copy()

    # ---- AGREGAR (Twitch): resumir métricas por 'game' para evitar duplicados ----
    agg_funcs = {
        "hours_watched": "sum",
        "hours_streamed": "sum",
        "peak_viewers": "max",
        "peak_channels": "max",
        "streamers": "sum",
        "avg_viewers": "mean",
        "avg_channels": "mean",
        "avg_viewer_ratio": "mean"
    }

    # Mantener sólo las columnas que existen
    existing_aggs = {k: v for k, v in agg_funcs.items() if k in twitch_df.columns}
    if existing_aggs:
        twitch_agg = twitch_df.groupby("game").agg(existing_aggs).reset_index()
    else:
        twitch_agg = twitch_df.drop_duplicates(subset=["game"]).copy()

    # ---- DEDUPLICAR Steam: si hay múltiples filas por juego (por ejemplo por mes/año),
    # mantener la fila más reciente si existen 'year'/'month', sino mantener la primera.
    if "year" in steam_df.columns and "month" in steam_df.columns:
        steam_df = steam_df.sort_values(["year", "month"], ascending=[False, False])
        steam_df = steam_df.drop_duplicates(subset=["game"], keep="first").copy()
    else:
        steam_df = steam_df.drop_duplicates(subset=["game"], keep="first").copy()

    # ---- MERGE ----
    merged = pd.merge(steam_df, twitch_agg, on="game", how="inner")

    merged.to_csv(os.path.join(processed_dir, "merged_data.csv"), index=False)

    print("✔ Transformación completada. Guardado en:", processed_dir)
    return merged


if __name__ == "__main__":
    df1 = pd.read_csv("data/raw/steam_raw.csv")
    df2 = pd.read_csv("data/raw/twitch_raw.csv")
    transform_data(df1, df2)
