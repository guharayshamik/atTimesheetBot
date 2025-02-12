# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy and install dependencies separately for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose necessary ports (modify if needed)
EXPOSE 8000

# Run the bot (environment variables should be passed at runtime)
CMD ["python", "bot.py"]

