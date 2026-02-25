from google.cloud import storage
import streamlit as st

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