FROM russss/polybot:latest
RUN apk add libxml2 libxslt imagemagick
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev libxml2-dev libxslt-dev && \
	pip install lxml && \
	apk del .build-deps
WORKDIR /app
COPY . /app
ENTRYPOINT ["python", "./tweet_updates.py"]
