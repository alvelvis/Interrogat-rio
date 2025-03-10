FROM python:3.9-slim

WORKDIR /app

# Install required packages for downloading and unzipping
RUN apt-get update && apt-get install -y wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Download and unzip the repository
RUN wget https://github.com/alvelvis/Interrogat-rio/archive/refs/heads/master.zip -O /tmp/Interrogat-rio.zip && \
    unzip /tmp/Interrogat-rio.zip -d /app && \
    mv /app/Interrogat-rio-master /app/Interrogat-rio && \
    rm /tmp/Interrogat-rio.zip

# Install virtualenv
RUN pip install virtualenv

# Create a virtual environment
RUN virtualenv /app/Interrogat-rio/.interrogatorio -p python3

# Activate the virtual environment and install dependencies
RUN /app/Interrogat-rio/.interrogatorio/bin/pip install --no-cache-dir -r /app/Interrogat-rio/requirements.txt

# Activate the virtual environment
ENV VIRTUAL_ENV=/app/Interrogat-rio/.interrogatorio
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app/Interrogat-rio/www

RUN chmod -R a+rwx /app/Interrogat-rio/www

CMD ["sh", "-c", "python -m CGIHTTPServer ${PORT:-8000}"]
