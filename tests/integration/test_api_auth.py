"""
Testes de Integração - API de Autenticação
Fase 1: MVP Core
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


class TestAuthEndpoints:
    """Testes para endpoints de autenticação"""
    
    def test_register_user_success(self):
        """Testa registro de usuário com sucesso"""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
            "tenant_id": "tenant-001"
        }
        
        response = client.post("/api/v1/auth/register", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["tenant_id"] == 1  # Alterado para int
        assert data["is_active"] is True
    
    def test_register_user_short_password(self):
        """Testa registro com senha curta"""
        payload = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "short",
            "tenant_id": 1  # Alterado para int
        }
        
        response = client.post("/api/v1/auth/register", json=payload)
        
        assert response.status_code == 400
        assert "Password must be at least 8 characters" in response.json()["detail"]
    
    def test_login_success(self):
        """Testa login com sucesso"""
        payload = {
            "username": "testuser",
            "password": "securepass123"
        }
        
        response = client.post("/api/v1/auth/login", data=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_short_password(self):
        """Testa login com senha curta"""
        payload = {
            "username": "testuser",
            "password": "short"
        }
        
        response = client.post("/api/v1/auth/login", data=payload)
        
        assert response.status_code == 401
    
    def test_get_me_authenticated(self):
        """Testa obtenção de dados do usuário autenticado"""
        # Primeiro fazer login
        login_payload = {
            "username": "testuser",
            "password": "securepass123"
        }
        login_response = client.post("/api/v1/auth/login", data=login_payload)
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_get_me_unauthenticated(self):
        """Testa obtenção de dados sem autenticação"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
