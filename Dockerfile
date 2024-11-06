FROM python:3.9-slim

# Copy application files
COPY . /app
WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8040

# Command to run the application
CMD ["python", "app.py"]

