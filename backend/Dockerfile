FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app

# PDF 디렉토리 생성
RUN mkdir -p pdf

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 