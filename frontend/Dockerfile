FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --include=dev
RUN npm cache clean --force
RUN npm install -g next

# 중요: 필요한 파일만 복사하여 중첩 문제 방지
COPY ./lib ./lib
COPY ./pages ./pages
COPY ./app ./app
COPY next.config.js .
COPY tailwind.config.js .
COPY postcss.config.js .
COPY tsconfig.json .
COPY next-env.d.ts .
COPY .gitattributes .

EXPOSE 3000

CMD ["npm", "run", "dev"] 