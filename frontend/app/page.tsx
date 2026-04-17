"use client";
import { useEffect, useState } from 'react';
import StatsCard from '@/components/StatsCard';
import api from '@/utils/api';
import { ArrowRight, Clock, CheckCircle2, XCircle } from 'lucide-react';
import Link from 'next/link';

interface DashboardStats {
  total_submissions: number;
  avg_score: number;
  pending_count: number;
  completed_count: number;
  on_time_count: number;
  late_count: number;
  rejected_count: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/dashboard/stats')
      .then(res => setStats(res.data))
      .catch(err => console.error("Error fetching stats:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Dashboard Overview</h1>
          <p className="text-gray-500 mt-1">Real-time marking analytics and submission status.</p>
        </div>
        <Link href="/upload" className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-sm shadow-blue-200">
          Upload New Paper
        </Link>
      </div>
      
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm h-32 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard title="Total Submissions" value={stats?.total_submissions || 0} />
          <StatsCard title="Avg AI Score" value={`${stats?.avg_score || 0}%`} description="Across all graded papers" />
          <StatsCard title="Pending Review" value={stats?.pending_count || 0} description="Currently processing" />
          <StatsCard title="Completed" value={stats?.completed_count || 0} />
        </div>
      )}

      <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
        <h2 className="text-lg font-bold mb-6 text-gray-900">Time & Status Analytics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex items-center gap-4 p-4 rounded-xl bg-green-50/50 border border-green-100">
            <div className="p-3 bg-green-100 text-green-600 rounded-lg">
              <CheckCircle2 size={24} />
            </div>
            <div>
              <p className="text-gray-500 text-sm font-medium">On Time</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.on_time_count || 0}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4 p-4 rounded-xl bg-amber-50/50 border border-amber-100">
            <div className="p-3 bg-amber-100 text-amber-600 rounded-lg">
              <Clock size={24} />
            </div>
            <div>
              <p className="text-gray-500 text-sm font-medium">Late (Accepted)</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.late_count || 0}</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-xl bg-red-50/50 border border-red-100">
            <div className="p-3 bg-red-100 text-red-600 rounded-lg">
              <XCircle size={24} />
            </div>
            <div>
              <p className="text-gray-500 text-sm font-medium">Rejected</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.rejected_count || 0}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
