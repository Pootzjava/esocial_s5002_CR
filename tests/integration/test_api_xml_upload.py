"""
Testes de Integração - API de Upload XML
Fase 1: MVP Core
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
import io

client = TestClient(app)


# Fixture para obter token de autenticação
@pytest.fixture
def auth_token():
    """Obtém token de autenticação para testes"""
    login_payload = {
        "username": "testuser",
        "password": "securepass123"
    }
    response = client.post("/api/v1/auth/login", data=login_payload)
    return response.json()["access_token"]


class TestXMLUploadEndpoints:
    """Testes para endpoints de upload XML"""
    
    def test_upload_xml_success(self, auth_token):
        """Testa upload de XML com sucesso"""
        # Criar XML mock
        xml_content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <eSocial xmlns="http://www.esocial.gov.br/schema/evt/evtPgtos/v_S_01_02_00">
            <evtPgtos>
                <ideBenef>
                    <cpfBenef>12345678901</cpfBenef>
                </ideBenef>
            </evtPgtos>
        </eSocial>'''
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        files = {"file": ("test.xml", io.BytesIO(xml_content), "application/xml")}
        
        response = client.post("/api/v1/xml/upload", files=files, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["filename"] == "test.xml"
        assert data["status"] == "processed"
        assert "events_count" in data
        assert "employees_count" in data
    
    def test_upload_non_xml_file(self, auth_token):
        """Testa upload de arquivo não XML"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        files = {"file": ("test.txt", b"content", "text/plain")}
        
        response = client.post("/api/v1/xml/upload", files=files, headers=headers)
        
        assert response.status_code == 400
        assert "Only XML files are allowed" in response.json()["detail"]
    
    def test_upload_invalid_xml(self, auth_token):
        """Testa upload de XML inválido"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        files = {"file": ("invalid.xml", b"<invalid>", "application/xml")}
        
        response = client.post("/api/v1/xml/upload", files=files, headers=headers)
        
        assert response.status_code == 400
    
    def test_upload_without_auth(self):
        """Testa upload sem autenticação"""
        xml_content = b'<?xml version="1.0"?><root></root>'
        files = {"file": ("test.xml", io.BytesIO(xml_content), "application/xml")}
        
        response = client.post("/api/v1/xml/upload", files=files)
        
        assert response.status_code == 401
    
    def test_list_processed_files(self, auth_token):
        """Testa listagem de arquivos processados"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/api/v1/xml/list", headers=headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_delete_file(self, auth_token):
        """Testa deleção de arquivo"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.delete("/api/v1/xml/test-id", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "File deleted successfully"
