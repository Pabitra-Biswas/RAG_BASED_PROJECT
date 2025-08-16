# Step 1: Use a specific, slim Python runtime as a parent image
FROM python:3.10-slim

# Step 2: Set environment variables for best practices
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Step 3: Set the working directory inside the container
WORKDIR /code

# Step 4: Copy only the requirements file to leverage Docker cache
COPY ./requirements.txt /code/requirements.txt

# Step 5: Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Step 6: Copy your application code and other necessary assets
COPY ./app /code/app
COPY ./templates /code/templates
# Note: Copying the initial DB state is fine, but for production,
# data should be managed via volumes or a managed database.
COPY ./chroma_db_storage /code/chroma_db_storage 

# --- CHANGE 1: Set a default PORT environment variable ---
# This makes the container work correctly for local "docker run" commands.
# It also serves as documentation for the port the app uses.
ENV PORT=8000

# --- CHANGE 2: Expose the PORT variable ---
# This tells Docker to expose the port defined by the $PORT variable.
# It's a good practice for clarity.
EXPOSE $PORT

# --- CHANGE 3: Use the PORT environment variable in the run command ---
# This is the most critical change.
# On Cloud Run, the $PORT variable will be automatically set to 8080.
# Locally, it will use the default value of 8000 that we set above.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]