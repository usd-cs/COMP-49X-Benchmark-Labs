FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/run_model.py .
COPY Notebook/model.knn ./Notebook/model.knn

EXPOSE 8000

CMD ["uvicorn", "run_model:app", "--host", "0.0.0.0", "--port", "8000"]