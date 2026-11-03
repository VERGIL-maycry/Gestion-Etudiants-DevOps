FROM python:3.14-slim
WORKDIR /app
COPY app ./app
RUN mkdir /app/data && chown -R 10001:10001 /app
USER 10001:10001
ENV HOST=0.0.0.0 DATABASE_PATH=/app/data/school.db PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
CMD ["python", "-m", "app.server"]
