import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import unidecode

st.title("Tendencias de Desarrollo")

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

    # Normalizar género
    def normalize_genre(g):
        if not isinstance(g, str):
            return "Desconocido"

        g_clean = unidecode.unidecode(g).lower().strip()

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

        for key, value in mapper.items():
            if key in g_clean:
                return value

        return g_clean.capitalize()

    df["genre"] = df["genre"].apply(normalize_genre)

    # Variables numéricas a número
    numeric_cols = [
        "hours_watched", "hours_streamed", "avg_viewers",
        "avg_channels", "peak_viewers", "price"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# cargar
df = load_data()

# --------------------------------------------------
# FILTROS
# --------------------------------------------------
st.sidebar.header("Filtros")

genres = sorted(df["genre"].dropna().unique())

selected_genres = st.sidebar.multiselect(
    "Selecciona géneros:",
    genres,
    default=[]
)

filtered_df = df if not selected_genres else df[df["genre"].isin(selected_genres)]

# =========================
# Helper para cluster
# =========================
def cluster_plot(data, title):
    scaler = StandardScaler()
    X = scaler.fit_transform(data)

    fig = px.scatter(
        data,
        x="hours_watched",
        y="avg_viewers",
        color=data["cluster"],
        labels={
            "hours_watched": "Horas vistas",
            "avg_viewers": "Viewers promedio",
            "cluster": "Cluster"
        },
        title=title,
    )
    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# K-MEANS
# --------------------------------------------------
st.subheader("K-means clustering basado en viewers y horas vistas")

data = filtered_df[["hours_watched", "avg_viewers"]].dropna().copy()

if len(data) < 20:
    st.warning("No hay suficientes datos para clustering.")
else:
    X = StandardScaler().fit_transform(data)

    kmeans = KMeans(n_clusters=4, n_init="auto").fit(X)
    data["cluster"] = kmeans.labels_

    cluster_plot(data, "Distribución K-Means")


