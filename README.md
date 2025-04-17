# AI 웹앱 프로젝트

Next.js (프론트엔드) + FastAPI (백엔드) + MongoDB + Pinecone + LangChain을 사용한 AI 챗봇 애플리케이션입니다. 문서 및 지식 기반의 질의응답 서비스를 제공합니다.

## 소개

이 프로젝트는 대화형 AI 챗봇을 구현한 웹 애플리케이션으로, 사용자가 질문을 입력하면 업로드된 PDF 문서와 관련 지식을 바탕으로 정확한 응답을 제공합니다. 벡터 검색을 통해 관련 문서 조각을 찾고, LLM을 활용하여 자연스러운 답변을 생성합니다.

주요 특징:
- 문서 기반 질의응답 시스템
- 벡터 검색을 통한 정보 검색
- 세션 관리를 통한 대화 기록 유지
- 모던 웹 인터페이스 (반응형 디자인)

## 기술 스택

### 프론트엔드
- **Next.js 14**: React 기반 프레임워크 (App Router 구조 사용)
- **TailwindCSS**: 유틸리티 CSS 프레임워크
- **React**: 사용자 인터페이스 구축
- **TypeScript**: 타입 안전성 제공

### 백엔드
- **FastAPI**: 고성능 Python 웹 프레임워크
- **LangChain**: LLM 애플리케이션 개발 프레임워크
- **MongoDB**: 대화 이력 및 사용자 세션 관리
- **Pinecone**: 벡터 데이터베이스 (문서 임베딩 저장)
- **OpenAI API**: GPT-4o 모델 사용

### 인프라
- **Docker**: 컨테이너화 및 배포
- **Docker Compose**: 멀티 컨테이너 애플리케이션 구성

## 설치 및 실행 방법

### 사전 요구사항
- Docker 및 Docker Compose 설치
- OpenAI API 키 (GPT-4o 접근 가능)
- Pinecone 계정 및 API 키

### 설정 단계

1. 저장소 클론:
   ```bash
   git clone https://github.com/quentinjeon/langchain.git
   cd langchain
   ```

2. 환경 변수 설정:
   ```bash
   cp .env.example .env
   ```
   
   `.env` 파일을 편집하여 필요한 API 키 및 설정 입력:
   ```
   # OpenAI API 키
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Pinecone 설정
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENV=your_pinecone_environment
   PINECONE_INDEX=your_pinecone_index_name
   ```

3. PDF 문서 준비:
   - PDF 문서를 `backend/pdf/` 디렉토리에 넣습니다.
   - 다양한 문서를 넣을 수 있으며, 한글, 영어 등 여러 언어 지원됩니다.

4. PDF 문서를 벡터 저장소에 업로드 (최초 1회):
   ```bash
   docker compose run backend python app/embeddings/ingest.py
   ```
   이 과정은 문서를 읽고, 텍스트를 추출하여 임베딩하고, Pinecone에 저장합니다.

5. 전체 스택 실행:
   ```bash
   docker compose up --build
   ```
   
   개별 서비스 실행도 가능합니다:
   ```bash
   # 데이터베이스만 실행
   docker compose up mongo
   
   # 백엔드만 실행
   docker compose up backend
   
   # 프론트엔드만 실행
   docker compose up frontend
   ```

6. 애플리케이션 접속:
   - 프론트엔드: http://localhost:3000
   - 백엔드 API 문서: http://localhost:8000/api/docs

### Windows PowerShell에서 실행 시 참고사항

Windows PowerShell에서는 `&&` 연산자가 작동하지 않을 수 있습니다. 이 경우 명령어를 개별적으로 실행하세요:

```powershell
cd my-ai-webapp
docker compose up --build
```

## 주요 기능

### 채팅 인터페이스
- 사용자 친화적인 채팅 UI (이전 메시지 표시)
- 메시지 입력 및 전송 기능
- 세션 관리를 통한 대화 기록 유지

### 벡터 검색 기반 질의응답
- 업로드된 문서에서 관련 정보 검색
- 유사도 기반 검색을 통한 정확한 컨텍스트 검색
- LLM을 활용한 자연스러운 답변 생성

### API 기능
- `/api/chat`: 질문을 받고 답변 생성 (POST)
- `/api/health`: 서비스 상태 확인 (GET)

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
│   ├── pdf/                  # 분석할 PDF 문서 저장 위치
│   └── requirements.txt
├── frontend/                 # Next.js 14(App Router)  
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── chat/             # 채팅 페이지 · 컴포넌트
│   │       ├── page.tsx      # 채팅 페이지
│   │       ├── ChatUI.tsx    # 채팅 UI 컴포넌트
│   │       └── actions.ts    # 서버 액션 → backend 호출
│   ├── lib/
│   │   └── api.ts            # fetch 래퍼
│   ├── pages/                # Pages Router (레거시)
│   ├── Dockerfile            # 프론트엔드 Docker 이미지 설정
│   ├── next.config.js        # Next.js 설정
│   ├── tailwind.config.js    # TailwindCSS 설정
│   ├── package.json          # 종속성 정의
│   └── tsconfig.json         # TypeScript 설정
└── scripts/
    └── dev.sh                # VSCode Tasks 등 통합 실행 스크립트
