# Use a lightweight Python image for compatibility
FROM --platform=linux/amd64 python:3.10

WORKDIR /app

# Copy the processing script
COPY solution1A.py .

# Installing dependencies
RUN pip install --no-cache-dir pymupdf pdftitle

# Run the script
CMD ["python", "solution1A.py"]
