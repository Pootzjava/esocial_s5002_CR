'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import StatCard from '@/components/StatCard';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState({ employees: 0, pdfs: 0, uploads: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    // Simula carregamento de dados
    setStats({ employees: 156, pdfs: 1240, uploads: 23 });
    setLoading(false);
  }, [router]);

  if (loading) return <div className="p-8">Carregando...</div>;

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="grid gap-6 md:grid-cols-3">
          <StatCard title="Funcionários" value={stats.employees} icon="👥" />
          <StatCard title="PDFs Gerados" value={stats.pdfs} icon="📄" />
          <StatCard title="Uploads XML" value={stats.uploads} icon="📤" />
        </div>
      </main>
    </div>
  );
}
