# Flux Backend

This repository contains the FastAPI backend for the Flux character‑generation demo. It handles authentication, prompt construction, and routing requests to the GPU worker endpoint.

## Features
- FastAPI application with modular routing
- Password‑protected access
- Prompt assembly and validation
- Worker endpoint forwarding

## Running Locally
pip install -r requirements.txt
uvicorn server:app --reload

## Deployment
Designed for containerized deployment on Render using the included Dockerfile.
