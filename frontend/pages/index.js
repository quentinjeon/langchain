import Link from 'next/link';

export default function Home() {
  return (
    <div className="py-10">
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
          Next.js + FastAPI + LangChain + MongoDB + Pinecone
        </h2>
        <p className="mt-4 text-lg text-gray-500">
          사용자 질문에 대해 PDF 문서 기반 지식을 활용한 AI 응답을 제공합니다.
        </p>
        <div className="mt-8">
          <Link 
            href="/chat" 
            className="px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            채팅 시작하기
          </Link>
        </div>
      </div>
    </div>
  );
} 