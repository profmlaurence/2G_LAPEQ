import streamlit as st

def main():
    st.set_page_config(
        page_title="2G LAPEQ - Bioetanol Intelligence",
        page_icon="⚗️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # --- Hero Section ---
    st.markdown("""
        <style>
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 1rem;
            background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-subtitle {
            font-size: 1.5rem;
            text-align: center;
            color: #555;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    col_spacer1, col_hero, col_spacer2 = st.columns([1, 4, 1])
    with col_hero:
        st.markdown('<div class="hero-title">Otimize a Produção de Bioetanol 2G com IA</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-subtitle">Transforme dados experimentais em modelos preditivos de alta precisão.</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🚀 Começar Agora", type="primary", use_container_width=True):
                if st.session_state.get("logged_in", False):
                    st.switch_page("pages/data.py")
                else:
                    st.switch_page("pages/login.py")

    st.divider()

    # --- Features Section ---
    st.markdown("### ⚡ Por que escolher o 2G LAPEQ?")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.subheader("📊 Engenharia de Dados")
            st.markdown("""
            Gerencie datasets complexos com facilidade.
            *   **Upload e validação** automática
            *   **Geração de dados sintéticos** para robustez
            *   **Pré-processamento** inteligente de variáveis
            """)

    with col2:
        with st.container(border=True):
            st.subheader("🧠 Modelagem Avançada")
            st.markdown("""
            Algoritmos de ponta para previsões precisas.
            *   **Redes Neurais Profundas** (Deep Learning)
            *   **SVM Otimizado** e Random Forest
            *   **Grid Search** para hiperparâmetros
            """)

    with col3:
        with st.container(border=True):
            st.subheader("📈 Insights Acionáveis")
            st.markdown("""
            Visualize resultados e tome decisões.
            *   **Superfícies de resposta 3D** interativas
            *   **Simulação de cenários** em tempo real
            *   **Métricas de performance** (R², MSE, RMSE)
            """)

    st.divider()
    
    # --- Social Proof / Stats (Mockup) ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modelos Treinados", "500+")
    c2.metric("Precisão Média", "98.5%")
    c3.metric("Datasets Processados", "10k+")
    c4.metric("Pesquisadores", "150+")

    st.divider()

    # --- CTA Section ---
    st.markdown("### 💡 Pronto para acelerar sua pesquisa?")
    
    col_cta1, col_cta2 = st.columns([2, 1])
    
    with col_cta1:
        st.markdown("""
        Junte-se a laboratórios e indústrias que já utilizam o 2G LAPEQ para otimizar processos de hidrólise e fermentação.
        Escolha o plano ideal para sua necessidade, desde pesquisa acadêmica até aplicações industriais.
        """)
    
    with col_cta2:
        if st.button("Ver Planos e Preços", use_container_width=True, icon="💰"):
            st.switch_page("pages/pricing.py")

    # --- Footer ---
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888;'>
            <small>© 2024 2G LAPEQ - Laboratório de Pesquisa em Engenharia Química. Todos os direitos reservados.</small>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()