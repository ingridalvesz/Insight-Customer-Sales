import logging
from processing import preprocess_clientes, preprocess_vendas, merge_datasets
from ingestion import load_clientes, load_vendas 
from config import OUTPUT_TRUSTED
from datetime import datetime

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_pipeline():
    logging.info("Iniciando a pipeline de processamento de dados.")
    
    # Carregamento
    logging.info("Carregando datasets de clientes e vendas.")
    clientes = load_clientes()
    vendas = load_vendas()
    
    # Pré-processamento
    logging.info("Pré-processando dados dos clientes.")
    clientes_clean = preprocess_clientes(clientes)
    logging.info("Pré-processando dados das vendas.")
    vendas_clean = preprocess_vendas(vendas)
    
    # Merge e salvamento
    logging.info("Mesclando datasets.")
    final_df = merge_datasets(clientes_clean, vendas_clean)
    
    logging.info(f"Salvando dataset final em: {OUTPUT_TRUSTED}")
    final_df.to_csv(OUTPUT_TRUSTED, index=False)
    
    logging.info("[SUCESSO] Pipeline executada com êxito.")
    logging.info(f"[ESTATÍSTICAS] Registros: {len(final_df)} | Colunas: {len(final_df.columns)}")


def run_pipeline():
    # Carregamento
    clientes = load_clientes()
    vendas = load_vendas()
    
    # Pré-processamento
    clientes_clean = preprocess_clientes(clientes)
    vendas_clean = preprocess_vendas(vendas)
    
    # Merge e salvamento
    final_df = merge_datasets(clientes_clean, vendas_clean)
    final_df.to_csv(OUTPUT_TRUSTED, index=False)
    
    print(f"[SUCESSO] Dataset final salvo em: {OUTPUT_TRUSTED}")
    print(f"[ESTATÍSTICAS] Registros: {len(final_df)} | Colunas: {len(final_df.columns)}")
    print(f"[DATA] Execução em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")