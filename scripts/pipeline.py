import logging
import pandas as pd
from processing import preprocess_data
from ingestion import load_clientes, load_vendas
from dimensional import create_dimensional_models
from config import OUTPUT_TRUSTED, REFINED_DIR

# Configuração básica do logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger()

def run_pipeline():
    logger = configure_logging()
    logger.info(" Iniciando pipeline de dados")
    
    try:
        # Etapa 1: Extração
        logger.info("Carregando dados brutos")
        clientes = load_clientes()
        vendas = load_vendas()
        logger.info(f"Dados carregados | Clientes: {len(clientes)} linhas | Vendas: {len(vendas)} linhas")
        
        # Etapa 2: Transformação
        logger.info("Processando e combinando datasets")
        df_final = preprocess_data(clientes, vendas)
        
        
        # Log de colunas para debug
        logger.debug(f"Colunas no dataset trusted: {df_final.columns.tolist()}")

        # Etapa 3: Carregamento
        logger.info(f"Salvando dados tratados em: {OUTPUT_TRUSTED}")
        df_final.to_parquet(OUTPUT_TRUSTED, index=False)
        
        logger.info("Construindo modelo dimensional")
        fato, dim_tempo, dim_cliente, dim_produto = create_dimensional_models(df_final)
        
        logger.info(f"Modelo dimensional criado | "
                f"Fato: {len(fato)} registros | "
                f"Tempo: {len(dim_tempo)} | "
                f"Cliente: {len(dim_cliente)} | "
                f"Produto: {len(dim_produto)}")
        
        logger.info(f"Salvando camada refined em: {REFINED_DIR}")
                
        logger.info(f"Pipeline concluída! | Registros: {len(df_final)} | Colunas: {len(df_final.columns)}")
        logger.info(f"Timestamp: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"X Erro na execução: {str(e)}")
        raise

if __name__ == "__main__":
    run_pipeline()