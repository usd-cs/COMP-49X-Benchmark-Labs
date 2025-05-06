FROM python:3.9-slim

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/run_model.py .
COPY Notebook/model.knn ./Notebook/model.knn
COPY website ./website

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run_model:app"]