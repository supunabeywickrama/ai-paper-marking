"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface ScoreChartProps {
  scores: (number | null | undefined)[];
}

const BUCKETS = [
  { label: '0–20', min: 0, max: 20 },
  { label: '21–40', min: 21, max: 40 },
  { label: '41–60', min: 41, max: 60 },
  { label: '61–80', min: 61, max: 80 },
  { label: '81–100', min: 81, max: 100 },
];

const COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6'];

export default function ScoreChart({ scores }: ScoreChartProps) {
  const data = BUCKETS.map((b, i) => ({
    label: b.label,
    count: scores.filter(s => s != null && s >= b.min && s <= b.max).length,
    color: COLORS[i],
  }));

  const total = scores.length;

  if (total === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
        No completed submissions yet.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h3 className="text-sm font-bold text-gray-600 uppercase tracking-wider mb-6">Score Distribution</h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#6b7280' }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#6b7280' }} />
          <Tooltip
            formatter={(value: number) => [`${value} student${value !== 1 ? 's' : ''}`, 'Count']}
            contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb', fontSize: 13 }}
          />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 text-right mt-2">{total} completed submission{total !== 1 ? 's' : ''}</p>
    </div>
  );
}
