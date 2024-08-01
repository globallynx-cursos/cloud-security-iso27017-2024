# SEGURIDAD EN LA NUBE BASADO EN ISO/IEC 27017


## Requirements

- Docker installed on your machine

## Included Files

- `Dockerfile`: Defines the Docker image
- `requirements.txt`: Lists the Python packages to be installed
- `README.md`: This file

## Steps to Build and Run the Docker Container

### 1. Clone the Repository

Clone this repository to your local machine:

```sh
git clone https://github.com/your-repo/jupyter-docker-env.git
cd jupyter-docker-env
```
2. Build the Docker Image
In the directory where the Dockerfile and requirements.txt are located, build the Docker image:

``` sh
docker build -t my-jupyter-notebook .
```

3. Run the Docker Container
Run the Docker container, mapping port 8888 and mounting the current directory:

```sh 
docker run -p 8888:8888 -v $(pwd):/root my-jupyter-notebook
```

4. Access Jupyter Notebook
Open your web browser and navigate to http://localhost:8888. You will see the Jupyter Notebook interface.

If prompted for a token, check the terminal where the Docker container is running. The Jupyter Notebook startup logs will include a URL with the token, something like:

``` bash
    http://127.0.0.1:8888/?token=some_long_token
```

5. Using boto3
You can now use boto3 within your Jupyter Notebooks to interact with AWS services.

### Notes
The Dockerfile sets up the environment with Python 3.12 and installs all necessary packages listed in requirements.txt.
The container mounts the current directory to /root in the container, so any changes you make to the files in your local directory will be reflected in the container and vice versa.
Troubleshooting
If you encounter any issues, please ensure that Docker is installed and running on your machine. If the problem persists, feel free to open an issue in this repository.

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.