import Link from 'next/link';
import { Home, FileText, Upload, Settings } from 'lucide-react';

export default function Sidebar() {
  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full flex flex-col shadow-sm">
      <div className="p-6">
        <h1 className="text-2xl font-black tracking-tight text-blue-600">AI MARKER</h1>
        <p className="text-xs text-gray-400 font-medium tracking-wider uppercase mt-1">Intelligence System</p>
      </div>
      <nav className="flex-1 px-4 py-4 space-y-2">
        <Link href="/" className="flex items-center gap-3 px-3 py-2.5 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-700 transition-colors font-medium">
          <Home size={18} /> Dashboard
        </Link>
        <Link href="/exams" className="flex items-center gap-3 px-3 py-2.5 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-700 transition-colors font-medium">
          <FileText size={18} /> Exams
        </Link>
        <Link href="/upload" className="flex items-center gap-3 px-3 py-2.5 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-700 transition-colors font-medium">
          <Upload size={18} /> Upload Paper
        </Link>
      </nav>
      <div className="p-4 border-t border-gray-100">
        <Link href="/settings" className="flex items-center gap-3 px-3 py-2.5 text-gray-500 rounded-lg hover:bg-gray-50 transition-colors font-medium text-sm">
          <Settings size={18} /> Settings
        </Link>
      </div>
    </div>
  );
}
