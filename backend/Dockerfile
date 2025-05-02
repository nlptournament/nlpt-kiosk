FROM python:3.10-alpine

LABEL org.opencontainers.image.authors="Nils Ost"

ENV HOME=/app

WORKDIR $HOME

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000/tcp 8765/tcp

ENTRYPOINT ["python3"]
CMD ["main.py"]
