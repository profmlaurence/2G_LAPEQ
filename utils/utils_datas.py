import time
import joblib
import streamlit as st
import pandas as pd
from config import DATASET_DIR, DEFAULT_DATA  # Importar desde config
from pathlib import Path  # Import correcto de Path

def handle_existing_dataset(filename):
    """Carrega e exibe datasets existentes."""
    file_path = DATASET_DIR / DEFAULT_DATA  # Usar Path desde config
    
    try:
        dataset = pd.read_csv(file_path)
        st.session_state.current_dataset = dataset
        st.session_state.filename = filename
        # print(st.session_state.current_dataset)
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado: {file_path}")
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")

def list_files(path=None):
    """Lista todos os arquivos no diretório especificado, usando pathlib."""
    p = Path(path) if path else Path(DATASET_DIR)
    files = []
    if p.exists() and p.is_dir():
        for item in p.iterdir():
            if item.is_file():
                # print(f"Arquivo: {item.name}")
                files.append(item.name)
    else:
        print("Diretório não encontrado ou não é um diretório válido.")
    return files

def handle_new_dataset():
    """Processa upload de novos datasets."""
    dataset = upload_file()
    if dataset is not None:
        st.session_state.new_dataset = dataset
        return True
    
    return False
        # show_data_interface()

def upload_file():
    """Componente para upload de arquivo CSV."""
    uploaded_file = st.file_uploader(
        "Escolha um arquivo CSV para upload", 
        type="csv"
    )
    return pd.read_csv(uploaded_file) if uploaded_file else None

def handle_synthetics(current_samples):
    """Interface para geração de dados sintéticos."""
    cols = st.columns(2)
    
    with cols[0]:
        new_samples = st.slider(
            "Número de amostras", 
            min_value=100, 
            max_value=1000, 
            value=100
        )
        
        if st.button("Gerar Dados"):
            with cols[1]:
                with st.spinner(f"Gerando {new_samples} amostras..."):
                    time.sleep(new_samples / 100)  # Simulação
                    
                # Atualiza o dataset na sessão
                updated_dataset = generate_synthetic_data(
                    st.session_state.current_dataset,new_samples
                    )
                st.session_state.current_dataset = updated_dataset
                
                st.success("Dados sintéticos gerados com sucesso!")
                st.write(f"Novo total de amostras: {len(updated_dataset)}")

def generate_synthetic_data(dataset, num_samples):
    """Gera dados sintéticos (implementação simulada)."""
    # TODO: Implementar lógica real de geração de dados sintéticos
    return pd.concat([dataset] * (num_samples // len(dataset) + 1), ignore_index=True)

def handle_save(dataset, name=DEFAULT_DATA):
    """Gerencia o processo de salvamento e treinamento."""
    
    if 'filename' not in st.session_state:
        st.session_state.filename = DEFAULT_DATA
    
    try:
        dataset.to_csv(name, index=False)
        # os.save(filename, dataset)
        st.success(f"Dados salvos com sucesso como {st.session_state.filename}!")
        
    except Exception as e:
        st.error(f"Erro ao salvar arquivo: {str(e)}")

def load_model(filepath):
        """Loads a trained model and its metadata from a serialized file."""
        try:
            # Load the data from the specified file
            training_data = joblib.load("trained_models/"+filepath)

            # Extract the components
            # model = training_data['model']
            # model_name = training_data['model_name']
            # columns_input = training_data['columns_input']
            # columns_output = training_data['columns_output']

            # st.success(f"Modelo '{model_name}' carregado com sucesso de: `{filepath}`")

            st.session_state.loaded_model = training_data

            return

        except FileNotFoundError:
            st.error(f"Erro: O arquivo não foi encontrado em `{filepath}`.")
            return
        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar o modelo: {e}")
            return