import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI 웹앱',
  description: 'Next.js + FastAPI + LangChain으로 만든 AI 챗봇',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <main className="min-h-screen bg-gray-50">
          <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
            <header className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">AI 웹앱</h1>
              <p className="text-gray-600">LangChain + RAG 기반 질의응답 시스템</p>
            </header>
            {children}
          </div>
        </main>
      </body>
    </html>
  );
} 