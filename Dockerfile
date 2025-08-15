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
COPY ./chroma_db_storage /code/chroma_db_storage 

# Step 7: Expose the port that Uvicorn will run on
EXPOSE 8000

# Step 8: Define the command to run your app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]