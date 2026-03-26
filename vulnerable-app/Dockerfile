# 🔴 INTENTIONALLY VULNERABLE Dockerfile
# Contains security misconfigurations for testing

# 🔴 VULN: Using latest tag (unpinned)
FROM python:3.11

# 🔴 VULN: Running as root (CWE-250)
# Should use: USER nonroot

WORKDIR /app

# 🔴 VULN: Copying everything including secrets
COPY . .

# 🔴 VULN: No .dockerignore, may include .env, .git, etc.
RUN pip install --no-cache-dir -r requirements.txt

# 🔴 VULN: Exposing debug port
EXPOSE 5000

# 🔴 VULN: Environment variables with secrets
ENV FLASK_DEBUG=1
ENV DATABASE_URL="postgresql://admin:P@ssw0rd123@db:5432/app"
ENV SECRET_KEY="hardcoded-docker-secret-key"

# 🔴 VULN: Running with debug mode
CMD ["python", "src/app.py"]
