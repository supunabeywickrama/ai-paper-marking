import { CheckCircle, XCircle } from 'lucide-react';

interface DetailedReasoning {
  key_points_covered?: string[];
  key_points_missed?: string[];
  accuracy?: string;
}

interface EvaluationCardProps {
  questionNumber: number;
  questionPart?: string | null;
  marksAwarded: number;
  maxMarks: number;
  feedback?: string | null;
  evaluationType: string;
  detailedReasoning?: DetailedReasoning | null;
}

export default function EvaluationCard({
  questionNumber,
  questionPart,
  marksAwarded,
  maxMarks,
  feedback,
  evaluationType,
  detailedReasoning,
}: EvaluationCardProps) {
  const label = `Q${questionNumber}${questionPart || ''}`;
  const pct = maxMarks > 0 ? (marksAwarded / maxMarks) * 100 : 0;
  const scoreColor = pct >= 70 ? 'text-green-600' : pct >= 40 ? 'text-amber-600' : 'text-red-600';
  const barColor = pct >= 70 ? 'bg-green-500' : pct >= 40 ? 'bg-amber-500' : 'bg-red-500';

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-gray-400">{evaluationType}</span>
          <h3 className="text-xl font-black text-gray-900 mt-0.5">{label}</h3>
        </div>
        <div className="text-right">
          <span className={`text-3xl font-black ${scoreColor}`}>{marksAwarded}</span>
          <span className="text-gray-400 text-lg font-medium">/{maxMarks}</span>
        </div>
      </div>

      <div className="h-2 bg-gray-100 rounded-full mb-4 overflow-hidden">
        <div className={`h-full rounded-full transition-all ${barColor}`} style={{ width: `${pct}%` }} />
      </div>

      {feedback && (
        <p className="text-sm text-gray-600 mb-4 leading-relaxed">{feedback}</p>
      )}

      {detailedReasoning && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
          {(detailedReasoning.key_points_covered ?? []).length > 0 && (
            <div>
              <p className="text-xs font-bold text-green-700 uppercase tracking-wider mb-2">Covered</p>
              <ul className="space-y-1">
                {detailedReasoning.key_points_covered!.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <CheckCircle size={14} className="text-green-500 mt-0.5 shrink-0" />
                    {pt}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {(detailedReasoning.key_points_missed ?? []).length > 0 && (
            <div>
              <p className="text-xs font-bold text-red-700 uppercase tracking-wider mb-2">Missed</p>
              <ul className="space-y-1">
                {detailedReasoning.key_points_missed!.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <XCircle size={14} className="text-red-400 mt-0.5 shrink-0" />
                    {pt}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
