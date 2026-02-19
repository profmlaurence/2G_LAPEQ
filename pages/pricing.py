import streamlit as st

def main():
    st.header("💲 Planos e Preços")
    st.markdown("Escolha o plano ideal para sua pesquisa ou indústria.")
    
    st.divider()

    col1, col2, col3 = st.columns(3)

    # Plano Gratuito
    with col1:
        with st.container(border=True):
            st.subheader("Pesquisador")
            st.markdown("### R$ 0 / mês")
            st.markdown("Ideal para estudantes e pesquisas iniciais.")
            st.divider()
            st.markdown("""
            *   ✅ Acesso a datasets públicos
            *   ✅ Modelos básicos (Regressão Linear)
            *   ✅ 10 Simulações/dia
            *   ❌ Exportação de resultados
            *   ❌ Suporte dedicado
            """)
            if st.button("Começar Grátis", use_container_width=True):
                st.switch_page("pages/login.py")

    # Plano Pro
    with col2:
        with st.container(border=True):
            st.subheader("Laboratório")
            st.markdown("### R$ 199 / mês")
            st.markdown("Para grupos de pesquisa e otimização avançada.")
            st.divider()
            st.markdown("""
            *   ✅ Tudo do plano Pesquisador
            *   ✅ Upload de datasets próprios
            *   ✅ Modelos avançados (SVM, Random Forest)
            *   ✅ Simulações ilimitadas
            *   ✅ Exportação em CSV/PDF
            """)
            if st.button("Assinar Pro", type="primary", use_container_width=True):
                st.switch_page("pages/login.py")

    # Plano Enterprise
    with col3:
        with st.container(border=True):
            st.subheader("Indústria")
            st.markdown("### Sob Consulta")
            st.markdown("Soluções customizadas para plantas industriais.")
            st.divider()
            st.markdown("""
            *   ✅ Tudo do plano Laboratório
            *   ✅ Redes Neurais Profundas (Deep Learning)
            *   ✅ API dedicada
            *   ✅ Deploy on-premise
            *   ✅ Suporte 24/7
            """)
            st.button("Em breve!", use_container_width=True, disabled=True)

    st.divider()
    
    st.info("💡 Dúvidas sobre qual plano escolher? Entre em contato com nossa equipe.")

if __name__ == "__main__":
    main()