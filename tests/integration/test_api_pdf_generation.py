"""
Testes de Integração - API de Geração de PDF
Fase 1: MVP Core
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Obtém token de autenticação para testes"""
    login_payload = {
        "username": "testuser",
        "password": "securepass123"
    }
    response = client.post("/api/v1/auth/login", data=login_payload)
    return response.json()["access_token"]


class TestPDFGenerationEndpoints:
    """Testes para endpoints de geração de PDF"""
    
    def test_generate_pdf_single(self, auth_token):
        """Testa geração de PDF individual"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "employee_ids": ["emp-001"],
            "year": 2024,
            "include_qr_code": True,
            "template": "standard"
        }
        
        response = client.post("/api/v1/pdf/generate", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "completed"
        assert data["employees_count"] == 1
        assert "download_url" in data
    
    def test_generate_pdf_batch(self, auth_token):
        """Testa geração de PDF em lote"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "year": 2024,
            "all_employees": True
        }
        
        response = client.post("/api/v1/pdf/batch", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["employees_count"] == 10  # Mock value
    
    def test_generate_pdf_invalid_year(self, auth_token):
        """Testa geração com ano inválido"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "employee_ids": ["emp-001"],
            "year": 1990,
            "include_qr_code": True
        }
        
        response = client.post("/api/v1/pdf/generate", json=payload, headers=headers)
        
        assert response.status_code == 400
        assert "Year must be between" in response.json()["detail"]
    
    def test_generate_pdf_without_auth(self):
        """Testa geração sem autenticação"""
        payload = {
            "employee_ids": ["emp-001"],
            "year": 2024
        }
        
        response = client.post("/api/v1/pdf/generate", json=payload)
        
        assert response.status_code == 401
    
    def test_get_pdf_status(self, auth_token):
        """Testa obtenção de status de geração"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/api/v1/pdf/status/test-pdf-id", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
    
    def test_delete_pdf(self, auth_token):
        """Testa deleção de PDF"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.delete("/api/v1/pdf/test-pdf-id", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "PDF deleted successfully"
