'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';

interface Report {
  id: string;
  topic: string;
  content: string;
  createdAt: string;
}

export default function ReportDetail() {
  const params = useParams();
  const id = params?.id as string;
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API}/report/${id}`);
        
        if (!response.ok) {
          throw new Error('보고서를 불러오는데 실패했습니다');
        }
        
        const data = await response.json();
        setReport(data);
      } catch (err) {
        console.error(err);
        setError('보고서를 불러오는 중 오류가 발생했습니다');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchReport();
    }
  }, [id]);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">로딩중...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center h-screen text-red-500">{error}</div>;
  }

  if (!report) {
    return <div className="flex justify-center items-center h-screen">보고서를 찾을 수 없습니다</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
        <h1 className="text-2xl font-bold mb-2">{report.topic}</h1>
        <p className="text-gray-500 mb-6">생성일: {new Date(report.createdAt).toLocaleDateString()}</p>
        
        <div className="prose max-w-none mb-8" dangerouslySetInnerHTML={{ __html: report.content }} />
        
        <div className="flex gap-4">
          <button
            onClick={handlePrint}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
          >
            인쇄하기
          </button>
          <button
            onClick={() => window.history.back()}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
          >
            뒤로가기
          </button>
        </div>
      </div>
    </div>
  );
} 