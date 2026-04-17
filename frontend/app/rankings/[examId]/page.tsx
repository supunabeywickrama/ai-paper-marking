"use client";
import { useEffect, useState } from 'react';
import api from '@/utils/api';
import { useParams } from 'next/navigation';
import { Trophy, Clock, CheckCircle } from 'lucide-react';
import Link from 'next/link';

export default function Rankings() {
  const { examId } = useParams();
  const [rankings, setRankings] = useState([]);
  const [exam, setExam] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!examId) return;
    
    Promise.all([
      api.get(`/rankings/${examId}`),
      api.get(`/exams/${examId}`)
    ])
      .then(([rankRes, examRes]) => {
        setRankings(rankRes.data);
        setExam(examRes.data);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [examId]);

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <Link href="/exams" className="text-blue-600 text-sm font-semibold hover:underline mb-2 inline-block">&larr; Back to Exams</Link>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Leaderboard: {exam?.title || "Loading..."}</h1>
          <p className="text-gray-500 mt-1">Live ranking of all processed submissions for this exam.</p>
        </div>
      </div>
      
      {loading ? (
        <div className="h-64 bg-gray-100 rounded-2xl animate-pulse"></div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm w-24 text-center">Rank</th>
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm">Student ID</th>
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm text-right">Total Score</th>
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm text-center">Time Status</th>
              </tr>
            </thead>
            <tbody>
              {rankings.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-12 text-center text-gray-500">No ranked submissions yet.</td>
                </tr>
              ) : rankings.map((rank: any) => (
                <tr key={rank.id} className="border-b border-gray-50 hover:bg-blue-50/50 transition-colors">
                  <td className="py-4 px-6 font-bold text-gray-900 text-center text-lg">
                    {rank.rank === 1 ? <Trophy className="w-6 h-6 text-yellow-500 mx-auto" /> : `#${rank.rank}`}
                  </td>
                  <td className="py-4 px-6 font-medium text-gray-600 font-mono text-sm">{rank.student_id}</td>
                  <td className="py-4 px-6 text-gray-900 font-black text-right text-lg">{rank.total_score}</td>
                  <td className="py-4 px-6 text-center">
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                      rank.status === 'ON_TIME' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {rank.status === 'ON_TIME' ? <CheckCircle size={14} /> : <Clock size={14} />}
                      {rank.status.replace('_', ' ')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
