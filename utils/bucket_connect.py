from io import StringIO, BytesIO
import time

from google.cloud import storage
import pandas as pd
import streamlit as st
import joblib

class BucketConnector:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = None
        self.bucket = None
        self.connect()

    def connect(self):
        if self.bucket is not None:
            return self.bucket
        try:
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(self.bucket_name)
            st.success(f"Connected to bucket: {self.bucket_name}")
            return self.bucket
        except Exception as e:
            st.error(f"Error connecting to bucket: {e}")
            return None

    def list_directories(self):
        if not self.bucket:
            self.connect()
        blobs = self.bucket.list_blobs(delimiter='/')
        directories = set()
        for page in blobs.pages:
            directories.update(page.prefixes)
        return sorted(list(directories))
    
    def display_bucket_objects(bucket):
        """Display all objects in the bucket."""
        blobs = list(bucket.list_blobs())
        if blobs:
            st.success(f"✅ Conexão bem-sucedida! O bucket contém {len(blobs)} objetos.")
            
            blob_names = [f"{blob.name} ({blob.size} bytes)" for blob in blobs]
            st.write("**Objetos no Bucket:**")  
            st.write(blob_names)
            
            return blobs
        else:
            st.warning("O bucket está vazio ou não retornou objetos.")
            return None

class BucketUtils:
    @staticmethod
    def read_csv_from_bucket(bucket, blob_name):
        """Read a CSV file from the bucket and return it as a DataFrame."""
        try:
            blob = bucket.blob(blob_name)
            if blob.exists():
                data = blob.download_as_text()
                return pd.read_csv(StringIO(data))
            else:
                st.error(f"Arquivo não encontrado no bucket: {blob_name}")
                return None
        except Exception as e:
            st.error(f"Erro ao ler arquivo do bucket: {e}")
            return None
    
    @staticmethod
    def upload_csv_to_bucket(bucket, df, blob_name):
        """Upload a DataFrame as a CSV file to the bucket."""
        try:
            csv_data = df.to_csv(index=False)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(csv_data, content_type='text/csv')
            st.success(f"Arquivo '{blob_name}' enviado com sucesso para o bucket!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao enviar arquivo para o bucket: {e}")
    
    @staticmethod
    def delete_blob_from_bucket(bucket, blob_name):
        """Delete a blob from the bucket."""
        try:
            blob = bucket.blob(blob_name)
            if blob.exists():
                blob.delete()
                st.toast(f"Arquivo '{blob_name}' deletado com sucesso do bucket!")
            else:
                st.toast(f"Arquivo '{blob_name}' não encontrado no bucket.")
        except Exception as e:
            st.error(f"Erro ao deletar arquivo do bucket: {e}")
    
    @staticmethod
    def load_model_from_bucket(bucket, blob_name):
        """Load a model from the bucket."""
        try:
            blob = bucket.blob(blob_name)
            if blob.exists():
                buffer = BytesIO()
                blob.download_to_file(buffer)
                buffer.seek(0)
                return joblib.load(buffer)
            else:
                st.error(f"Arquivo não encontrado no bucket: {blob_name}")
                return None
        except Exception as e:
            st.error(f"Erro ao carregar modelo do bucket: {e}")
            return None

    @staticmethod
    def save_model_to_bucket(bucket, filename, model, model_name, columns_input, columns_output, dataset):
        """Saves the trained model and its metadata to a serialized file in the bucket."""

        try:
            # Data to be saved
            training_data = {
                'model': model,
                'model_name': model_name,
                'columns_input': columns_input,
                'columns_output': columns_output,
                'dataset': dataset,
                'filename': filename,
            }

            # Sanitize model_name for use as a filename
            safe_filename = filename + "_" + "".join(x for x in model_name if x.isalnum() or x in "._- ").replace(" ", "_")
            blob_name = f"trained_models/{safe_filename}.joblib"

            # Serialize and save the data to buffer
            buffer = BytesIO()
            joblib.dump(training_data, buffer)
            buffer.seek(0)

            # Upload to bucket
            blob = bucket.blob(blob_name)
            blob.upload_from_file(buffer, content_type='application/octet-stream')

            st.success(f"Modelo '{model_name}' salvo com sucesso no bucket: `{blob_name}`")

        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o modelo no bucket: {e}")