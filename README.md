# ImageKit Upload & Auth with FastAPI

A full-stack Python web application that integrates **ImageKit.io** for image uploading and management, complete with user authentication. The backend is built with FastAPI, and the project is configured for easy deployment on Render.

## Features

*   **Image Management:** Seamless image uploading and serving using the ImageKit API.
*   **Authentication:** Secure user authentication integrated into the FastAPI backend.
*   **Timezone-Aware:** Robust handling of timezone-aware datetimes for database models (e.g., Post models).
*   **Modern Python Tooling:** Managed via `pyproject.toml` and `uv` for fast dependency resolution.
*   **Deployment Ready:** Pre-configured for deployment on platforms like Render.

## Project Structure

*   `main.py`: The main entry point for the FastAPI backend application.
*   `app/` / `src/fastapi/`: Core backend logic, routing, auth, and database models.
*   `frontend.py`: The frontend application interface.
*   `requirements.txt` / `pyproject.toml` / `uv.lock`: Project dependencies and package configurations.

## Prerequisites

Before running the project locally, ensure you have the following installed:
*   Python 3.x (check `.python-version` for exact version)
*   `pip` or `uv` (recommended for faster package management)
*   An [ImageKit.io](https://imagekit.io/) account and API credentials.

## Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Winminoo17/uploading_in_imagekitio.git](https://github.com/Winminoo17/uploading_in_imagekitio.git)
   cd uploading_in_imagekitio
