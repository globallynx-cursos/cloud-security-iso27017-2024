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

# Run Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
