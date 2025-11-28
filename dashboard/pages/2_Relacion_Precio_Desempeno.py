import os
import ast
import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
import unidecode

st.title("Dashboard — Precio, Desempeño y Endorsers")

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
            "Aassapso": "Acceso Anticipado",
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




# -----------------------------------------------------------
# EXTRAER PRICES CORRECTAMENTE
# -----------------------------------------------------------
def extract_price_fields(row):
    try:
        d = row if isinstance(row, dict) else ast.literal_eval(str(row))
        return pd.Series([
            d.get("final", None),
            d.get("initial", None),
            d.get("discount_percent", None),
            d.get("currency", None),
        ])
    except:
        return pd.Series([None, None, None, None])

if "price_overview" in df.columns:
    df[["price_final", "price_initial", "discount_percent", "currency"]] = \
        df["price_overview"].apply(extract_price_fields)

    df["price"] = pd.to_numeric(df["price_final"], errors="coerce")
    df["sale_spike"] = pd.to_numeric(df["discount_percent"], errors="coerce")
else:
    df["price"] = None
    df["sale_spike"] = None

# -----------------------------------------------------------
# FILTROS
# -----------------------------------------------------------
st.sidebar.header("Filtros")

genres = sorted(df["genre"].dropna().unique())
selected = st.sidebar.multiselect("Filtrar por género", genres)

if selected:
    df = df[df["genre"].isin(selected)]

# -----------------------------------------------------------
# 1. PRECIO VS VIEWERS
# -----------------------------------------------------------
st.subheader("Relación entre precio y viewers promedio")

fig = px.scatter(
    df,
    x="price",
    y="avg_viewers",
    color="genre",
    title="Precio vs Viewers",
)
st.plotly_chart(fig, use_container_width=True)



# -----------------------------------------------------------
# 3. GÉNEROS MÁS POPULARES
# -----------------------------------------------------------
st.subheader("Géneros con mayor proporción de juegos populares")

df["popular"] = df["avg_viewers"] > df["avg_viewers"].median()

rate = (
    df.groupby("genre")["popular"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

fig2 = px.bar(
    rate,
    x="genre",
    y="popular",
    title="Proporción de juegos populares por género (ordenado)",
)

# Forzar orden exacto en el eje:
fig2.update_xaxes(categoryorder="array", categoryarray=rate["genre"])

st.plotly_chart(fig2, use_container_width=True)


# -----------------------------------------------------------
# 4. ENDORSERS VS SPIKES
# -----------------------------------------------------------
st.subheader("Endorsers vs Spikes en Ventas")

endorser_option = st.selectbox("Indicador de endorsement", ["streamers", "avg_channels"])

sub2 = df.dropna(subset=[endorser_option, "sale_spike"])

fig3 = px.scatter(
    sub2,
    x=endorser_option,
    y="sale_spike",
    trendline="ols",
    color="genre",
    title=f"{endorser_option} vs Spike de Ventas"
)
st.plotly_chart(fig3, use_container_width=True)

st.success("Dashboard generado correctamente.")
