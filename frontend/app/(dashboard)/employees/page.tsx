'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';

interface Employee {
  id: number;
  name: string;
  cpf: string;
}

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Simula carregamento de funcionários
    setEmployees([
      { id: 1, name: 'João Silva', cpf: '123.456.789-00' },
      { id: 2, name: 'Maria Santos', cpf: '987.654.321-00' },
      { id: 3, name: 'Pedro Oliveira', cpf: '456.789.123-00' },
    ]);
  }, []);

  const filtered = employees.filter(emp =>
    emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.cpf.includes(searchTerm)
  );

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Funcionários</h1>
        
        <input
          type="text"
          placeholder="Buscar por nome ou CPF..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="mb-6 w-full rounded-md border border-gray-300 px-4 py-2"
        />

        <div className="overflow-hidden rounded-lg bg-white shadow">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Nome</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">CPF</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {filtered.map((emp) => (
                <tr key={emp.id}>
                  <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">{emp.name}</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">{emp.cpf}</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    <button className="text-primary-600 hover:text-primary-900">Gerar PDF</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
