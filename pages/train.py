import time
import streamlit as st
import utils.BioethanolOptimizer as bioopt
from utils.bucket_connect import BucketUtils


class TrainPage:
    def __init__(self):
        self.optimizer = None
        if 'filename' in st.session_state:
            self.optimizer = bioopt.BioethanolOptimizer(st.session_state.filename)

    def select_dataset(self):
        dataset = st.session_state.current_dataset
        st.success(f"Dataset: {st.session_state.filename}", icon="💾")
        
        selected_cols = st.segmented_control(
            "Selecionar a(s) coluna(s) de saída. Colunas com texto serão automaticamente excluídas", 
            dataset.columns, 
            selection_mode="multi"
        )
        
        # Garante que df_output seja um DataFrame mesmo se nada for selecionado
        df_output = dataset[selected_cols] if selected_cols else dataset[[]]
        df_input = dataset.drop(columns=df_output.columns)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Colunas de entrada**")
            st.write(", ".join(df_input.columns))
        with col2:
            st.markdown("**Colunas de saída**")
            st.write(", ".join(df_output.columns))
                
        st.divider()
        return df_input.columns, df_output.columns

    def select_model(self, columns_input, columns_output):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Modelos disponíveis:")

            if len(columns_output) < 1:
                st.error("Adicione pelo menos uma coluna de saída para treinar o modelo")
            else:
                model_name = st.selectbox("Modelos disponíveis:", self.optimizer.models.keys())
                with st.spinner("Treinando modelo..."):
                    time.sleep(1)
                    
                    r2, mse, qmse, params, model_train = self.optimizer.fit_model(model_name, columns_input, columns_output)

                    if r2 is not None:
                        colR, colM, colRM = st.columns(3)
                        with colM:
                            st.metric("R² Score", f"{r2:.3f}")
                        with colR:
                            st.metric("MSE", f"{mse:.3f}")
                        with colRM:
                            st.metric("RMSE", f"{qmse:.3f}")
                
                with col2:
                    if r2 is not None:
                        st.expander("Parâmetros do treinamento", expanded=False, icon="⚙️").write(params)
                        
                        padrao = st.session_state.username + time.strftime("_%Y-%m-%d-%H:%M:%S")

                        filename = st.text_input("Digite o nome do modelo para salvar:", on_change=None, key="model_filename_input", placeholder=padrao )

                        if filename == "":
                            filename = padrao


                        if st.button("Salvar treinamento", key="save_training_button", icon="💾"):
                            BucketUtils.save_model_to_bucket(
                                bucket=st.session_state.bucket,
                                filename=filename,
                                model=model_train,
                                model_name=model_name,
                                columns_input=columns_input,
                                columns_output=columns_output,
                                dataset=st.session_state.current_dataset
                            )
                            st.session_state.current_train = filename, model_train, columns_input, columns_output
                            st.toast("Modelo salvo com sucesso", icon="📂", duration="long")

    def run(self):
        st.subheader("Treinamento do Modelo")
        st.markdown(
            """
            Esta página permite treinar o modelo de previsão de rendimento de bioetanol 2G.
            """
        )
        
        if self.optimizer:
            columns_input, columns_output = self.select_dataset()
            if len(columns_input) > 0 and len(columns_output) > 0:
                self.select_model(columns_input, columns_output)
            else:
                st.warning("Selecione um dataset e as colunas de entrada e saída para treinar o modelo.")
        else:
            st.warning("Nenhum dataset selecionado. Vá para a página de Dados.")

if __name__ == "__main__":
    page = TrainPage()
    page.run()