"use client";
import { useState } from 'react';
import Link from 'next/link';
import { ArrowUpDown } from 'lucide-react';
import TimeStatusBadge from './TimeStatusBadge';

interface Submission {
  id: string;
  student_id: string;
  submitted_at: string;
  time_status: string;
  processing_status: string;
  total_score?: number | null;
  rank?: number | null;
}

type SortKey = 'submitted_at' | 'total_score' | 'processing_status';

export default function SubmissionTable({ submissions }: { submissions: Submission[] }) {
  const [sortKey, setSortKey] = useState<SortKey>('submitted_at');
  const [sortAsc, setSortAsc] = useState(false);

  const toggle = (key: SortKey) => {
    if (sortKey === key) setSortAsc(a => !a);
    else { setSortKey(key); setSortAsc(false); }
  };

  const sorted = [...submissions].sort((a, b) => {
    let av: number | string = '';
    let bv: number | string = '';
    if (sortKey === 'submitted_at') { av = a.submitted_at; bv = b.submitted_at; }
    else if (sortKey === 'total_score') { av = a.total_score ?? -1; bv = b.total_score ?? -1; }
    else { av = a.processing_status; bv = b.processing_status; }
    const cmp = av < bv ? -1 : av > bv ? 1 : 0;
    return sortAsc ? cmp : -cmp;
  });

  const statusColors: Record<string, string> = {
    COMPLETED: 'text-green-700 bg-green-50',
    PROCESSING: 'text-blue-700 bg-blue-50',
    PENDING: 'text-gray-600 bg-gray-100',
    FAILED: 'text-red-700 bg-red-50',
  };

  const SortBtn = ({ col }: { col: SortKey }) => (
    <button onClick={() => toggle(col)} className="ml-1 inline-flex">
      <ArrowUpDown size={12} className={sortKey === col ? 'text-blue-500' : 'text-gray-300'} />
    </button>
  );

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-gray-50 border-b border-gray-100">
            <th className="py-4 px-6 font-semibold text-gray-600 text-sm">Student ID</th>
            <th className="py-4 px-6 font-semibold text-gray-600 text-sm">
              Submitted <SortBtn col="submitted_at" />
            </th>
            <th className="py-4 px-6 font-semibold text-gray-600 text-sm">Time Status</th>
            <th className="py-4 px-6 font-semibold text-gray-600 text-sm">
              Status <SortBtn col="processing_status" />
            </th>
            <th className="py-4 px-6 font-semibold text-gray-600 text-sm text-right">
              Score <SortBtn col="total_score" />
            </th>
            <th className="py-4 px-6 font-semibold text-gray-600 text-sm text-right">Detail</th>
          </tr>
        </thead>
        <tbody>
          {sorted.length === 0 ? (
            <tr>
              <td colSpan={6} className="py-12 text-center text-gray-500">No submissions yet.</td>
            </tr>
          ) : sorted.map(sub => (
            <tr key={sub.id} className="border-b border-gray-50 hover:bg-blue-50/40 transition-colors">
              <td className="py-4 px-6 font-mono text-xs text-gray-600">{sub.student_id.slice(0, 8)}…</td>
              <td className="py-4 px-6 text-gray-600 text-sm">
                {new Date(sub.submitted_at).toLocaleString()}
              </td>
              <td className="py-4 px-6">
                <TimeStatusBadge status={sub.time_status} />
              </td>
              <td className="py-4 px-6">
                <span className={`text-xs font-bold uppercase px-2 py-1 rounded-md ${statusColors[sub.processing_status] ?? 'text-gray-600 bg-gray-50'}`}>
                  {sub.processing_status}
                </span>
              </td>
              <td className="py-4 px-6 text-right font-black text-gray-900">
                {sub.total_score != null ? sub.total_score.toFixed(1) : '—'}
              </td>
              <td className="py-4 px-6 text-right">
                <Link href={`/submissions/${sub.id}`} className="text-blue-600 hover:text-blue-800 font-semibold text-sm">
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
