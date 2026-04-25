"use client";
import { useEffect, useState } from 'react';
import api from '@/utils/api';
import Link from 'next/link';
import ExamForm from '@/components/ExamForm';

export default function ExamsList() {
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const load = () => {
    setLoading(true);
    api.get('/exams')
      .then(res => setExams(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Exams</h1>
          <p className="text-gray-500 mt-1">Manage exam templates and marking schemes.</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-sm shadow-blue-200"
        >
          Create New Exam
        </button>
      </div>

      {showForm && (
        <ExamForm
          onClose={() => setShowForm(false)}
          onCreated={() => { setShowForm(false); load(); }}
        />
      )}

      {loading ? (
        <div className="animate-pulse flex flex-col gap-4">
          <div className="h-16 bg-gray-200 rounded-xl w-full"></div>
          <div className="h-16 bg-gray-200 rounded-xl w-full"></div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm">Title</th>
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm">Subject</th>
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm">Questions</th>
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm">Deadline</th>
                <th className="py-4 px-6 font-semibold text-gray-600 text-sm text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {exams.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-gray-500">No exams found. Create one to get started!</td>
                </tr>
              ) : exams.map((exam: any) => (
                <tr key={exam.id} className="border-b border-gray-50 hover:bg-gray-50/80 transition-colors">
                  <td className="py-4 px-6 font-bold text-gray-900">
                    <Link href={`/exams/${exam.id}`} className="hover:text-blue-600 transition-colors">{exam.title}</Link>
                  </td>
                  <td className="py-4 px-6 text-gray-600">{exam.subject}</td>
                  <td className="py-4 px-6 text-gray-600 font-mono text-sm">{exam.max_questions}</td>
                  <td className="py-4 px-6 text-gray-600">{new Date(exam.deadline_time).toLocaleDateString()}</td>
                  <td className="py-4 px-6 text-right flex items-center justify-end gap-4">
                    <Link href={`/exams/${exam.id}`} className="text-blue-600 hover:text-blue-800 font-semibold text-sm">
                      Manage
                    </Link>
                    <Link href={`/rankings/${exam.id}`} className="text-gray-500 hover:text-gray-800 font-semibold text-sm">
                      Leaderboard
                    </Link>
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
