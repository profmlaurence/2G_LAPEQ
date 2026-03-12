import io
import os

import pandas as pd
import streamlit as st
from utils.bucket_connect import BucketConnector, BucketUtils
from utils.utils_datas import handle_existing_dataset
from config import DATASET_DIR, DEFAULT_DATA

# Layout columns
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])


def verified_dataset():
    """Verify and set the current dataset in session state."""
    if 'current_dataset' not in st.session_state:
        handle_existing_dataset(DEFAULT_DATA)
    
    if 'current_dataset' in st.session_state:
        print(st.session_state.filename)


def handle_bucket_error(error):
    """Handle bucket connection errors."""
    if "billing account" in str(error).lower():
        st.error("❌ Erro de Faturamento: O projeto do Google Cloud não possui uma conta de faturamento ativa.")
        st.info("Para resolver: Acesse o [Console do Google Cloud](https://console.cloud.google.com/billing), selecione seu projeto e ative uma conta de faturamento. Certifique-se de que o projeto tenha permissões adequadas para acessar o GCS.")
    else:
        st.error(f"❌ Erro ao tentar ler do bucket (verifique as credenciais): {error}")


def handle_navigation_buttons():
    """Handle navigation buttons for different pages."""
    if col2.button("Treinar um novo modelo", key="new_model"):
        st.session_state.menu = True
        st.divider()
        st.switch_page("pages/data.py")

    if col3.button("Fazer Predições", key="predict_model"):
        st.session_state.menu = False
        st.switch_page("pages/prediction.py")


def main():
    """Main application function."""
    try:
        # Carrega configuração do Google Cloud Storage
        bucket_name = st.secrets.get("gcs", {}).get("storage_bucket")
        if not bucket_name:
            bucket_name = os.environ.get("GCS_STORAGE_BUCKET", "lapeq2g")
            
        bucket = BucketConnector(bucket_name).connect()
        
        if bucket:
            with st.expander("🔍 Detalhes do Bucket",expanded=True):
                st.write(f"**Objeto Bucket:** `{bucket}`")
                st.write(f"**Nome:** `{bucket.name}`")
                blobs = bucket.list_blobs(prefix='dataset/')
                
                if blobs:
                    default_blob = next((blob for blob in blobs if blob.name == f"{DATASET_DIR}/{DEFAULT_DATA}"), None)
                    if default_blob:
                        st.write(f"**Blob do Dataset Padrão:** {default_blob.name} ({default_blob.size} bytes)")
                        st.session_state.bucket = bucket
                        st.session_state.filename = DEFAULT_DATA
                        st.session_state.current_dataset = BucketUtils.read_csv_from_bucket(bucket, default_blob.name)
                    else:
                        st.warning(f"⚠️ O dataset padrão `{DEFAULT_DATA}` não foi encontrado no bucket.")
                else:
                    st.warning("⚠️ Nenhum blob encontrado no bucket com o prefixo 'dataset/'.")
        else:
            st.warning("⚠️ Não foi possível conectar ao bucket. Verifique as credenciais e a configuração do Google Cloud.")
            
        verified_dataset()
        handle_navigation_buttons()
        
    except Exception as e:
        handle_bucket_error(e)


if __name__ == "__main__":
    main()