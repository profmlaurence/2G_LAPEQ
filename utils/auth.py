import requests
import streamlit as st
import urllib.parse

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

def get_google_auth_url(client_id, redirect_uri):
    """Gera a URL para autenticação OAuth2 do Google."""
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def get_google_token_from_code(code, client_id, client_secret, redirect_uri):
    """Troca o código de autorização pelo token de acesso/ID do Google."""
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()

def sign_in_with_google(id_token, api_key, request_uri="http://localhost"):
    """Autentica no Firebase usando o ID Token do Google (signInWithIdp)."""
    request_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "postBody": f"id_token={id_token}&providerId=google.com",
        "requestUri": request_uri,
        "returnIdpCredential": True,
        "returnSecureToken": True
    }
    response = requests.post(request_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def sign_up(email, password, api_key):
    """
    Cria um novo usuário usando a API REST do Firebase Auth.
    """
    request_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(request_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        return {"error": response.json().get('error', {}).get('message', 'Erro desconhecido')}
    except Exception as e:
        return {"error": str(e)}
