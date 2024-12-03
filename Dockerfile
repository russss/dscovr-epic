FROM ghcr.io/astral-sh/uv:python3.12-alpine
RUN apk add libxml2 libxslt imagemagick
RUN apk add --no-cache gcc musl-dev libffi-dev libxml2-dev libxslt-dev
WORKDIR /app
COPY . /app
RUN uv sync
ENTRYPOINT ["uv", "run", "python", "./tweet_updates.py"]
