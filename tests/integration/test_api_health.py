"""
Testes de Integração - API de Health Check
Fase 1: MVP Core
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Testes para endpoints de health check"""
    
    def test_health_status_public(self):
        """Testa endpoint público de status"""
        response = client.get("/api/v1/health/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0-multi-tenant"
        assert data["phase"] == "Fase 2 - Multi-Tenant + UX"
        assert "timestamp" in data
        assert "uptime_seconds" in data
    
    def test_health_detailed_authenticated(self):
        """Testa health check detalhado com autenticação"""
        # Obter token
        login_payload = {
            "username": "testuser",
            "password": "securepass123"
        }
        login_response = client.post("/api/v1/auth/login", data=login_payload)
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/health/detailed", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "api" in data
        assert "database" in data
        assert "environment" in data
        assert "dependencies" in data
        assert data["api"]["status"] == "healthy"
        assert data["database"]["connected"] is True
    
    def test_health_detailed_unauthenticated(self):
        """Testa health check detalhado sem autenticação"""
        response = client.get("/api/v1/health/detailed")
        
        assert response.status_code == 401
    
    def test_readiness_check(self):
        """Testa check de readiness"""
        response = client.get("/api/v1/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
    
    def test_liveness_check(self):
        """Testa check de liveness"""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    def test_root_endpoint(self):
        """Testa endpoint raiz"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "eSocial Rendimentos SaaS API"
        assert data["version"] == "2.0.0-multi-tenant"
        assert data["phase"] == "Fase 2 - Multi-Tenant + UX"
