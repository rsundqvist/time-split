FROM python:3.12-slim AS app

#  ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=1
ENV STREAMLIT_SERVER_HEADLESS=1
ENV STREAMLIT_SERVER_WATCHER_TYPE=none

WORKDIR /app

COPY src/ README.md pyproject.toml ./project/
RUN pip install ./project[streamlit] && rm -rf ./project/

COPY src/time_split/streamlit/app.py app.py

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
