# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the playwright_req.sh script into the container at /app
# COPY playwright_req.sh .

# Run the playwright_req.sh script
# RUN sh playwright_req.sh

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt



# Install Playwright dependencies
RUN playwright install
RUN playwright install-deps 


# Copy the entire project directory into the container at /app
COPY . .

# Expose port 8000 to allow communication to/from server
EXPOSE 8000

# Command to run the Flask application
CMD ["gunicorn", "-b", "0.0.0.0:80", "wsgi:app"]
