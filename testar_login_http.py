#!/usr/bin/env python3
"""Script para testar login via HTTP requests"""

import requests
import sys

def testar_login_http():
    print("=== TESTANDO LOGIN VIA HTTP ===")
    
    base_url = "http://127.0.0.1:5000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Testar página inicial
        print("1. Acessando página inicial...")
        resp = session.get(base_url, allow_redirects=True)
        print(f"   Status: {resp.status_code}")
        print(f"   URL final: {resp.url}")
        
        # 2. Fazer login POST
        print("\n2. Fazendo login...")
        login_data = {
            'username': 'alissonporto',
            'password': 'porto510'
        }
        
        resp = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"   Status: {resp.status_code}")
        print(f"   Location header: {resp.headers.get('Location', 'Nenhum')}")
        print(f"   Cookies recebidos: {dict(session.cookies)}")
        
        # 3. Tentar acessar dashboard
        print("\n3. Testando acesso ao dashboard...")
        resp = session.get(f"{base_url}/dashboard", allow_redirects=False)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print("   ✅ Dashboard acessível - Login OK!")
        elif resp.status_code == 302:
            location = resp.headers.get('Location', '')
            print(f"   ❌ Redirecionado para: {location}")
            if '/login' in location:
                print("   🔍 Problema: Sessão não está sendo mantida")
            
        # 4. Verificar se há cookies de sessão
        print(f"\n4. Cookies ativos: {list(session.cookies.keys())}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando em http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    testar_login_http()