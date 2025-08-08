import pandas as pd

# 1. Ler o arquivo original no formato que ele está
df = pd.read_csv(
    "data/preds/pred_morb_circ.csv",
    sep=";",       # separador de colunas original
    decimal=",",   # separador decimal original
    encoding="utf-8"  # ou "latin-1" se der erro
)

# 2. Salvar no formato padronizado (vírgula separador, ponto decimal)
df.to_csv(
    "data/preds/pred_morb_circ2.csv",
    sep=",",       # separador de colunas novo
    decimal=".",   # separador decimal novo
    index=False
)
