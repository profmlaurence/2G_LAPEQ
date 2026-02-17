import os
import time
import streamlit as st
from utils.utils_datas import handle_save, list_files, handle_existing_dataset, handle_new_dataset, generate_synthetic_data
from config import DATASET_DIR, DEFAULT_DATA  # Importar desde config
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analyze_data(dataset):

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
            # st.dataframe(pca_df)
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
        
    # st.markdown("### Distribuição das Variáveis")
    # for col in dataset.select_dtypes(include=['number']).columns:
    #     st.subheader(f"Distribuição de `{col}`")
    #     # st.histogram(dataset[col], bins=30, title=f"Distribuição de `{col}`").interactive().display()

def gen_synthetics(dataset):
    """Interface para geração de dados sintéticos."""
    cols = st.columns(2)
    cols_buttons = st.columns([1, 2, 2, 2, 1])

    if 'data_generated' not in st.session_state:
        st.session_state.data_generated = False
    
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
                    st.session_state.current_dataset,new_samples
                    )
                st.session_state.current_dataset = updated_dataset
                st.session_state.data_generated = True
                
                st.success("Dados sintéticos gerados com sucesso!")
                st.write(f"Novo total de amostras: {len(st.session_state.current_dataset)}")
                st.session_state.bt_save = st.session_state.bt_train_save = True
            
@st.dialog("Salvar Dados", width="small")
def save_dataset_updated():
    # if not st.session_state.get("data_generated"):
    #     st.warning("Gere dados antes de salvar!")
        # return
    
    padrão = st.session_state.username + time.strftime("_%Y-%m-%d-%H:%M:%S")
    with st.form(key="save_form"):
        name = st.text_input("Nome do arquivo", value=padrão)
        submitted = st.form_submit_button("Salvar")

        if submitted:
            try:
                caminho_arquivo = str(DATASET_DIR) + "/" + name + ".csv"
                # st.session_state.current_dataset = name
                handle_save(st.session_state.current_dataset, caminho_arquivo)
            except Exception as e:
                st.error(f"Erro ao salvar arquivo: {str(e)}")
                st.session_state.current_dataset = DEFAULT_DATA
                st.session_state.bt_save = st.session_state.bt_train_save = False
            
            st.write(f"Arquivo salvo como: {name}.csv")
            # st.rerun()
        
def select_dataset():
    files = list_files()
    
    col1, col2 = st.columns([0.85, 0.15], vertical_alignment="bottom")
    
    with col1:
        if files: 
            opcoes = [" "] + files + ["Nova Base"]
            dataset_option = st.selectbox("Selecione uma base de dados:",opcoes)
            st.session_state.current_name_dataset = dataset_option
        else:
            st.warning("Nenhum arquivo encontrado no diretório informado.")

    with col2:
        if dataset_option != " ":
            if st.button("🗑️", help="Excluir dataset selecionado"):
                try:
                    os.remove(os.path.join(DATASET_DIR, dataset_option))
                    st.toast(f"Dataset excluído!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
                    
    return dataset_option

def show_data_interface(dataset=None):
    with st.expander("Visualizar Dados", expanded=False):
        # st.subheader("Pré-visualização dos Dados")
        st.dataframe(dataset)

    with st.expander("Análise Exploratória", expanded=False):
        analyze_data(dataset)
    
    if len(dataset) < 500:
        st.warning(f"""
        Total de amostras: {len(dataset)} 
        - Este valor é considerado baixo para treinamento do modelo.
        """)
    
    if st.checkbox("Gerar dados sintéticos", value=False, key="gerar"):
        gen_synthetics(dataset)
        
        
def show_action_buttons(bt_save=False, bt_train=False, bt_train_save=False, bt_analyze=False):
    """Componente com botões de ação."""
    cols = st.columns([1, 2, 2, 2, 1])
    
    with cols[1]:
        if bt_save:
            if st.button("💾 Salvar Dados"):
                save_dataset_updated()
                # handle_save(dataset)

    with cols[2]:
        if bt_train:
            if st.button("🧠 Treinar Modelo"):
                st.switch_page("pages/train.py")
        
    with cols[3]:
        if bt_train_save:
            if st.button("💾 Salvar e Treinar Modelo"):
                save_dataset_updated()
                st.switch_page("pages/train.py")
    
    with cols[3]:
        if bt_analyze:
            if st.button("📊 Analisar o Dataset"):
                analyze_data(st.session_state.current_dataset)

def main():
    st.subheader("📀 Seleção dos Dados")
    st.markdown(
        "Selecione o dataset que deseja usar para treinar o modelo ou fazer previsões."
    )
    dataset_option = select_dataset()
    st.session_state.bt_save = st.session_state.bt_train = st.session_state.bt_train_save = False

    if 'new_dataset' not in st.session_state:
        st.session_state.new_dataset = None

    if dataset_option == "Nova Base":
        st.session_state.new_dataset = None
        if handle_new_dataset():
            st.session_state.bt_save = st.session_state.bt_train = st.session_state.bt_train_save = True

        if st.session_state.new_dataset is not None:
            show_data_interface(st.session_state.new_dataset)
    elif dataset_option == " ":
        st.warning("Selecione um dataset ou faça upload de um novo.")
        
    else:
        st.session_state.bt_train = True
        st.session_state.bt_analyze = False
        handle_existing_dataset(dataset_option)
        show_data_interface(st.session_state.current_dataset)

    st.divider()
    show_action_buttons(st.session_state.bt_save, st.session_state.bt_train, st.session_state.bt_train_save, st.session_state.bt_analyze)
        
    

if __name__ == "__main__":
    main()
    