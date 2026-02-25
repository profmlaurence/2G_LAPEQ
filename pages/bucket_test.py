import streamlit as st
import inspect
import pandas as pd
import io
from utils.bucket_connect import BucketConnector

def main():
    st.set_page_config(page_title="Teste Bucket", page_icon="🪣")
    st.title("Teste de Conexão GCS")
    
    st.markdown("Esta página testa a classe `BucketConnector` definida em `utils/bucket_connect.py`.")

    # Exibir o código da classe para conferência
    with st.expander("Ver código fonte da classe"):
        try:
            source_code = inspect.getsource(BucketConnector)
            st.code(source_code, language='python')
        except Exception as e:
            st.warning(f"Não foi possível ler o código fonte: {e}")

    st.divider()

    # if st.button("Executar BucketConnector()"):
    # Executa a classe importada
    connector = BucketConnector("lapeq2g")
    bucket = connector.connect()
        
    if bucket:
        st.write(f"**Objeto Bucket:** `{bucket}`")
        st.write(f"**Nome:** `{bucket.name}`")
        st.write(f"**Endereço:** gs://{bucket.name}")
        st.write(f"**Self Link:** {bucket.self_link}")
        
        # Validação extra: Tentar listar arquivos para garantir que as credenciais funcionam
        st.info("Tentando listar os blobs para validar permissões de leitura...")
        try:
            blobs = list(bucket.list_blobs())
            if blobs:
                st.success(f"✅ Conexão bem-sucedida! O bucket contém {len(blobs)} objetos.")
                
                blob_names = [f"{blob.name} ({blob.size} bytes)" for blob in blobs]
                st.write("**Objetos no Bucket:**")  
                st.write(blob_names)

                # Select para escolher um blob
                selected_blob_name = st.selectbox("Selecione um blob para carregar como DataFrame:", blob_names)
                
                if selected_blob_name:
                    # Encontrar o blob selecionado
                    selected_blob = next((blob for blob in blobs if blob.name == selected_blob_name), None)
                    if selected_blob:
                        st.write(f"**Blob Selecionado:** {selected_blob_name}")
                        try:
                            # Baixar o conteúdo do blob
                            content = selected_blob.download_as_text()
                            # Criar DataFrame assumindo que é CSV
                            df = pd.read_csv(io.StringIO(content))
                            st.write("**DataFrame do Blob:**")
                            st.dataframe(df)
                        except Exception as e:
                            st.error(f"Erro ao carregar o DataFrame: {e}")
                
            else:
                st.warning("O bucket está vazio ou não retornou objetos.")
        except Exception as e:
            if "billing account" in str(e).lower():
                st.error("❌ Erro de Faturamento: O projeto do Google Cloud não possui uma conta de faturamento ativa.")
                st.info("Para resolver: Acesse o [Console do Google Cloud](https://console.cloud.google.com/billing), selecione seu projeto e ative uma conta de faturamento. Certifique-se de que o projeto tenha permissões adequadas para acessar o GCS.")
            else:
                st.error(f"❌ Erro ao tentar ler do bucket (verifique as credenciais): {e}")

if __name__ == "__main__":
    main()