```

## 개발 가이드

### 백엔드 개발

새로운 API 엔드포인트 추가 방법:
1. `backend/app/routers/` 디렉토리에 새 라우터 파일 생성
2. 새 라우터를 `backend/app/main.py`에 등록

예시:
```python
# backend/app/routers/new_feature.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/new-feature", tags=["new-feature"])

@router.get("/")
async def get_new_feature():
    return {"message": "New feature response"}
```

```python
# backend/app/main.py에 추가
from app.routers import new_feature

app.include_router(new_feature.router)
```

### 프론트엔드 개발

새로운 페이지 추가 방법:
1. App Router: `frontend/app/<페이지-경로>/page.tsx` 생성
2. 필요한 컴포넌트 추가: `frontend/app/<페이지-경로>/components/`

예시:
```tsx
// frontend/app/new-feature/page.tsx
export default function NewFeaturePage() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">새 기능</h1>
      <p>새 기능 페이지입니다.</p>
    </main>
  );
}
```

## 문제 해결 가이드

### 일반적인 문제

1. **Docker 컨테이너가 시작되지 않는 경우**
   ```bash
   # 로그 확인
   docker compose logs
   
   # 특정 서비스 로그 확인
   docker compose logs frontend
   docker compose logs backend
   ```

2. **프론트엔드 빌드 오류**
   
   TailwindCSS 관련 오류가 발생하는 경우:
   ```bash
   # 프론트엔드 디렉토리에서
   npm uninstall tailwindcss
   npm install tailwindcss@3.4.5
   
   # Docker 재빌드
   docker compose build --no-cache frontend
   ```

3. **"Cannot find module './lib/setupTrackingContext'" 오류**
   
   TailwindCSS 버전 이슈입니다. 버전을 3.4.5로 고정하여 해결할 수 있습니다.

4. **"stream did not contain valid UTF-8" 오류**
   
   파일 인코딩 문제입니다. 텍스트 파일을 UTF-8로 저장해야 합니다:
   ```powershell
   # PowerShell에서
   Get-Content -Path file.ts | Out-File -FilePath file.ts -Encoding utf8
   ```

5. **백엔드 연결 오류 (ECONNREFUSED)**
   
   백엔드 서비스가 실행 중인지 확인하고, 환경 변수 설정을 확인하세요:
   ```
   # .env 파일의 API URL 확인
   NEXT_PUBLIC_API=http://backend:8000/api
   ```

6. **라우팅 충돌 오류**
   
   Next.js App Router와 Pages Router가 충돌하는 경우:
   - `pages/` 디렉토리와 `app/` 디렉토리에 동일한 경로의 페이지가 있는지 확인
   - 중복되는 경로가 있다면 한 쪽을 제거하세요 (App Router 우선 권장)

### 컨테이너 관련 문제

1. **Windows에서 Docker 실행 오류**
   
   Windows에서는 파일 경로와 PowerShell 문법에 주의해야 합니다:
   ```powershell
   # 절대 경로 사용
   cd C:\path\to\my-ai-webapp
   docker compose up
   ```

2. **도커 캐시 문제**
   
   캐시로 인한 문제가 발생할 경우 캐시 없이 빌드:
   ```bash
   docker compose build --no-cache
   docker compose up
   ```

## API 문서

백엔드 API 문서는 Swagger UI를 통해 제공됩니다: http://localhost:8000/api/docs

### 주요 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 | 요청 바디 | 응답 |
|------------|--------|------|-----------|------|
| `/api/chat` | POST | 질문에 대한 답변 생성 | `{"session_id": "string", "message": "string"}` | `{"answer": "string"}` |
| `/api/health` | GET | 서비스 상태 확인 | - | `{"status": "ok"}` |

## 기여 방법

이 프로젝트에 기여하고 싶으시다면:

1. 이슈 생성 또는 기존 이슈 확인
2. 저장소 포크
3. 기능 개발 브랜치 생성
4. 변경사항 커밋
5. Pull Request 제출

## 라이선스

MIT License

## 연락처

문의사항이 있으시면 이슈를 생성하거나 다음 연락처로 문의하세요:
- GitHub: [@quentinjeon](https://github.com/quentinjeon)