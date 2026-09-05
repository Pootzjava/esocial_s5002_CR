'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Upload XML', href: '/upload' },
  { name: 'Funcionários', href: '/employees' },
  { name: 'Assinatura', href: '/billing' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-900 text-white">
      <div className="p-6">
        <h2 className="text-xl font-bold">eSocial SaaS</h2>
        <p className="text-xs text-gray-400 mt-1">Painel Administrativo</p>
      </div>
      
      <nav className="mt-6">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={`block px-6 py-3 text-sm transition-colors ${
              pathname === item.href
                ? 'bg-primary-600 text-white'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            }`}
          >
            {item.name}
          </Link>
        ))}
      </nav>
      
      <div className="absolute bottom-0 w-64 p-6 border-t border-gray-800">
        <button className="text-sm text-gray-400 hover:text-white">
          Sair do Sistema
        </button>
      </div>
    </aside>
  );
}
