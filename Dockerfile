FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# SECURITY: In production, mount media storage outside the container and serve it securely (not via static web server)
