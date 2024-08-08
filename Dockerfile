FROM python:3.12-slim

# Install Docker
RUN apt-get update && \
    apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io

# Install AWS CLI
RUN apt-get install -y unzip && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

# Install Jupyter
RUN pip install jupyter

# Set the working directory
WORKDIR /root

# Accept build arguments for AWS credentials
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION

# Set environment variables for AWS credentials
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

# Copy the requirements file and install dependencies
COPY requirements.txt /root/requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /root
COPY . /root

# Create a startup script
RUN echo '#!/bin/bash' > /start.sh && \
    echo 'service docker start' >> /start.sh && \
    echo 'sleep 5' >> /start.sh && \
    echo 'jupyter notebook --ip=0.0.0.0 --no-browser --allow-root' >> /start.sh && \
    chmod +x /start.sh

# Expose port 8888 for Jupyter Notebook
EXPOSE 8888

# Run the startup script
CMD ["/start.sh"]