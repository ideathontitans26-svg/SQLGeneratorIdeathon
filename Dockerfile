# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/ .
RUN npm ci && npm run build

# Stage 2: Backend + serve frontend
FROM python:3.12-slim
WORKDIR /app

# Copy backend
COPY backend/ backend/

# Copy built frontend from stage 1
COPY --from=frontend-build /app/dist /app/frontend/dist

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Render sets PORT at runtime; default for local runs
# Use 8081 as the default port inside the container to match your local setup.
ENV PORT=8081
EXPOSE 8081

# Use shell form so $PORT is expanded; Render injects PORT when deploying
CMD ["/bin/sh", "-c", "cd backend && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8081}"]
