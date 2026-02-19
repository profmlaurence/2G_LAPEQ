import streamlit as st

def main():
    st.set_page_config(
        page_title="Apresentação - 2G LAPEQ",
        page_icon="⚗️",
        layout="wide"
    )

    # st.title("⚗️ 2G LAPEQ - Otimização de Bioetanol")
    # st.markdown("### Laboratório de Pesquisa em Engenharia Química")

    cols = st.columns([1, 2, 2, 1])
    with cols[1]:
        if not st.session_state.get("logged_in", False):
            if st.button("🔐 Fazer Login", use_container_width=True):
                st.switch_page("pages/login.py")
    with cols[2]:
        if st.button("💰 Preços e Planos", use_container_width=True):
            st.switch_page("pages/pricing.py")

    st.divider()

    st.header("🚀 Funcionalidades do Sistema")

    st.markdown("""
    A plataforma **2G LAPEQ** é uma solução integrada para a **análise, modelagem e otimização** de processos de produção de Bioetanol de 2ª Geração. 
    Utilizando o estado da arte em Inteligência Artificial, oferecemos ferramentas para transformar dados experimentais em modelos preditivos precisos.
    """)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Engenharia de Dados")
        st.markdown("""
        *   **Gestão de Datasets**: Upload intuitivo e listagem de arquivos CSV.
        *   **Dados Sintéticos**: Gerador integrado para ampliação de amostras e testes de estresse dos modelos.
        *   **Pré-processamento**: Tratamento automático de variáveis e normalização.
        """)
        
        st.subheader("📈 Análise de Performance")
        st.markdown("""
        *   **Métricas Robustas**: Avaliação via R², MSE e RMSE.
        *   **Visualização Avançada**: Gráficos 3D interativos para exploração de superfícies de resposta.
        *   **Diagnóstico**: Matrizes de confusão e curvas de erro.
        """)

    with col2:
        st.subheader("🧠 Modelagem Preditiva")
        st.markdown("""
        Biblioteca diversificada de algoritmos de Machine Learning:
        *   **SVM (Support Vector Machine)**: Implementação otimizada (Vinitha, 2023).
        *   **Redes Neurais (MLP)**: Arquitetura profunda proposta por *Freitas, Gramacho e Guarda (2024)*.
        *   **Modelos Híbridos**: Combinação de PCA + ANN + SVM para alta dimensionalidade.
        *   **Benchmarks**: Random Forest e Regressão Linear.
        """)

        st.subheader("⚙️ Otimização Automática")
        st.markdown("""
        *   **Grid Search**: Busca exaustiva pelos melhores hiperparâmetros.
        *   **Persistência**: Salve modelos treinados e recupere-os instantaneamente.
        """)

    # st.divider()
    
    # col1, col2 = st.columns([3, 1])
    # with col1:
    #     st.info("👈 Utilize o menu lateral para acessar as ferramentas de **Dados**, **Treinamento** e **Predição**.")
    # with col2:
    #     if not st.session_state.get("logged_in", False):
    #         if st.button("🔐 Fazer Login", use_container_width=True):
    #             st.switch_page("pages/login.py")

if __name__ == "__main__":
    main()