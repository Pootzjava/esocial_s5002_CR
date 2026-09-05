import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Cria instância do axios com configurações padrão
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token JWT automaticamente
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      
      // Extrai tenant_id do token (em produção usar decodificação JWT real)
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.tenant_id) {
          config.headers['X-Tenant-ID'] = payload.tenant_id;
        }
      } catch (e) {
        console.error('Erro ao decodificar token:', e);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para lidar com erros de autenticação
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Métodos utilitários
export const authAPI = {
  login: (email: string, password: string) => 
    apiClient.post('/api/v1/auth/login', { email, password }),
  
  register: (data: any) => 
    apiClient.post('/api/v1/auth/register', data),
};

export const employeesAPI = {
  list: () => apiClient.get('/api/v1/employees'),
  getById: (id: number) => apiClient.get(`/api/v1/employees/${id}`),
  generatePDF: (id: number, year: number) => 
    apiClient.get(`/api/v1/pdf/generate/${id}?year=${year}`, { responseType: 'blob' }),
};

export const uploadAPI = {
  uploadXML: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/v1/xml/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const billingAPI = {
  getPlans: () => apiClient.get('/api/v1/billing/plans'),
  getSubscription: () => apiClient.get('/api/v1/billing/subscription'),
  createCheckout: (planTier: string) => 
    apiClient.post('/api/v1/billing/checkout', {
      plan_tier: planTier,
      success_url: `${window.location.origin}/billing/success`,
      cancel_url: `${window.location.origin}/billing/cancel`,
    }),
};
