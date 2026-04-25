"use client";
import { useState } from 'react';
import api from '@/utils/api';
import { X, Upload } from 'lucide-react';

interface ExamFormProps {
  onClose: () => void;
  onCreated: () => void;
}

export default function ExamForm({ onClose, onCreated }: ExamFormProps) {
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('');
  const [maxQuestions, setMaxQuestions] = useState(10);
  const [deadline, setDeadline] = useState('');
  const [lateDeadline, setLateDeadline] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) { setError('Please upload a marking scheme PDF.'); return; }

    setLoading(true);
    setError('');
    const fd = new FormData();
    fd.append('title', title);
    fd.append('subject', subject);
    fd.append('max_questions', String(maxQuestions));
    fd.append('deadline_time', new Date(deadline).toISOString());
    fd.append('late_deadline', new Date(lateDeadline).toISOString());
    fd.append('file', file);

    try {
      await api.post('/exams', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      onCreated();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create exam.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg animate-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="text-xl font-bold text-gray-900">Create New Exam</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm p-3 rounded-xl border border-red-100">{error}</div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Title</label>
              <input
                className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 text-sm outline-none focus:border-blue-500 transition"
                value={title} onChange={e => setTitle(e.target.value)} required placeholder="e.g. Mathematics Final 2025"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Subject</label>
              <input
                className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 text-sm outline-none focus:border-blue-500 transition"
                value={subject} onChange={e => setSubject(e.target.value)} required placeholder="e.g. Mathematics"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Max Questions</label>
              <input
                type="number" min={1}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 text-sm outline-none focus:border-blue-500 transition"
                value={maxQuestions} onChange={e => setMaxQuestions(Number(e.target.value))} required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Deadline</label>
              <input
                type="datetime-local"
                className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 text-sm outline-none focus:border-blue-500 transition"
                value={deadline} onChange={e => setDeadline(e.target.value)} required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Late Deadline</label>
              <input
                type="datetime-local"
                className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 text-sm outline-none focus:border-blue-500 transition"
                value={lateDeadline} onChange={e => setLateDeadline(e.target.value)} required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">Marking Scheme (PDF)</label>
            <label className="flex items-center gap-3 w-full border-2 border-dashed border-gray-300 rounded-xl p-4 cursor-pointer hover:border-blue-400 transition-colors bg-gray-50 group">
              <Upload size={20} className="text-gray-400 group-hover:text-blue-500 transition-colors shrink-0" />
              <span className="text-sm text-gray-500">
                {file ? <span className="text-blue-600 font-medium">{file.name}</span> : 'Click to upload PDF marking scheme'}
              </span>
              <input type="file" className="hidden" accept=".pdf" onChange={e => setFile(e.target.files?.[0] || null)} />
            </label>
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 text-gray-700 font-semibold text-sm hover:bg-gray-50 transition">
              Cancel
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 px-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm transition disabled:opacity-70">
              {loading ? 'Creating...' : 'Create Exam'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
