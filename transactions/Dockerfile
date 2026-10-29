FROM node:22-alpine
WORKDIR /app
COPY src/package*.json ./
RUN npm ci --omit=dev
COPY --chown=node:node src/ .
USER node
EXPOSE 3000
CMD ["node", "app.js"]
