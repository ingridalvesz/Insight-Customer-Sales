import pandas as pd
from datetime import datetime

# src/processing.py
def preprocess_data(df_clientes: pd.DataFrame, df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Processa e combina os datasets de clientes e vendas"""
    # Processar vendas
    df_vendas = _process_vendas(df_vendas)
    
    # Processar clientes
    df_clientes = _process_clientes(df_clientes)
    
    # Merge dos datasets
    merged = pd.merge(df_vendas, df_clientes, on='id_compra', how='inner')
    
    # Mapeamento de colunas para renomeação
    rename_map = {
        'cidade': 'no_cidade',
        'uf': 'sg_uf',
        'regiao': 'cat_regiao',
        'idade': 'nu_idade',
        'sexo_biologico': 'cat_genero',
        'cashback': 'vr_cashback',
        'avaliacao_compra': 'nu_avaliacao'
    }
    
    # Renomear colunas (apenas as que existem)
    merged = merged.rename(columns={k: v for k, v in rename_map.items() if k in merged.columns})
    
    # Selecionar colunas que existem no DataFrame
    possible_columns = [
        'id_compra', 'ts_compra', 'dt_compra', 'nu_ano', 'ano', 'nu_mes', 'mes',
        'no_dia_semana', 'dia_semana', 'cat_categoria', 'vr_unitario', 'qt_itens',
        'vr_frete', 'vr_total', 'cat_meio_pagamento', 'id_cliente', 'no_cidade',
        'sg_uf', 'cat_regiao', 'nu_idade', 'cat_genero', 'vr_cashback', 'nu_avaliacao'
    ]
    
    # Filtrar apenas colunas existentes
    available_columns = [col for col in possible_columns if col in merged.columns]
    
    return merged[available_columns]

# src/processing.py
def _process_vendas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Conversão de tipos básicos
    df['data'] = pd.to_datetime(df['data'])
    df = df.astype({
        'id_compra': 'int32',
        'quantidade': 'int16',
        'preco_unitario': 'float32',
        'frete': 'float32'
    })
    
    # Colunas derivadas
    df['ts_compra'] = pd.to_datetime(df['data'].dt.strftime('%Y-%m-%d') + ' ' + df['horario'])
    df['vr_total'] = (df['preco_unitario'] * df['quantidade']) + df['frete']
    df['nu_ano'] = df['data'].dt.year.astype('int16')
    df['nu_mes'] = df['data'].dt.month.astype('int8')
    df['no_dia_semana'] = df['data'].dt.day_name().astype('category')
    
    # Renomeação consistente
    return df.rename(columns={
        'data': 'dt_compra',
        'preco_unitario': 'vr_unitario',
        'quantidade': 'qt_itens',
        'frete': 'vr_frete',
        'categoria': 'cat_categoria',
        'metodo_pagamento': 'cat_meio_pagamento'
    }).drop(columns=['horario'], errors='ignore')

def _process_clientes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Filtro e conversão
    df = df[df['idade'].between(10, 100)]
    df = df.astype({
        'id_compra': 'int32',
        'id_cliente': 'int32',
        'idade': 'int16',
        'avaliacao_compra': 'int8'
    })
    
    # Transformações
    df['cashback'] = df['cashback'].map({'Sim': 1, 'Não': 0}).astype('int8')
    
    # Renomeação padrão
    return df.rename(columns={
        'cidade': 'no_cidade',
        'uf': 'sg_uf',
        'regiao': 'cat_regiao',
        'idade': 'nu_idade',
        'sexo_biologico': 'cat_genero',
        'cashback': 'vr_cashback',
        'avaliacao_compra': 'nu_avaliacao'
    })

if __name__ == "__main__":
    # Teste de carga
    from ingestion import load_clientes, load_vendas
    clientes = load_clientes()
    vendas = load_vendas()
    
    print("\nColunas em clientes:", clientes.columns.tolist())
    print("\nColunas em vendas:", vendas.columns.tolist())
    
    processed = preprocess_data(clientes, vendas)
    print("\nColunas no resultado:", processed.columns.tolist())
    print("\nExemplo de dados:\n", processed.head(2))