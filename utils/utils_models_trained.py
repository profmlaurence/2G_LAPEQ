import os
import time
import streamlit as st
from utils.bucket_connect import BucketUtils
import utils.utils_datas as data

class UtilsModelsTrained:
    def __init__(self, bucket=None):
        self.bucket = bucket

    @staticmethod
    def load_model_selector(bucket=None):
        col1, col2 = st.columns([0.85, 0.15], vertical_alignment="bottom")
        
        modelo_select = " "
        
        with col1:
            if bucket:
                blobs = list(bucket.list_blobs(prefix='trained_models/'))
                files = [blob.name for blob in blobs if not blob.name.endswith('/')]
                modelo_select = st.selectbox("Selecione o modelo", [" "] + files, index=0)
            else:
                files = data.list_files("trained_models")
                modelo_select = st.selectbox("Selecione o modelo", [" "] + files, index=0)
        
        with col2:
            if modelo_select != " ":
                if st.button("🗑️", help="Excluir modelo selecionado"):
                    try:
                        if bucket:
                            BucketUtils.delete_blob_from_bucket(bucket, modelo_select)
                            time.sleep(2)
                            st.rerun()
                        else:
                            os.remove(os.path.join("trained_models", modelo_select))
                            st.toast(f"Modelo excluído!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
        
        return modelo_select