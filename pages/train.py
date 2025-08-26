import time
import streamlit as st
import utils.BioethanolOptimizer as bioopt


def select_dataset():
    dataset = st.session_state.current_dataset
    st.success(f"Dataset: {st.session_state.filename}",icon="💾")
    # aim = [col for col in dataset.columns if st.checkbox(f"Selecionar {col} como coluna do resultado esperado", key=f"aim_{col}")]
    # aim = st.multiselect("Selecionar colunas do resultado esperado", dataset.columns)
    df_output = dataset[st.segmented_control("Selecionar a(s) coluna(s) de saída. Colunas com texto serão automaticamente excluídas", dataset.columns, selection_mode="multi")]
    df_input = dataset.drop(columns=df_output)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Colunas de entrada**")
        st.write(", ".join(df_input.columns))
        # st.dataframe(input.head())
    with col2:
        st.markdown("**Colunas de saída**")
        st.write(", ".join(df_output.columns))
        # st.dataframe(output.head())
            
    st.divider()
    return df_input.columns, df_output.columns
            
        # st.write(aim.columns)

    
def select_model(columns_input,columns_output, bioopt=None):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Modelos disponíveis:")

        if len(columns_output) < 1:
            st.error("Adicine pelo menos uma coluna de saída para treinar o modelo")
        else:
            model = st.selectbox("Modelos disponíveis:", bioopt.models.keys())
            with st.spinner("Treinando modelo..."):
                time.sleep(1)
                
                r2, mse, qmse, params, model_train = bioopt.fit_model(model, columns_input, columns_output)

                # r2, mse, qmse, real_predito, curva = bioethanol_optimizer.fit_model_optimized(model, columns_input, columns_output)

                colR, colM, colRM = st.columns(3)
                with colM:
                    st.metric("R² Score", f"{r2:.3f}")
                with colR:
                    st.metric("MSE", f"{mse:.3f}")
                with colRM:
                    st.metric("RMSE", f"{qmse:.3f}")
                
            with col2:
                # st.markdown("### Parâmetros de treinamento")
                # params=None
                st.expander("Parâmetros do treinamento", expanded=False,icon="⚙️").write(params)
                # st.write(params)
                
                padrao = st.session_state.username + time.strftime("_%Y-%m-%d-%H:%M:%S")

                filename = st.text_input("Digite o nome do modelo para salvar:", f"{model}_{padrao}")

                if st.button("Salvar treinamento", key="save_training_button",icon="💾"):
                    # with st.spinner("Salvando modelo..."):
                    bioopt.save_model(filename=filename, model=model_train, model_name=model, columns_input=columns_input, columns_output=columns_output)
                    st.session_state.current_train = filename,model_train, columns_input, columns_output
                    st.success("Modelo salvo com sucesso",icon="📂")

def main():
    st.subheader("Treinamento do Modelo")
    st.markdown(
        """
        Esta página permite treinar o modelo de previsão de rendimento de bioetanol 2G.
        """
    )
    optimizer = bioopt.BioethanolOptimizer(st.session_state.filename)

    columns_input, columns_output = select_dataset()
    if len(columns_input) > 0 and len(columns_output) > 0:
        select_model(columns_input, columns_output, optimizer)
    else:
        st.warning("Selecione um dataset e as colunas de entrada e saída para treinar o modelo.")

if __name__ == "__main__":
    main()