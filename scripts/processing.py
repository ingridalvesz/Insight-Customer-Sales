import pandas as pd
from datetime import datetime
import numpy as np


def preprocess_clientes(df: pd.DataFrame) -> pd.DataFrame:
    # Deep copy para evitar side effects
    df = df.copy()
    
    # Padronização de colunas
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Tratamento de tipos e valores
    df = df.astype({
        'id_compra': 'int64',
        'id_cliente': 'int64',
        'idade': 'int16',
        'avaliacao_compra': 'int8' 
    })
    
    # Filtro de idade plausível
    df = df[df['idade'].between(10, 100)]
    
    # Transformação de categóricos
    df['cashback'] = df['cashback'].map({'Sim': 1, 'Não': 0}).astype('int8')
    df['sexo_biologico'] = df['sexo_biologico'].str.strip().astype('category')
    
    # Normalização de texto
    text_cols = ['cidade', 'uf', 'regiao']
    for col in text_cols:
        df[col] = df[col].str.strip().str.title().astype('category')
    
    # Remoção de duplicatas
    df.drop_duplicates(subset='id_compra', keep='first', inplace=True)
    
    return df

def preprocess_vendas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Padronização de colunas
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Conversão de tipos
    df = df.astype({
        'id_compra': 'int64',
        'quantidade': 'int16'
    })
    
    # Conversão de datas
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    
    # Criação de colunas temporais
    df['ano'] = df['data'].dt.year.astype('int16')
    df['mes'] = df['data'].dt.month.astype('int8')
    df['dia_semana'] = df['data'].dt.day_name().astype('category')
    
    # Cálculo de valor total
    df['valor_total'] = (df['preco_unitario'] * df['quantidade']) + df['frete']
    
    # Normalização de categóricos
    df['categoria'] = df['categoria'].str.strip().str.title().astype('category')
    df['metodo_pagamento'] = df['metodo_pagamento'].str.strip().astype('category')
    
    return df

def merge_datasets(df_clientes: pd.DataFrame, df_vendas: pd.DataFrame) -> pd.DataFrame:
    # Merge com chave primária id_compra
    df_merged = pd.merge(
        df_vendas,
        df_clientes,
        on='id_compra',
        how='inner',
        validate='one_to_one'
    )
    
    # Reordenação de colunas
    col_order = [
        'id_compra', 'data', 'horario', 'ano', 'mes', 'dia_semana',
        'categoria', 'preco_unitario', 'quantidade', 'frete', 'valor_total',
        'metodo_pagamento', 'id_cliente', 'cidade', 'uf', 'regiao',
        'idade', 'sexo_biologico', 'cashback', 'avaliacao_compra'
    ]
    
    return df_merged[col_order]