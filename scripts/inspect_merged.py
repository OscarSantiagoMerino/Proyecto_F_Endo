import pandas as pd
import os


def main(path="data/processed/merged_data.csv", n=10):
    if not os.path.exists(path):
        print("No se encontró:", path)
        return

    df = pd.read_csv(path)
    print("Filas totales:", len(df))
    print("Columnas:", list(df.columns))

    # Nulls per column
    print('\nNulos por columna:')
    print(df.isna().sum())

    # Revisar columnas críticas
    req = ['name', 'genres', 'price']
    print('\nNulos en columnas requeridas:')
    for c in req:
        if c in df.columns:
            print(f" - {c}: {df[c].isna().sum()}")
        else:
            print(f" - {c}: (no existe)")

    # Mostrar ejemplos de filas con nulos en columnas requeridas
    mask = False
    for c in req:
        if c in df.columns:
            mask = mask | df[c].isna()

    if mask.any():
        print('\nEjemplos de filas con valores vacíos en columnas requeridas:')
        print(df[mask].head(10))

    # Duplicados por 'name' si existe
    if 'name' in df.columns:
        dup_count = df['name'].duplicated().sum()
        print(f"\nDuplicados en 'name': {dup_count}")
        if dup_count > 0:
            print('\nPrimeras filas duplicadas:')
            dup_names = df['name'][df['name'].duplicated()].unique()[:n]
            for nm in dup_names:
                print('---', nm)
                print(df[df['name'] == nm].head())
    else:
        print("No existe la columna 'name' en el dataset final.")


if __name__ == '__main__':
    main()
