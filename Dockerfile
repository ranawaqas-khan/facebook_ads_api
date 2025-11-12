FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Install missing Linux dependencies for Chromium
RUN playwright install-deps

# Make the start script executable
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
