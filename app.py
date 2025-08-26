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


def login():
    col1, col2 = st.columns([1, 1])
    username = col1.text_input("Usuário", value="lapeq", disabled=True)
    password = col2.text_input("Senha", type="password", value="la123", disabled=True)
    if st.button("Log in", key="login"):
        if username == "lapeq" and password == "la123":
            st.session_state.username = username
            st.session_state.logged_in = True
            st.success("Login bem-sucedido!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
            st.session_state.logged_in = False
        # st.session_state.logged_in = True

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

main = st.Page("main.py", title="Home", icon="🏠")
data_page = st.Page("pages/data.py", title="Seleção dos Dados", icon="📀")
train_page = st.Page("pages/train.py", title="Treinamento", icon="🧠")
simulation_page = st.Page("pages/simulation.py", title="Simulação", icon="📈")
prediction_page = st.Page("pages/prediction.py", title="Previsão de Rendimento", icon="🔮")
pred_page = st.Page("pages/pred.py", title="NEW Previsão de Rendimento", icon="♻️")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Account": [main,logout_page],
            # "": [main],
            "Treinamento": [data_page,train_page, simulation_page],
            "Previsão": [prediction_page, pred_page]
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()


# pg.run()
# Footer
st.markdown(
    "<div style='text-align: center; color: grey;'>Laboratório de Pesquisa em Química Ambiental e de Biocombustíveis <br/>Universidade Federal do Tocantins - UFT, Campus de Palmas - CUP.</div>",
    unsafe_allow_html=True)