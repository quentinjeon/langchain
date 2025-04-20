'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ReportPage() {
  const [topic, setTopic] = useState('');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('주제를 입력해주세요');
      return;
    }

    setGenerating(true);
    setError('');

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API}/report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error('보고서 생성에 실패했습니다');
      }

      const data = await response.json();
      router.push(`/report/${data.reportId}`);
    } catch (err) {
      console.error(err);
      setError('보고서 생성 중 오류가 발생했습니다');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="container mx-auto max-w-4xl p-4">
      <h1 className="text-2xl font-bold mb-6">AI 보고서 생성</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <p className="mb-4">
          업로드된 문서를 기반으로 특정 주제에 대한 보고서를 자동으로 생성합니다.
        </p>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="topic" className="block text-sm font-medium mb-1">
              보고서 주제
            </label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="예: 기후 변화의 경제적 영향"
            />
          </div>
          
          {error && (
            <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            disabled={generating}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {generating ? '생성 중...' : '보고서 생성하기'}
          </button>
        </form>
      </div>
    </div>
  );
} 