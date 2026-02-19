import streamlit as st
from config import DATASET_DIR, DEFAULT_DATA


st.set_page_config(
    page_title="Bioethanol 2G Parameters Optimizer",
    page_icon="assets/microscope.png",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': 'This is a bioethanol 2G optimizer application.'
        }
)


st.title("🧪 Bioethanol 2G Optimizer LAPEQ")
st.markdown(
    "Este aplicativo web permite otimizar os parâmetros do processo de produção de bioetanol 2G."
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def logout():
    # if st.button("Log out"):
    st.session_state.logged_in = False
    st.rerun()

login_page = st.Page("pages/login.py", title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Sair", icon=":material/logout:")

main = st.Page("main.py", title="Home", icon="🏠")
data_page = st.Page("pages/data.py", title="Seleção dos Dados", icon="📀")
train_page = st.Page("pages/train.py", title="Treinamento", icon="🧠")
simulation_page = st.Page("pages/simulation.py", title="Simulação", icon="📈")
prediction_page = st.Page("pages/prediction.py", title="Previsão de Rendimento", icon="🔮")
pred_page = st.Page("pages/pred.py", title="NEW Previsão de Rendimento", icon="♻️")
config_user = st.Page("pages/config_user.py", title="Configurações", icon="⚙️")
apresentacao_page = st.Page("pages/apresentacao.py", title="Apresentação", icon="⚗️")
pricing_page = st.Page("pages/pricing.py", title="Planos", icon="💲")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "": [main, apresentacao_page, pricing_page],
            # "": [main],
            "Treinamento": [data_page,train_page, simulation_page],
            "Previsão": [prediction_page],#, pred_page],
            "Configurações": [config_user,logout_page],
        }
    )
    # st.sidebar.page_link(logout_page)
else:
    # pg = st.navigation([login_page])
    pg = st.navigation([apresentacao_page, login_page, pricing_page])

pg.run()


# pg.run()
# Footer
st.markdown(
    "<div style='text-align: center; color: grey;'>Laboratório de Pesquisa em Química Ambiental e de Biocombustíveis <br/>Universidade Federal do Tocantins - UFT, Campus de Palmas - CUP.</div>",
    unsafe_allow_html=True)