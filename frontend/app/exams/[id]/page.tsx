"use client";
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import api from '@/utils/api';
import SubmissionTable from '@/components/SubmissionTable';
import RankingTable from '@/components/RankingTable';
import ScoreChart from '@/components/ScoreChart';
import { RefreshCw } from 'lucide-react';

type Tab = 'submissions' | 'rankings' | 'analytics';

export default function ExamDetail() {
  const { id } = useParams();
  const [exam, setExam] = useState<any>(null);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [rankings, setRankings] = useState<any[]>([]);
  const [tab, setTab] = useState<Tab>('submissions');
  const [loading, setLoading] = useState(true);
  const [generatingRankings, setGeneratingRankings] = useState(false);

  const load = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [examRes, subsRes, rankRes] = await Promise.all([
        api.get(`/exams/${id}`),
        api.get(`/exams/${id}/submissions`),
        api.get(`/rankings/${id}`)
      ]);
      setExam(examRes.data);
      setSubmissions(subsRes.data);
      setRankings(rankRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleGenerateRankings = async () => {
    setGeneratingRankings(true);
    try {
      await api.post(`/exams/${id}/generate-rankings`);
      const rankRes = await api.get(`/rankings/${id}`);
      setRankings(rankRes.data);
    } finally {
      setGeneratingRankings(false);
    }
  };

  const completedScores = submissions
    .filter(s => s.processing_status === 'COMPLETED')
    .map(s => s.total_score);

  const tabs: { key: Tab; label: string }[] = [
    { key: 'submissions', label: 'Submissions' },
    { key: 'rankings', label: 'Rankings' },
    { key: 'analytics', label: 'Analytics' },
  ];

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <Link href="/exams" className="text-blue-600 text-sm font-semibold hover:underline mb-2 inline-block">&larr; Back to Exams</Link>
        {loading ? (
          <div className="h-8 bg-gray-200 rounded-lg w-64 animate-pulse mt-1" />
        ) : (
          <>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">{exam?.title}</h1>
            <p className="text-gray-500 mt-1">{exam?.subject} &middot; Deadline: {exam?.deadline_time ? new Date(exam.deadline_time).toLocaleString() : '—'}</p>
          </>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit mb-6">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all ${
              tab === t.key ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
            {t.key === 'submissions' && !loading && (
              <span className="ml-1.5 text-xs bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded-full">{submissions.length}</span>
            )}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="h-64 bg-gray-100 rounded-2xl animate-pulse" />
      ) : (
        <>
          {tab === 'submissions' && (
            <SubmissionTable submissions={submissions} />
          )}

          {tab === 'rankings' && (
            <div className="space-y-4">
              <div className="flex justify-end">
                <button
                  onClick={handleGenerateRankings}
                  disabled={generatingRankings}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-semibold text-sm transition disabled:opacity-70"
                >
                  <RefreshCw size={16} className={generatingRankings ? 'animate-spin' : ''} />
                  {generatingRankings ? 'Generating…' : 'Generate Rankings'}
                </button>
              </div>
              <RankingTable rankings={rankings} />
            </div>
          )}

          {tab === 'analytics' && (
            <ScoreChart scores={completedScores} />
          )}
        </>
      )}
    </div>
  );
}
