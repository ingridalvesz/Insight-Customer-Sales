import pandas as pd
from config import CLIENTES_RAW, VENDAS_RAW

def load_clientes() -> pd.DataFrame:
    return pd.read_csv(CLIENTES_RAW)

def load_vendas() -> pd.DataFrame:
    return pd.read_csv(VENDAS_RAW)