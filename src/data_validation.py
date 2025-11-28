import pandas as pd


def validate_data(df: pd.DataFrame):
    """Valida un DataFrame y devuelve una lista de errores.

    Reglas aplicadas:
    - Comprobar columnas requeridas: `name`, `genres`, `price`.
    - Detectar valores vacíos en las columnas requeridas.
    - Detección de duplicados por `name` (si existe).
    - Comprobación de rangos simples para `price` (>=0) cuando exista.

    Retorna:
        errors (list): lista de mensajes de error vacía si no hay errores.
    """
    errors = []

    required_cols = ["name", "genres", "price"]

    # 1) Columnas requeridas
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Falta la columna requerida: {col}")

    # Si faltan columnas, retornamos errores encontrados hasta ahora
    if errors:
        return errors

    # 2) Valores vacíos
    if df[required_cols].isnull().any(axis=None):
        errors.append("Valores vacíos encontrados")

    # 3) Duplicados por nombre
    if "name" in df.columns and df["name"].duplicated().sum() > 0:
        errors.append("Hay juegos duplicados en la columna 'name'.")

    # 4) Rangos
    if "price" in df.columns:
        try:
            invalid_prices = (pd.to_numeric(df["price"], errors="coerce") < 0).sum()
            if invalid_prices > 0:
                errors.append("Existen precios negativos (inválido).")
        except Exception:
            errors.append("No se pudo validar la columna 'price'.")

    return errors


if __name__ == "__main__":
    df = pd.read_csv("data/processed/merged_data.csv")
    errs = validate_data(df)
    if errs:
        print("Validación fallida:")
        for e in errs:
            print(" -", e)
    else:
        print("✔ Validación exitosa")
