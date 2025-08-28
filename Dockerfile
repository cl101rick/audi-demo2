# Use a base image with Java and Python
FROM adoptopenjdk/openjdk17:alpine as base

# Install Python and other build tools
RUN apk add --no-cache python3 py3-pip

# Install required Audiveris dependencies (adjust based on Audiveris version)
RUN apk add --no-cache leptonica-dev tesseract-ocr-dev

# Set up Audiveris
WORKDIR /audiveris
# Download and unzip the Audiveris executable (adjust version as needed)
RUN wget https://github.com/Audiveris/audiveris/releases/download/v5.3.0/Audiveris-5.3.0.jar -O Audiveris.jar

# Set up Flask application
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

# Expose the port for the Flask app
EXPOSE 8000

# Run the Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
