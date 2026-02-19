import requests
import streamlit as st

def sign_in(email, password, api_key):
    """
    Autentica o usuário usando a API REST do Firebase Auth.
    """
    request_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(request_url, headers=headers, json=payload)
        response.raise_for_status() # Levanta erro para códigos 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError:
        return {"error": response.json().get('error', {}).get('message', 'Erro desconhecido')}
    except Exception as e:
        return {"error": str(e)}
