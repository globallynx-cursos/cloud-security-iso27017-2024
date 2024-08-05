# Use an official Python 3.12 runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /root

# Copy the current directory contents into the container at /root
COPY . /root

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8888 for the Jupyter Notebook
EXPOSE 8888

# Set environment variables for AWS credentials using build arguments
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION

ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

# Run Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
