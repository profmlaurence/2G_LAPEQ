import streamlit as st
import time
from utils.auth import sign_in, sign_up, get_google_auth_url, get_google_token_from_code, sign_in_with_google

def main():
    st.header("Acesso ao Sistema")
    
    # Recupera a API Key dos secrets
    api_key = st.secrets.get("firebase", {}).get("api_key")
    
    # Configuração do Google OAuth
    google_secrets = st.secrets.get("google", {})
    client_id = google_secrets.get("client_id")
    client_secret = google_secrets.get("client_secret")
    redirect_uri = google_secrets.get("redirect_uri", "http://localhost:8501/login")
    
    if not api_key:
        st.error("⚠️ Configuração do Firebase não encontrada. Verifique o arquivo secrets.toml.")
        return

    # Lógica de Callback do Google Login (verifica se voltou do Google com um código)
    if "code" in st.query_params:
        code = st.query_params["code"]
        try:
            with st.spinner("Autenticando com Google..."):
                # 1. Troca o código pelo token do Google
                google_tokens = get_google_token_from_code(code, client_id, client_secret, redirect_uri)
                google_id_token = google_tokens["id_token"]
                
                # 2. Troca o token do Google por sessão do Firebase
                user = sign_in_with_google(google_id_token, api_key, redirect_uri)
                
                # 3. Salva sessão
                st.session_state.username = user.get("email")
                st.session_state.id_token = user.get("idToken")
                st.session_state.local_id = user.get("localId")
                st.session_state.logged_in = True
                
                st.success(f"Bem-vindo, {user.get('email')}!")
                # Limpa a URL
                st.query_params.clear()
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(f"Erro no login com Google: {e}")
            st.query_params.clear()

    tab1, tab2 = st.tabs(["Login", "Criar Conta"])

    with tab1:
        col1, col2 = st.columns([1, 1])
        email = col1.text_input("Email", key="login_email")
        password = col2.text_input("Senha", type="password", key="login_pass")
        
        if st.button("Entrar", key="login_btn", type="primary"):
            if not email or not password:
                st.warning("Preencha todos os campos.")
            else:
                with st.spinner("Autenticando..."):
                    user = sign_in(email, password, api_key)
                    
                if "error" in user:
                    error_msg = user["error"]
                    if "INVALID_LOGIN_CREDENTIALS" in error_msg or "EMAIL_NOT_FOUND" in error_msg or "INVALID_PASSWORD" in error_msg:
                        st.error("Email ou senha incorretos.")
                    else:
                        st.error(f"Erro de autenticação: {error_msg}")
                    st.session_state.logged_in = False
                else:
                    st.session_state.username = user.get("email")
                    st.session_state.id_token = user.get("idToken")
                    st.session_state.local_id = user.get("localId")
                    st.session_state.logged_in = True
                    st.success("Login bem-sucedido!")
                    time.sleep(1)
                    st.rerun()
        
        # Botão de Login com Google
        if client_id and client_secret:
            st.divider()
            auth_url = get_google_auth_url(client_id, redirect_uri)
            st.link_button("Entrar com Google", auth_url, type="secondary", use_container_width=True)

    with tab2:
        col1, col2 = st.columns([1, 1])
        new_email = col1.text_input("Email", key="signup_email")
        new_password = col2.text_input("Senha", type="password", key="signup_pass")
        
        if st.button("Cadastrar", key="signup_btn", type="primary"):
            if not new_email or not new_password:
                st.warning("Preencha todos os campos.")
            else:
                with st.spinner("Criando conta..."):
                    user = sign_up(new_email, new_password, api_key)
            
                if "error" in user:
                    error_msg = user["error"]
                    if "EMAIL_EXISTS" in error_msg:
                        st.error("Este email já está cadastrado.")
                    elif "WEAK_PASSWORD" in error_msg:
                        st.error("A senha deve ter pelo menos 6 caracteres.")
                    elif "INVALID_EMAIL" in error_msg:
                        st.error("Email inválido.")
                    else:
                        st.error(f"Erro no cadastro: {error_msg}")
                else:
                    st.session_state.username = user.get("email")
                    st.session_state.id_token = user.get("idToken")
                    st.session_state.local_id = user.get("localId")
                    st.session_state.logged_in = True
                    st.success("Conta criada com sucesso! Entrando...")
                    time.sleep(1)
                    st.rerun()

if __name__ == "__main__":
    main()