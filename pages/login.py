import streamlit as st

def main():
    st.header("Log in")
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

if __name__ == "__main__":
    main()