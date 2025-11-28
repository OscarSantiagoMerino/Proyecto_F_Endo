import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Steam + Twitch Dashboard", layout="wide")

st.title("Steam + Twitch - Proyecto Final")
st.sidebar.success("Selecciona un análisis en el menú de la izquierda.")


@st.cache_data
def load_data():
    """Carga el `merged_data.csv` generado por el pipeline en `data/processed/`.

    Si el archivo no existe se muestra un error en la app y se devuelve
    un DataFrame vacío para evitar excepciones posteriores.
    """
    processed_path = os.path.join("data", "processed", "merged_data.csv")

    if not os.path.exists(processed_path):
        st.error(
            f"Archivo no encontrado: {processed_path}. Ejecuta el pipeline para generar `merged_data.csv`."
        )
        return pd.DataFrame()

    df = pd.read_csv(processed_path, encoding="latin1", low_memory=False)

    # Normalizar 'game' a minúsculas cuando exista
    if "game" in df.columns:
        df["game"] = df["game"].astype(str).str.lower()

    return df


df = load_data()
st.session_state["data"] = df

st.write("Datos cargados correctamente:", df.shape[0], "filas.")
