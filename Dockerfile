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

# Install Jupyter
RUN pip install jupyter

# Set the working directory
WORKDIR /root

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