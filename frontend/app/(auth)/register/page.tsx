'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    company_name: '',
    cnpj: '',
    email: '',
    password: '',
    username: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await axios.post(`${API_URL}/api/v1/auth/register`, formData);
      router.push('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar conta');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-6 rounded-lg bg-white p-8 shadow-xl">
        <h2 className="text-center text-3xl font-bold text-gray-900">Criar Conta</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <input
            type="text"
            placeholder="Nome da Empresa"
            required
            value={formData.company_name}
            onChange={(e) => setFormData({...formData, company_name: e.target.value})}
            className="block w-full rounded-md border border-gray-300 px-3 py-2"
          />
          <input
            type="text"
            placeholder="CNPJ"
            required
            value={formData.cnpj}
            onChange={(e) => setFormData({...formData, cnpj: e.target.value})}
            className="block w-full rounded-md border border-gray-300 px-3 py-2"
          />
          <input
            type="email"
            placeholder="Email"
            required
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="block w-full rounded-md border border-gray-300 px-3 py-2"
          />
          <input
            type="text"
            placeholder="Username"
            required
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            className="block w-full rounded-md border border-gray-300 px-3 py-2"
          />
          <input
            type="password"
            placeholder="Senha"
            required
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="block w-full rounded-md border border-gray-300 px-3 py-2"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-primary-600 py-2 text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'Criando...' : 'Criar Conta'}
          </button>
        </form>

        <div className="text-center">
          <a href="/login" className="text-sm font-medium text-primary-600">
            Já tem conta? Faça login
          </a>
        </div>
      </div>
    </div>
  );
}
