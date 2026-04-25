"use client";
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import api from '@/utils/api';
import TimeStatusBadge from '@/components/TimeStatusBadge';
import EvaluationCard from '@/components/EvaluationCard';
import { Download, FileText } from 'lucide-react';

export default function SubmissionDetail() {
  const { id } = useParams();
  const [submission, setSubmission] = useState<any>(null);
  const [exam, setExam] = useState<any>(null);
  const [evaluations, setEvaluations] = useState<any[]>([]);
  const [pdfs, setPdfs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    api.get(`/submissions/${id}`)
      .then(async subRes => {
        const sub = subRes.data;
        setSubmission(sub);
        const [examRes, evalRes, pdfRes] = await Promise.all([
          api.get(`/exams/${sub.exam_id}`),
          api.get(`/submissions/${id}/evaluations`),
          api.get(`/submissions/${id}/pdfs`),
        ]);
        setExam(examRes.data);
        setEvaluations(evalRes.data);
        setPdfs(pdfRes.data);
      })
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, [id]);

  const statusColors: Record<string, string> = {
    COMPLETED: 'text-green-700 bg-green-50',
    PROCESSING: 'text-blue-700 bg-blue-50',
    PENDING: 'text-gray-600 bg-gray-100',
    FAILED: 'text-red-700 bg-red-50',
  };

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <Link href="/exams" className="text-blue-600 text-sm font-semibold hover:underline mb-2 inline-block">
          &larr; Back to Exams
        </Link>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Submission Detail</h1>
      </div>

      {loading ? (
        <div className="space-y-4">
          <div className="h-32 bg-gray-100 rounded-2xl animate-pulse" />
          <div className="h-48 bg-gray-100 rounded-2xl animate-pulse" />
        </div>
      ) : (
        <>
          {/* Header card */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">Exam</p>
                <p className="font-semibold text-gray-900 text-sm">{exam?.title ?? '—'}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">Submitted</p>
                <p className="font-semibold text-gray-900 text-sm">
                  {submission?.submitted_at ? new Date(submission.submitted_at).toLocaleString() : '—'}
                </p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">Time Status</p>
                {submission?.time_status && <TimeStatusBadge status={submission.time_status} />}
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">Processing</p>
                <span className={`text-xs font-bold uppercase px-2 py-1 rounded-md ${statusColors[submission?.processing_status] ?? ''}`}>
                  {submission?.processing_status}
                </span>
              </div>
            </div>
            <div className="mt-6 pt-6 border-t border-gray-100 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-gray-400">Total Score</p>
                <p className="text-4xl font-black text-gray-900 mt-1">
                  {submission?.total_score != null ? submission.total_score.toFixed(1) : '—'}
                </p>
              </div>
              {pdfs.length > 0 && (
                <div className="flex gap-3">
                  {pdfs.map((pdf: any) => (
                    <a
                      key={pdf.id}
                      href={`/api/static/${pdf.file_path.split('/').pop()}`}
                      download
                      className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-50 font-semibold text-sm transition"
                    >
                      {pdf.pdf_type === 'ANNOTATED' ? <FileText size={16} className="text-blue-500" /> : <Download size={16} className="text-green-500" />}
                      {pdf.pdf_type === 'ANNOTATED' ? 'Annotated PDF' : 'Clean PDF'}
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Evaluations */}
          <h2 className="text-lg font-bold text-gray-900 mb-4">Question Breakdown</h2>
          {evaluations.length === 0 ? (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-12 text-center text-gray-500">
              No evaluation data available yet.
            </div>
          ) : (
            <div className="space-y-4">
              {evaluations.map(ev => (
                <EvaluationCard
                  key={ev.id}
                  questionNumber={ev.question_number}
                  questionPart={ev.question_part}
                  marksAwarded={ev.marks_awarded}
                  maxMarks={ev.max_marks}
                  feedback={ev.feedback}
                  evaluationType={ev.evaluation_type}
                  detailedReasoning={ev.detailed_reasoning}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
