"use client";
import { useState, useEffect } from 'react';
import api from '@/utils/api';
import { Upload as UploadIcon, CheckCircle, AlertCircle } from 'lucide-react';

export default function UploadPaper() {
  const [exams, setExams] = useState([]);
  const [examId, setExamId] = useState('');
  const [studentId, setStudentId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.get('/exams').then(res => setExams(res.data));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !examId || !studentId) return;
    
    setStatus('uploading');
    const formData = new FormData();
    formData.append('exam_id', examId);
    formData.append('student_id', studentId);
    formData.append('file', file);
    
    try {
      await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus('success');
      setMessage('Paper uploaded successfully! It is now being processed by the AI.');
      setFile(null);
    } catch (err: any) {
      setStatus('error');
      setMessage(err.response?.data?.detail || 'An error occurred during upload.');
    }
  };

  return (
    <div className="max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Upload Answer Sheet</h1>
        <p className="text-gray-500 mt-2">Submit your handwritten or printed exam paper for automatic grading.</p>
      </div>

      <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
        {status === 'success' ? (
          <div className="text-center py-10 animate-in zoom-in duration-300">
            <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Complete</h2>
            <p className="text-gray-500 mb-8 max-w-md mx-auto">{message}</p>
            <button onClick={() => setStatus('idle')} className="text-blue-600 font-semibold hover:text-blue-800 transition-colors">
              Upload Another Paper
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {status === 'error' && (
              <div className="bg-red-50 text-red-700 p-4 rounded-xl flex items-start gap-3 text-sm border border-red-100">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <p className="font-medium">{message}</p>
              </div>
            )}
            
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Select Exam</label>
                <select 
                  className="w-full bg-gray-50 border border-gray-200 text-gray-900 text-sm rounded-xl focus:ring-blue-500 focus:border-blue-500 block p-3.5 outline-none transition-all"
                  value={examId}
                  onChange={e => setExamId(e.target.value)}
                  required
                >
                  <option value="" disabled>Choose an exam...</option>
                  {exams.map((ex: any) => (
                    <option key={ex.id} value={ex.id}>{ex.title} ({ex.subject})</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Student ID (UUID)</label>
                <input 
                  type="text" 
                  className="w-full bg-gray-50 border border-gray-200 text-gray-900 text-sm rounded-xl focus:ring-blue-500 focus:border-blue-500 block p-3.5 outline-none transition-all" 
                  placeholder="Enter your system Student UUID" 
                  value={studentId}
                  onChange={e => setStudentId(e.target.value)}
                  required 
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Upload File (PDF, PNG, JPG)</label>
                <label className="flex flex-col items-center justify-center w-full h-56 border-2 border-gray-300 border-dashed rounded-xl cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors group">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <UploadIcon className="w-12 h-12 mb-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    <p className="mb-2 text-sm text-gray-600 font-medium text-center px-4">
                      {file ? <span className="text-blue-600 text-base">{file.name}</span> : <span>Click to upload or drag and drop</span>}
                    </p>
                    <p className="text-xs text-gray-400 font-medium uppercase tracking-wider mt-2">PDF, PNG, or JPG (MAX. 10MB)</p>
                  </div>
                  <input type="file" className="hidden" onChange={e => setFile(e.target.files?.[0] || null)} accept=".pdf,.png,.jpg,.jpeg" required />
                </label>
              </div>
            </div>
            
            <button 
              type="submit" 
              disabled={status === 'uploading' || !file || !examId || !studentId}
              className="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 font-bold tracking-wide rounded-xl text-sm px-5 py-4 text-center transition-all disabled:opacity-70 disabled:cursor-not-allowed shadow-sm"
            >
              {status === 'uploading' ? 'UPLOADING...' : 'SUBMIT PAPER'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
