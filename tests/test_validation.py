import sys
import os
import pandas as pd

# Asegurar que pytest encuentre el módulo
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.data_validation import validate_data



def test_validate_data_ok():
    df = pd.DataFrame({
        "name": ["Halo", "Minecraft"],
        "genres": ["Action", "Adventure"],
        "price": [30, 20]
    })
    
    errors = validate_data(df)
    assert len(errors) == 0


def test_validate_data_missing_columns():
    df = pd.DataFrame({
        "name": ["Halo"],
        # Falta "genres"
        "price": [30]
    })

    errors = validate_data(df)
    assert "Falta la columna requerida: genres" in errors


def test_validate_data_empty_values():
    df = pd.DataFrame({
        "name": ["Halo", None],
        "genres": ["Action", "Adventure"],
        "price": [30, 20]
    })

    errors = validate_data(df)
    assert "Valores vacíos encontrados" in errors[0]
