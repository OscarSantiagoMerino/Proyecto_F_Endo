import os
import yaml
import pandas as pd
from scipy.stats import spearmanr, kruskal


def run_analysis(df: pd.DataFrame, output: str = None,
                 config_path: str = "config/pipeline_config.yaml"):
    """Corre los análisis definidos en la configuración y guarda resultados.
    """
    # Leer config si existe
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
    else:
        cfg = {}

    output = output or cfg.get("paths", {}).get("processed_data",
                                             "data/processed/")
    os.makedirs(output, exist_ok=True)
    out_file = os.path.join(output, "analysis_results.csv")

    # 1. Spearman correlation
    corr, p_spearman = spearmanr(df["hours_watched"], df["avg_viewers"],
                                 nan_policy="omit")

    # 2. Kruskal-Wallis (por género) si hay al menos 2 grupos
    groups = [g["avg_viewers"].dropna() for _, g in df.groupby("genre")]
    if len([g for g in groups if len(g) > 0]) >= 2:
        stat, p_kruskal = kruskal(*groups)
    else:
        stat, p_kruskal = None, None

    result = pd.DataFrame({
        "spearman_corr": [corr],
        "spearman_p": [p_spearman],
        "kruskal_stat": [stat],
        "kruskal_p": [p_kruskal]
    })

    result.to_csv(out_file, index=False)
    print("✔ Análisis completado. Guardado en:", out_file)

    return result


if __name__ == "__main__":
    df = pd.read_csv("data/processed/merged_data.csv")
    run_analysis(df)
