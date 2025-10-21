#!/usr/bin/env python3
"""Script para testar o sistema completo"""

import requests
import json

def testar_sistema():
    print("=== TESTANDO SISTEMA DE BANCO DE HORAS ===")
    
    base_url = "http://127.0.0.1:5000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        print("\n1. Testando página inicial...")
        response = session.get(base_url)
        print(f"Status: {response.status_code}")
        print(f"URL final: {response.url}")
        
        if response.status_code == 200:
            if "/login" in response.url:
                print("✅ Redirecionamento para login funcionando")
                
                print("\n2. Testando login...")
                
                # Primeiro, pegar o formulário de login
                login_page = session.get(f"{base_url}/login")
                print(f"Login page status: {login_page.status_code}")
                
                # Fazer login
                login_data = {
                    'username': 'Alissonporto',
                    'password': 'porto510'
                }
                
                login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
                print(f"Login response status: {login_response.status_code}")
                print(f"Login final URL: {login_response.url}")
                
                if "/dashboard" in login_response.url:
                    print("✅ Login realizado com sucesso!")
                    print("✅ Redirecionamento para dashboard funcionando!")
                else:
                    print("❌ Falha no login ou redirecionamento")
                    print("Conteúdo da resposta:")
                    print(login_response.text[:500])
            
            elif "/setup" in response.url:
                print("⚠️  Sistema redirecionando para setup - usuário admin não encontrado")
            
            else:
                print(f"❌ Redirecionamento inesperado: {response.url}")
        
        else:
            print(f"❌ Erro na página inicial: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que o servidor Flask está rodando em http://127.0.0.1:5000")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    testar_sistema()