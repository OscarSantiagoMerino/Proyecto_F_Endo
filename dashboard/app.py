import streamlit as st
import pandas as pd
import unidecode
import plotly.express as px

st.set_page_config(page_title="Steam + Twitch Dashboard", layout="wide")

st.title("Steam + Twitch – Dashboard Final")
st.sidebar.success("Selecciona un análisis o aplica filtros.")


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

    # Normalizar texto
    df["game"] = df["game"].astype(str).str.lower()

    # Normalizar género según tu lista final
    def normalize_genre(g):
        if not isinstance(g, str):
            return "Desconocido"

        g_clean = unidecode.unidecode(g).lower().strip()

        mapper = {
            "accion": "Acción",
            "akcji": "Acción",
            "casual": "Casual",
            "rpg": "RPG",
            "indie": "Indie",
            "mmo": "MMO",
            "avent": "Aventura",
            "przyg": "Aventura",
            "abente": "Aventura",
            "estrateg": "Estrategia",
            "sport": "Deportes",
            "simu": "Simulación",
            "race": "Carreras",
            "adult": "Contenido Adulto",
            "access": "Acceso Anticipado",
            "early": "Acceso Anticipado"
        }

        for key, value in mapper.items():
            if key in g_clean:
                return value

        return "Acción"

    df["genre"] = df["genre"].apply(normalize_genre)

    # columnas numéricas
    for col in [
        "hours_watched", "hours_streamed", "avg_viewers",
        "avg_channels", "peak_viewers", "price"
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()


# -----------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------
st.sidebar.header("Filtros")

genres = sorted(df["genre"].dropna().unique())
selected = st.sidebar.multiselect("Filtrar por género", genres)

df_filtered = df[df["genre"].isin(selected)] if selected else df.copy()


# -----------------------------------------------------------
# KPIs
# -----------------------------------------------------------
st.subheader("Indicadores generales")

col1, col2, col3 = st.columns(3)

col1.metric("Juegos Totales", len(df_filtered))
col2.metric("Horas vistas promedio", f"{df_filtered['hours_watched'].mean():,.0f}")
col3.metric("Precio promedio", f"${df_filtered['price'].mean():.2f}")


# -----------------------------------------------------------
# GRÁFICO 1
# -----------------------------------------------------------
st.subheader("Horas vistas por género")

df_genre = (
    df_filtered.groupby("genre")["hours_watched"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig = px.bar(
    df_genre,
    x="genre",
    y="hours_watched",
)

st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------
# TOP 10
# -----------------------------------------------------------
st.subheader("Top 10 juegos más vistos")

st.dataframe(
    df_filtered[["name", "genre", "hours_watched", "avg_viewers", "price"]]
    .sort_values("hours_watched", ascending=False)
    .head(10)
)

st.success("Dashboard generado correctamente")
