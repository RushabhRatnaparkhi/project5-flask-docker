# Project 5 - Flask Dockerized App

This is a fresh Flask application built to satisfy Project 5 requirements.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

## Dockerize (Requirement A)

```bash
docker build -t project5-flask-docker:latest .
docker run --rm -p 5000:5000 project5-flask-docker:latest
```

## Push image to registry (Requirement B)

Example with GitHub Container Registry:

```bash
docker tag project5-flask-docker:latest ghcr.io/<github-username>/project5-flask-docker:latest
echo <github-token> | docker login ghcr.io -u <github-username> --password-stdin
docker push ghcr.io/<github-username>/project5-flask-docker:latest
```
