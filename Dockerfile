FROM python:3.11.5-slim-bullseye

WORKDIR /app

# We need to install gcc for requirements.txt
RUN apt-get update -y &&\
    apt-get install -y build-essential

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy all files after installing requirements.txt to optimize caching
COPY src/ .

# Create a non-root user to run the app for security reasons
RUN groupadd -r app_group && \
    useradd -r -g app_group app_user && \
    chmod -R 777 /app

USER app_user

CMD ["python", "main.py"]