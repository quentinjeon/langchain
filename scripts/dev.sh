#!/bin/bash

# 로컬 개발 환경 실행 스크립트
echo "🚀 AI 웹앱 개발 환경 시작..."

# .env 파일 확인
if [ ! -f .env ]; then
  echo "⚠️ .env 파일이 없습니다. .env.example 파일을 복사합니다."
  cp .env.example .env
  echo "👉 .env 파일에 API 키를 추가해주세요."
fi

# 전체 스택 실행
docker compose up --build 