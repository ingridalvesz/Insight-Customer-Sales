# src/dimensional.py
import pandas as pd
import numpy as np
from pathlib import Path
from config import REFINED_DIR

# src/dimensional.py
def create_dimensional_models(df: pd.DataFrame):
    """
    Valida colunas antes de processar
    Cria modelo dimensional a partir dos dados tratados
    """

    required_columns = [
        'dt_compra', 'vr_frete', 'vr_total', 'vr_cashback', 'id_cliente',
        'cat_categoria', 'cat_meio_pagamento', 'nu_idade', 'cat_genero',
        'no_cidade', 'sg_uf', 'cat_regiao'
    ]
    
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias faltando: {missing}")
    


    # Criar dimensões
    dim_tempo = create_dim_tempo(df)
    dim_cliente = create_dim_cliente(df)
    dim_produto = create_dim_produto(df)
    
    # Criar fato de vendas
    fato_vendas = create_fato_vendas(df, dim_tempo, dim_cliente, dim_produto)
    
    # Salvar modelos
    dim_tempo.to_parquet(REFINED_DIR / 'dim_tempo.parquet', index=False)
    dim_cliente.to_parquet(REFINED_DIR / 'dim_cliente.parquet', index=False)
    dim_produto.to_parquet(REFINED_DIR / 'dim_produto.parquet', index=False)
    fato_vendas.to_parquet(REFINED_DIR / 'fato_vendas.parquet', index=False)
    
    return fato_vendas, dim_tempo, dim_cliente, dim_produto

def create_dim_tempo(df):
    """Cria dimensão tempo com todas as datas únicas"""
    # Extrair datas únicas
    dates = df['dt_compra'].drop_duplicates().to_frame('dt_completa')
    
    # Criar dataframe dimensional
    dim = dates.copy()
    dim['id_tempo'] = dim['dt_completa'].dt.strftime('%Y%m%d').astype(int)
    dim['nu_ano'] = dim['dt_completa'].dt.year.astype('int16')
    dim['nu_mes'] = dim['dt_completa'].dt.month.astype('int8')
    dim['nu_dia'] = dim['dt_completa'].dt.day.astype('int8')
    dim['no_dia_semana'] = dim['dt_completa'].dt.day_name()
    dim['nu_semana_ano'] = dim['dt_completa'].dt.isocalendar().week.astype('int8')
    dim['flag_fim_semana'] = dim['no_dia_semana'].isin(['Saturday', 'Sunday']).astype('int8')
    
    # Converter para categoria após cálculos
    dim['no_dia_semana'] = dim['no_dia_semana'].astype('category')
    
    return dim[['id_tempo', 'dt_completa', 'nu_ano', 'nu_mes', 'nu_dia', 
                'no_dia_semana', 'nu_semana_ano', 'flag_fim_semana']]

def create_dim_cliente(df):
    """Cria dimensão cliente com atributos do cliente"""
    # Selecionar colunas e remover duplicatas
    dim = df[['id_cliente', 'nu_idade', 'cat_genero', 'no_cidade', 'sg_uf', 'cat_regiao']]
    dim = dim.drop_duplicates(subset='id_cliente').reset_index(drop=True)
    
    # Criar chave substituta (surrogate key)
    dim['sk_cliente'] = dim.index + 1
    
    # Criar faixa etária usando pd.cut (mais eficiente)
    bins = [0, 17, 24, 34, 44, 54, 64, 120]
    labels = ['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    dim['cat_faixa_etaria'] = pd.cut(
        dim['nu_idade'], 
        bins=bins, 
        labels=labels,
        right=False
    )
    
    # Converter para categorias
    cat_cols = ['cat_genero', 'cat_regiao', 'cat_faixa_etaria']
    dim[cat_cols] = dim[cat_cols].astype('category')
    
    return dim[['sk_cliente', 'id_cliente', 'nu_idade', 'cat_faixa_etaria', 
                'cat_genero', 'no_cidade', 'sg_uf', 'cat_regiao']]

def create_dim_produto(df):
    """Cria dimensão produto com categorias e métodos de pagamento"""
    # Combinar combinações únicas
    dim = df[['cat_categoria', 'cat_meio_pagamento']].drop_duplicates().reset_index(drop=True)
    
    # Criar chave substituta
    dim['id_produto'] = dim.index + 1
    
    # Converter para categorias
    dim['cat_categoria'] = dim['cat_categoria'].astype('category')
    dim['cat_meio_pagamento'] = dim['cat_meio_pagamento'].astype('category')
    
    return dim[['id_produto', 'cat_categoria', 'cat_meio_pagamento']]

def create_fato_vendas(df, dim_tempo, dim_cliente, dim_produto):
    """Cria fato de vendas com medidas e chaves dimensionais"""
    # Mapear chaves dimensionais
    fato = (
        df.merge(
            dim_tempo[['dt_completa', 'id_tempo']],
            left_on='dt_compra',
            right_on='dt_completa'
        )
        .merge(
            dim_cliente[['id_cliente', 'sk_cliente']],
            on='id_cliente'
        )
        .merge(
            dim_produto,
            on=['cat_categoria', 'cat_meio_pagamento']
        )
    )
    
    # Selecionar colunas finais
    return fato[['id_compra', 'id_tempo', 'sk_cliente', 'id_produto',
                'vr_unitario', 'qt_itens', 'vr_frete', 'vr_total',
                'vr_cashback', 'nu_avaliacao']]