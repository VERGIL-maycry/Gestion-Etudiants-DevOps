FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    STUDENT_DB=/app/data/etudiants.db

WORKDIR /app
RUN groupadd --system scolarite && useradd --system --gid scolarite scolarite \
    && mkdir /app/data && chown scolarite:scolarite /app/data
COPY app.py style.css ./
USER scolarite
EXPOSE 8000
CMD ["python", "app.py"]
