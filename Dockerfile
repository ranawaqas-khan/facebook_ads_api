FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x start.sh

EXPOSE 8000
CMD ["./start.sh"]
