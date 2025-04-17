# AI 웹앱 프로젝트

Next.js (프론트엔드) + FastAPI (백엔드) + MongoDB + Pinecone + LangChain을 사용한 AI 챗봇 애플리케이션입니다.

## 기술 스택

- **프론트엔드**: Next.js 14 (App Router)
- **백엔드**: FastAPI, LangChain
- **데이터베이스**: MongoDB (세션 및 대화 이력), Pinecone (벡터 저장소)
- **AI 모델**: OpenAI GPT-4o 사용

## 설치 및 실행 방법

1. 환경 변수 설정:
   ```bash
   cp .env.example .env
   # .env 파일에 필요한 API 키 입력
   ```

2. PDF 문서를 벡터 저장소에 업로드:
   ```bash
   docker compose run backend python app/embeddings/ingest.py
   ```

3. 전체 스택 실행:
   ```bash
   docker compose up --build
   ```

4. 접속:
   - 프론트엔드: http://localhost:3000
   - 백엔드 API 문서: http://localhost:8000/api/docs

## 디렉토리 구조

```
my-ai-webapp/
├── docker-compose.yml        # 로컬 전체 스택을 한 번에 띄움
├── .env.example              # 공통 환경변수 예시
├── README.md                 # 프로젝트 설명
├── backend/                  # Python · FastAPI · LangChain
│   ├── app/
│   │   ├── main.py           # FastAPI 엔트리포인트
│   │   ├── deps.py           # 공통 의존성(예: DB, Pinecone 클라이언트)
│   │   ├── routers/
│   │   │   ├── health.py     
│   │   │   └── chat.py       # /chat → LLM + 벡터검색
│   │   ├── chains/
│   │   │   └── qa_chain.py   # LangChain 정의
│   │   ├── embeddings/
│   │   │   └── ingest.py     # PDF·웹문서 → Pinecone 업로드 스크립트
│   │   └── models/           # Pydantic 스키마
│   └── requirements.txt
├── frontend/                 # Next.js 14(App Router)  
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── chat/             # 페이지 · 컴포넌트
│   │       ├── ChatUI.tsx
│   │       └── actions.ts    # 서버 액션 → backend 호출
│   ├── lib/api.ts            # fetch 래퍼
│   └── tsconfig.json
└── scripts/
    └── dev.sh                # VSCode Tasks 등 통합 실행 스크립트
``` 