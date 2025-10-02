# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry for dependency management
RUN pip install poetry

# Copy the dependency files to the working directory
COPY pyproject.toml poetry.lock* ./

# Install project dependencies
# --no-root is used because we are installing in a virtual env managed by poetry
# and we don't need to install the project package itself, just its dependencies.
RUN poetry install --no-root

# Copy the rest of the application's source code
COPY . .

# Set environment variables from build secrets (will be passed by fly.io)
ARG TAVILY_API_KEY
ARG GOOGLE_API_KEY
ENV TAVILY_API_KEY=$TAVILY_API_KEY
ENV GOOGLE_API_KEY=$GOOGLE_API_KEY

# Command to run the application
CMD ["python", "main.py"]