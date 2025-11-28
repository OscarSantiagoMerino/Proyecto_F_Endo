import streamlit as st
import pandas as pd
import plotly.express as px
import unidecode
from scipy.stats import spearmanr, kruskal

st.set_page_config(layout="wide")

st.title("Análisis Estadístico — Steam + Twitch")

# -----------------------------------------------------------
# CARGA DE DATOS + LIMPIEZA
# -----------------------------------------------------------
@st.cache_data
def load_data():

    df = pd.read_csv(
        r"C:\Users\kimbo\Downloads\merged_data.csv",
        low_memory=False,
        encoding="latin1"
    )

    # Normalizar game
    df["game"] = df["game"].astype(str).str.lower()

    # ------ FUNCIÓN MEJORADA PARA NORMALIZAR GÉNEROS ------
    def normalize_genre(g):
        if not isinstance(g, str):
            return "Desconocido"

        g_clean = unidecode.unidecode(g).lower().strip()

        # Diccionario extendido
        mapper = {
            # Acción
            "accion": "Acción",
            "accia3n": "Acción",
            "akcja": "Acción",
            "akana": "Acción",

            # Aventura
            "aventura": "Aventura",
            "abenteuer": "Aventura",
            "aventure": "Aventura",
            "przygodowe": "Aventura",

            # Casual
            "casual": "Casual",

            # RPG
            "rpg": "RPG",
            "rollenspiel": "RPG",

            # MMO
            "mmo": "MMO",

            # Indie
            "indie": "Indie",

            # Estrategia
            "estrategia": "Estrategia",

            # Simulación
            "simulacion": "Simulación",

            # Deportes
            "deportes": "Deportes",

            # Carreras
            "carreras": "Carreras",

            # Adultos
            "contenido adulto": "Contenido Adulto",

            # Acceso anticipado
            "acceso anticipado": "Acceso Anticipado",
            "early access": "Acceso Anticipado",
        }

        # Coincidencia por clave
        for key, value in mapper.items():
            if key in g_clean:
                return value

        # Si está corrupto (muchos símbolos raros)
        if any(char.isdigit() or char in "!*>/<" for char in g_clean):
            return "Desconocido"

        # Caso general
        return g_clean.capitalize()

    df["genre"] = df["genre"].apply(normalize_genre)

    # Convertir numéricos
    for col in [
        "hours_watched", "hours_streamed", "avg_viewers",
        "avg_channels", "peak_viewers", "price"
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# cargar
df = load_data()


# --------------------------------------------------
# FILTRADO DE GÉNERO
# --------------------------------------------------
st.sidebar.header("Filtros")

genres = sorted(df["genre"].dropna().unique())

selected_genres = st.sidebar.multiselect(
    "Selecciona géneros:",
    genres,
    default=[]
)

filtered_df = df if not selected_genres else df[df["genre"].isin(selected_genres)]

# ====================================================
# 1️ Correlación Spearman — Horas vistas vs Viewers
# ====================================================
st.subheader("1️ Correlación Spearman")

col1, col2 = st.columns(2)

corr, p = spearmanr(
    filtered_df["hours_watched"],
    filtered_df["avg_viewers"],
    nan_policy="omit"
)

col1.metric("Coeficiente Spearman", round(corr, 4))
col2.metric("P-value", f"{p:.6f}")

fig1 = px.scatter(
    filtered_df,
    x="hours_watched",
    y="avg_viewers",
    color="genre",
    hover_name="game",
    title="Horas vistas vs. Audiencia promedio"
)
st.plotly_chart(fig1, use_container_width=True)


# ====================================================
# 2️ Prueba Kruskal-Wallis por género
# ====================================================
st.subheader("2️ Prueba Kruskal-Wallis por género")

groups = [g["avg_viewers"].dropna() for _, g in filtered_df.groupby("genre")]

if len(groups) > 1:
    stat, pval = kruskal(*groups)

    st.write(f"**H-statistic:** {stat:.4f}")
    st.write(f"**P-value:** {pval:.6f}")
else:
    st.info("No hay suficientes géneros seleccionados para ejecutar Kruskal-Wallis.")

viewer_genre = (
    filtered_df.groupby("genre")["avg_viewers"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

fig2 = px.bar(
    viewer_genre,
    x="genre",
    y="avg_viewers",
    title="Audiencia promedio por género",
    labels={"genre": "Género", "avg_viewers": "Promedio Viewers"},
)

st.plotly_chart(fig2, use_container_width=True)
