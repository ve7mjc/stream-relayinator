# Use the official Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY src/app.py .
# COPY config.yaml .

# Expose the UDP port used for forwarding (replace 12346 with the actual port)
# EXPOSE 12346/udp

# Set the environment variables (optional, you can use a YAML file or command-line arguments)
# ENV TCP_HOST tcp.example.com
# ENV TCP_PORT 12345
# ENV UDP_HOST udp.example.com
# ENV UDP_PORT 12346

# Run the application
CMD ["python", "app.py"]
