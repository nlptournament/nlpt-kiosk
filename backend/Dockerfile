FROM python:3.10-alpine

LABEL org.opencontainers.image.authors="Nils Ost"

ENV HOME=/app

WORKDIR $HOME

COPY requirements.txt ./
RUN apk add --no-cache --virtual build-dependencies git build-base && pip3 install -r requirements.txt && apk del build-dependencies

COPY . .

EXPOSE 8000/tcp 8765/tcp

ENTRYPOINT ["python3"]
CMD ["main.py"]
