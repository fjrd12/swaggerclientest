# Python image from the Docker Hub
FROM python:3.11.3-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    # - apt-get upgrade is run to patch known vulnerabilities in apt-get packages as
    #   the python base image may be rebuilt too seldom sometimes (less than once a month)
    # required for psutil python package to install
    python3-dev \
    gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
    
# Copy the requirements file into the container
COPY requirements.txt .

RUN pip install --upgrade pip
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the app runs on
EXPOSE 8450

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8450"]