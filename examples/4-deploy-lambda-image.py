import boto3
import base64
import os
import subprocess
import json

# Initialize boto3 clients
ecr_client = boto3.client('ecr')
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')

def print_docker_info():
    print("\n🐳 About Docker and Containers:")
    print("  • Docker is a platform for developing, shipping, and running applications in containers")
    print("  • Containers are lightweight, standalone, executable packages that include everything needed to run an application")
    print("  • Key components of Docker:")
    print("    - Dockerfile: A text file with instructions to build a Docker image")
    print("    - Docker Image: A read-only template with instructions for creating a Docker container")
    print("    - Docker Container: A runnable instance of a Docker image")
    print("  • Benefits of using Docker with Lambda:")
    print("    - Consistent environment across development and production")
    print("    - Easy management of dependencies and libraries")
    print("    - Ability to use any programming language or framework")
    print("    - Simplified deployment process")
    print("    - Improved isolation and security")

# Step 0: Create or get IAM role
def create_or_get_lambda_role(role_name):
    print(f"\n👤 Checking for IAM role: {role_name}")
    try:
        response = iam_client.get_role(RoleName=role_name)
        print(f"✅ Role {role_name} already exists")
        return response['Role']['Arn']
    except iam_client.exceptions.NoSuchEntityException:
        print(f"🆕 Creating new role: {role_name}")
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        print(f"✅ Role {role_name} created successfully")
        return response['Role']['Arn']

# Step 1: Create ECR repository
def create_ecr_repository(repo_name):
    print(f"\n🚀 Creating ECR repository: {repo_name}")
    try:
        response = ecr_client.create_repository(repositoryName=repo_name)
        print(f"✅ Repository created successfully!")
        return response['repository']['repositoryUri']
    except ecr_client.exceptions.RepositoryAlreadyExistsException:
        print(f"ℹ️ Repository already exists. Fetching URI...")
        return ecr_client.describe_repositories(repositoryNames=[repo_name])['repositories'][0]['repositoryUri']

# Step 2: Build and push Docker image to ECR
def build_and_push_image(repo_uri, dockerfile_path, image_tag):
    print("\n🏗️ Building and Pushing Docker Image:")
    print("  1. Authenticate with Amazon ECR")
    print("  2. Build the Docker image")
    print("  3. Tag the image")
    print("  4. Push the image to ECR")

    print(f"\n🔑 Getting ECR login token...")
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint']

    print(f"\n🏗️ Building Docker image...")
    print("  • Reading instructions from Dockerfile:")
    with open(os.path.join('lambda', dockerfile_path), 'r') as dockerfile:
        print(dockerfile.read())
    print("  • Installing dependencies specified in requirements.txt")
    print("  • Copying Lambda function code into the image")
    print("  • Setting up the Lambda runtime environment")
    subprocess.run(['docker', 'build', '-t', f'{repo_uri}:{image_tag}', '-f', dockerfile_path, '.'], cwd='lambda', check=True)
    print(f"✅ Docker image built successfully!")

    print(f"\n🔐 Logging in to ECR...")
    print("  • Authenticating with Amazon ECR")
    subprocess.run(['docker', 'login', '--username', username, '--password', password, registry], check=True)
    print(f"✅ Logged in to ECR successfully!")

    print(f"\n⬆️ Pushing image to ECR...")
    print("  • Uploading Docker image layers to ECR repository")
    print("  • This may take a few minutes depending on image size and internet speed")
    subprocess.run(['docker', 'push', f'{repo_uri}:{image_tag}'], check=True)
    print(f"✅ Image pushed to ECR successfully!")

# Step 3: Create and deploy Lambda function
def create_lambda_function(function_name, repo_uri, image_tag, role_arn):
    print(f"\n⚙️ Creating Lambda function: {function_name}")
    print("\n📊 Lambda Function Properties:")
    print("  • Timeout: 30 seconds (maximum execution time for each invocation)")
    print("  • Memory: 256 MB (affects CPU power and pricing)")
    print("  • Package Type: Image (using container image from ECR)")
    print("  • Runtime: Defined by the container image")
    print("  • Handler: Defined in the Dockerfile CMD")
    print("  • Environment Variables: Set for configuration")
    print("  • Tracing: X-Ray tracing enabled for debugging")
    print("  • Tags: Added for resource management")
    
    response = lambda_client.create_function(
        FunctionName=function_name,
        PackageType='Image',
        Code={'ImageUri': f'{repo_uri}:{image_tag}'},
        Role=role_arn,
        Timeout=30,
        MemorySize=256,
        Environment={
            'Variables': {
                'ENV': 'production',
                'LOG_LEVEL': 'INFO'
            }
        },
        TracingConfig={
            'Mode': 'Active'
        },
        Tags={
            'Environment': 'Production',
            'Project': 'Serverless Demo'
        }
    )
    
    print(f"\n✅ Lambda function created successfully!")
    return response['FunctionArn']

# Main execution
if __name__ == '__main__':
    repo_name = 'my-lambda-repo'
    image_tag = 'latest'
    function_name = 'my-lambda-function'
    dockerfile_path = 'Dockerfile'
    role_name = 'my-lambda-execution-role'

    print("🎉 Starting Lambda deployment process...")
    print("\n📋 Deployment Process Overview:")
    print("  1. Create or retrieve IAM role for Lambda execution")
    print("  2. Create ECR repository to store Docker image")
    print("  3. Build Docker image from Dockerfile")
    print("  4. Push Docker image to ECR repository")
    print("  5. Create Lambda function using the Docker image")
    print("  6. Configure Lambda function properties and environment")

    print_docker_info()

    # Step 0: Create or get IAM role
    print("\n👤 Step 1: Setting up IAM Role")
    role_arn = create_or_get_lambda_role(role_name)
    print(f"🔑 Using IAM role ARN: {role_arn}")

    # Create ECR repository
    print("\n🏭 Step 2: Creating ECR Repository")
    repo_uri = create_ecr_repository(repo_name)
    print(f"📦 ECR repository URI: {repo_uri}")

    # Build and push Docker image
    print("\n🐳 Step 3 & 4: Building and Pushing Docker Image")
    build_and_push_image(repo_uri, dockerfile_path, image_tag)

    # Create and deploy Lambda function
    print("\n⚙️ Step 5 & 6: Creating and Configuring Lambda Function")
    function_arn = create_lambda_function(function_name, repo_uri, image_tag, role_arn)
    print(f"🎊 Lambda function created with ARN: {function_arn}")

    print("\n🏁 Deployment process completed successfully!")
    print("\n💡 Key Serverless and Docker Benefits:")
    print("  • Reduced operational complexity")
    print("  • Automatic scaling and high availability")
    print("  • Pay-per-use pricing model")
    print("  • Faster time to market and improved developer productivity")
    print("  • Consistent runtime environment across development and production")
    print("  • Easy integration with other AWS services")
    print("  • Simplified dependency management with containers")
    print("  • Improved application isolation and security")
    print("  • Flexibility to use any programming language or library")

    print("\n🚀 Next steps:")
    print("  1. Test your Lambda function using the AWS Console or CLI")
    print("  2. Set up triggers (e.g., API Gateway, S3 events) for your function")
    print("  3. Monitor function performance and logs in CloudWatch")
    print("  4. Iterate and update your function as needed")
    print("  5. Implement CI/CD pipeline for automated deployments")
    print("  6. Optimize function performance and cost")