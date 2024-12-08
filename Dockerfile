FROM python:3.10-slim

# Set the working directory to /app inside the container
WORKDIR /app

# Copy the requirements file first to cache dependencies
COPY requirements.txt .

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the project files into /app
COPY . .

# The .env file should remain outside the image for security reasons.
# You will provide it at runtime using `--env-file .env`.

# Command to start the bot
CMD ["python", "Bot.py"]
