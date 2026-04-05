FROM python:3.11
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_ml.txt .

RUN pip install --no-cache-dir -r requirements_ml.txt

RUN python -m spacy download es_core_news_sm

COPY . .

RUN echo 'from flask import Flask\napp = Flask(__name__)\n\n@app.route("/health")\ndef health():\n    return {"status": "healthy"}\n\nif __name__ == "__main__":\n    app.run(host="0.0.0.0", port=5000)' > health_server.py

EXPOSE 5000

CMD ["python", "health_server.py"]