# Use the same Playwright version as installed via pip
FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure script is executable
RUN chmod +x start.sh

EXPOSE 8000

# Launch app
CMD ["./start.sh"]
