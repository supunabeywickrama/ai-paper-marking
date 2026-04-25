import { Trophy } from 'lucide-react';
import TimeStatusBadge from './TimeStatusBadge';

interface Ranking {
  id: string;
  student_id: string;
  total_score: number;
  rank: number;
  status: string;
}

export default function RankingTable({ rankings }: { rankings: Ranking[] }) {
  return (
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
              <td colSpan={4} className="py-12 text-center text-gray-500">No rankings yet. Click "Generate Rankings" to compute them.</td>
            </tr>
          ) : rankings.map(rank => (
            <tr key={rank.id} className="border-b border-gray-50 hover:bg-blue-50/50 transition-colors">
              <td className="py-4 px-6 font-bold text-gray-900 text-center text-lg">
                {rank.rank === 1 ? <Trophy className="w-6 h-6 text-yellow-500 mx-auto" /> : `#${rank.rank}`}
              </td>
              <td className="py-4 px-6 font-medium text-gray-600 font-mono text-sm">{rank.student_id}</td>
              <td className="py-4 px-6 text-gray-900 font-black text-right text-lg">{rank.total_score.toFixed(1)}</td>
              <td className="py-4 px-6 text-center">
                <TimeStatusBadge status={rank.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
