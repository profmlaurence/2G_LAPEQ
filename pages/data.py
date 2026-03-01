import os
import time
import streamlit as st
from utils.utils_datas import handle_save, list_files, handle_existing_dataset, handle_new_dataset, generate_synthetic_data
from utils.bucket_connect import BucketConnector, BucketUtils
from config import DATASET_DIR, DEFAULT_DATA  # Importar desde config
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class DataPage:
    def __init__(self):
        self.bucket = st.session_state.get("bucket", None)
        self._initialize_session_state()

    def _initialize_session_state(self):
        if 'data_generated' not in st.session_state:
            st.session_state.data_generated = False
        if 'new_dataset' not in st.session_state:
            st.session_state.new_dataset = None
        
        # Initialize button states
        for key in ['bt_save', 'bt_train', 'bt_train_save', 'bt_analyze']:
            if key not in st.session_state:
                st.session_state[key] = False

    def analyze_data(self, dataset):
        try:
            st.markdown("### Matriz de Correlação")
            
            corr = dataset.corr()
            st.dataframe(corr.style.background_gradient(cmap='coolwarm').format("{:.2f}"))

            st.markdown("### PCA")
            
            pca = PCA(n_components=2)
            numeric_data = dataset.select_dtypes(include=['number']).dropna()
            if numeric_data.shape[1] >= 2:
                pca_result = pca.fit_transform(numeric_data)
                pca_df = pd.DataFrame(pca_result, columns=['PCA1', 'PCA2'])
                
                tab = st.tabs(["Gráfico de Dispersão PCA", "Biplot PCA"])
                with tab[0]:
                    st.markdown("##### Gráfico de Dispersão PCA")
                    st.scatter_chart(pca_df)
                with tab[1]:
                    st.markdown("##### Biplot PCA")
                    fig, ax = plt.subplots(figsize=(10, 8))
                    
                    # Plotar os pontos dos dados (scores)
                    ax.scatter(pca_result[:, 0], pca_result[:, 1], alpha=0.6, edgecolors='k')
                    
                    # Plotar as setas das variáveis (loadings)
                    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
                    for i, var in enumerate(numeric_data.columns):
                        ax.arrow(0, 0, loadings[i, 0], loadings[i, 1], 
                                head_width=0.1, head_length=0.1, fc='red', ec='red', alpha=0.7)
                        ax.text(loadings[i, 0] * 1.15, loadings[i, 1] * 1.15, var, 
                            fontsize=10, fontweight='bold', color='red')
                    
                    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
                    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
                    ax.set_title('Biplot PCA')
                    ax.grid(True, alpha=0.3)
                    ax.axhline(y=0, color='k', linewidth=0.5)
                    ax.axvline(x=0, color='k', linewidth=0.5)
                    
                    st.pyplot(fig)
        except Exception as e:
            st.error(f"Erro na análise exploratória: {str(e)}") 

    def gen_synthetics(self, dataset):
        """Interface para geração de dados sintéticos."""
        cols = st.columns(2)
        cols_buttons = st.columns([1, 2, 2, 2, 1])
        
        with cols[0]:
            new_samples = st.slider(
                "Número de amostras", 
                min_value=100, 
                max_value=1000, 
                value=100
            )
            
        with cols_buttons[1]:
            if st.button("Gerar Dados", key="generate_synthetic_data", icon="✴️"):
                with cols[1]:
                    with st.spinner(f"Gerando {new_samples} amostras..."):
                        time.sleep(new_samples / 100)  # Simulação
                        
                    # Atualiza o dataset na sessão
                    updated_dataset = generate_synthetic_data(
                        st.session_state.current_dataset, new_samples
                    )
                    st.session_state.current_dataset = updated_dataset
                    st.session_state.data_generated = True
                    
                    st.success("Dados sintéticos gerados com sucesso!")
                    st.write(f"Novo total de amostras: {len(st.session_state.current_dataset)}")
                    st.session_state.bt_save = st.session_state.bt_train_save = True

    @st.dialog("Salvar Dados", width="small")
    def save_dataset_updated(self, bucket=None):
        pattern = st.session_state.username + time.strftime("_%Y-%m-%d-%H:%M:%S")
        with st.form(key="save_form"):
            name: str = st.text_input("Nome do arquivo")
            submitted = st.form_submit_button("Salvar")

            if submitted:
                if not name:
                    name = pattern
                
                try:
                    if bucket:
                        file_path = f"dataset/{name}.csv"
                        BucketUtils.upload_csv_to_bucket(bucket, st.session_state.new_dataset, file_path)
                        print(f"Arquivo salvo como: {name}.csv")
                    # Salvar localmente se não estiver usando bucket
                    else:
                        caminho_arquivo = str(DATASET_DIR) + "/" + name + ".csv"
                        handle_save(st.session_state.new_dataset, caminho_arquivo)
                except Exception as e:
                    st.error(f"Erro ao salvar arquivo: {str(e)}")
                    st.session_state.current_dataset = DEFAULT_DATA
                    st.session_state.bt_save = st.session_state.bt_train_save = False

    def select_dataset(self):
        try:
            if self.bucket:
                files = list(self.bucket.list_blobs(prefix='dataset/'))
            else:
                files = list_files()
        except Exception as e:
            st.error(f"Erro ao listar arquivos: {str(e)}")
            files = []
        
        col1, col2 = st.columns([0.85, 0.15], vertical_alignment="bottom")
        
        dataset_option = " "
        with col1:
            if files: 
                if self.bucket:
                    opcoes = [" "] + [blob.name.split('/')[-1] for blob in files] + ["Nova Base"]
                else:
                    # Handle local files (strings or Path objects)
                    opcoes = [" "] + [f.name if hasattr(f, 'name') else str(f) for f in files] + ["Nova Base"]
                    
                dataset_option = st.selectbox("Selecione uma base de dados:", opcoes)
                st.session_state.current_name_dataset = dataset_option
            else:
                st.warning("Nenhum arquivo encontrado no diretório informado.")

        with col2:
            if dataset_option != " ":
                if st.button("🗑️", help="Excluir dataset selecionado"):
                    try:
                        if self.bucket:
                            file_path = f"dataset/{dataset_option}"
                            BucketUtils.delete_blob_from_bucket(self.bucket, file_path)
                            time.sleep(2)
                            st.rerun()
                        else:
                            os.remove(os.path.join(DATASET_DIR, dataset_option))
                            st.toast(f"Dataset excluído!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.toast(f"Erro: {e}", icon="❌")
                        
        return dataset_option

    def show_data_interface(self, dataset=None):
        try:
            with st.expander("Visualizar Dados", expanded=False):
                st.dataframe(dataset)

            with st.expander("Análise Exploratória", expanded=False):
                self.analyze_data(dataset)
            
            if len(dataset) < 500:
                st.warning(f"""
                Total de amostras: {len(dataset)} 
                - Este valor é considerado baixo para treinamento do modelo.
                """)
            
            if st.checkbox("Gerar dados sintéticos", value=False, key="gerar"):
                self.gen_synthetics(dataset)
        except Exception as e:
            st.error(f"Erro ao exibir dados: {str(e)}")

    def show_action_buttons(self):
        """Componente com botões de ação."""
        cols = st.columns([1, 2, 2, 2, 1])
        
        with cols[1]:
            if st.session_state.bt_save:
                if st.button("💾 Salvar Dados"):
                    self.save_dataset_updated(self.bucket)

        with cols[2]:
            if st.session_state.bt_train:
                if st.button("🧠 Treinar Modelo"):
                    st.switch_page("pages/train.py")
            
        with cols[3]:
            if st.session_state.bt_train_save:
                if st.button("💾 Salvar e Treinar Modelo"):
                    self.save_dataset_updated()
                    st.switch_page("pages/train.py")
        
        with cols[3]:
            if st.session_state.bt_analyze:
                if st.button("📊 Analisar o Dataset"):
                    self.analyze_data(st.session_state.current_dataset)

    def run(self):
        st.subheader("📀 Seleção dos Dados")
        st.markdown(
            "Selecione o dataset que deseja usar para treinar o modelo ou fazer previsões."
        )

        # print(st.session_state.current_dataset, "-", st.session_state.bucket)
        
        dataset_option = self.select_dataset()
        
        # Reset flags
        st.session_state.bt_save = False
        st.session_state.bt_train = False
        st.session_state.bt_train_save = False
        st.session_state.bt_analyze = False

        if dataset_option == "Nova Base":
            try:
                st.session_state.new_dataset = None
                
                uploaded_file = st.file_uploader("Escolha um arquivo CSV para upload", type="csv")
                new_dataset = pd.read_csv(uploaded_file) if uploaded_file else None

                if new_dataset is not None:
                    st.session_state.new_dataset = new_dataset
                    st.session_state.bt_save = True
                    st.session_state.bt_train = True
                    st.session_state.bt_train_save = True

                if st.session_state.new_dataset is not None:
                    self.show_data_interface(st.session_state.new_dataset)
            except Exception as e:
                st.error(f"Erro ao carregar novo dataset: {str(e)}")
                st.session_state.new_dataset = None
                st.session_state.bt_save = False
                st.session_state.bt_train = False
                st.session_state.bt_train_save = False

        elif dataset_option == " ":
            st.warning("Selecione um dataset ou faça upload de um novo.")
            
        else:
            st.session_state.bt_train = True
            if self.bucket:
                files = self.bucket.list_blobs(prefix='dataset/')
                dataset_blob = next((blob for blob in files if blob.name.split('/')[-1] == dataset_option), None)
                if dataset_blob:
                    st.session_state.current_dataset = BucketUtils.read_csv_from_bucket(self.bucket, dataset_blob.name)
                else:
                    st.error("Erro: Dataset selecionado não encontrado no bucket.")
                    st.session_state.current_dataset = DEFAULT_DATA
            else:
                handle_existing_dataset(dataset_option)

            self.show_data_interface(st.session_state.current_dataset)

        st.divider()
        self.show_action_buttons()

if __name__ == "__main__":
    page = DataPage()
    page.run()