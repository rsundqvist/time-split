FROM python:3.12-slim AS app

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python -
RUN /root/.local/bin/poetry config virtualenvs.create false

# Install dependencies - these don't change as often.
COPY README.md pyproject.toml poetry.lock /tmp/time-split/
RUN /root/.local/bin/poetry install \
    -C /tmp/time-split/ -E plotting --only=main \
    --no-root --no-interaction --no-cache --compile

# Install time-split package
COPY src/ /tmp/time-split/
RUN pip install /tmp/time-split/ --no-deps --no-cache --no-cache-dir && rm -rf /tmp/time-split/

# Entrypoint
CMD ["python", "-c", "import time_split; print(f'Successfully imported time_split=={time_split.__version__}!')"]
