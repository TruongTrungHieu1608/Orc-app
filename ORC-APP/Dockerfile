FROM python:3.10-slim

# Cài Tesseract + ngôn ngữ OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    tesseract-ocr-eng \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy code vào container
WORKDIR /app
COPY . .

# Cài Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Run script khi container khởi động
CMD ["python", "app.py"]