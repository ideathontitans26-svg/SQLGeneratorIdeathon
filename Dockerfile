# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Backend + serve frontend
FROM python:3.12-slim
WORKDIR /app

# Copy backend
COPY backend/ backend/

# Copy built frontend from stage 1
COPY --from=frontend-build /app/dist /app/frontend/dist

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Render sets PORT
ENV PORT=8000
EXPOSE $PORT

CMD cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
