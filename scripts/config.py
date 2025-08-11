import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "dados" / "raw"
TRUSTED_DIR = BASE_DIR / "dados" / "trusted"

# Arquivos brutos
CLIENTES_RAW = RAW_DIR / "dadoscliente.csv"
VENDAS_RAW = RAW_DIR / "dadosvendas.csv"

# Arquivo final tratado
OUTPUT_TRUSTED = TRUSTED_DIR / "vendas_clientes.parquet"

REFINED_DIR = BASE_DIR / "dados" / "refined"