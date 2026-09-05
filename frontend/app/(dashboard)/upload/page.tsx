'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';

export default function UploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFiles([...files, ...Array.from(e.dataTransfer.files)]);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Upload XML eSocial</h1>
        
        <div
          className={`rounded-lg border-2 border-dashed p-12 text-center ${
            dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <p className="text-xl text-gray-600">Arraste arquivos XML aqui</p>
          <p className="mt-2 text-sm text-gray-500">ou clique para selecionar</p>
        </div>

        {files.length > 0 && (
          <div className="mt-6 rounded-lg bg-white p-4 shadow">
            <h3 className="mb-3 font-semibold">Arquivos selecionados:</h3>
            <ul className="space-y-2">
              {files.map((file, idx) => (
                <li key={idx} className="flex items-center justify-between rounded bg-gray-50 p-2">
                  <span className="text-sm">{file.name}</span>
                  <span className="text-xs text-gray-500">{(file.size / 1024).toFixed(2)} KB</span>
                </li>
              ))}
            </ul>
            <button className="mt-4 w-full rounded bg-primary-600 py-2 text-white hover:bg-primary-700">
              Processar Arquivos
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
