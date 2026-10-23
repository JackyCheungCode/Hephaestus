FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8787
CMD ["sh","-c","npm run d1:local && npm run dev:worker"]
