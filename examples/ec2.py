import boto3
from botocore.exceptions import ClientError

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Specify your VPC and subnet IDs
vpc_id = 'vpc-054eacb87342c9240'
subnet_id = 'subnet-00cde9c01181ce876'

# Read the contents of docker_install.sh
with open('docker_install.sh', 'r') as file:
    docker_install_script = file.read()

# Create or get existing security group
security_group_name = 'EC2-InstanceConnect-SG'
try:
    security_group = ec2.create_security_group(
        GroupName=security_group_name,
        Description='Security group for EC2 Instance Connect',
        VpcId=vpc_id
    )
    # Add inbound rule for SSH from EC2 Instance Connect IP range
    ec2.authorize_security_group_ingress(
        GroupId=security_group['GroupId'],
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '18.206.107.24/29'}]  # EC2 Instance Connect IP range
            }
        ]
    )
    print("Security group created successfully with SSH inbound rule")
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
        print("Security group already exists. Using existing group.")
        security_groups = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [security_group_name]},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )['SecurityGroups']
        if security_groups:
            security_group = security_groups[0]
        else:
            raise Exception(f"Security group {security_group_name} not found in VPC {vpc_id}")
    else:
        raise e

# Launch EC2 instance
try:
    user_data_script = f'''#!/bin/bash
        yum update -y
        yum install -y ec2-instance-connect
        echo "Instance launched with EC2 Instance Connect installed"

        # Docker installation script
        {docker_install_script}
    '''

    response = ec2.run_instances(
        ImageId='ami-04a81a99f5ec58529',  # Amazon Linux 2023 AMI
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        UserData=user_data_script,
        NetworkInterfaces=[{
            'SubnetId': subnet_id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [security_group['GroupId']]
        }]
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f"EC2 instance created with ID: {instance_id}")

    print("Setup complete. The instance is launching.")
    print("Docker will be installed during the instance launch.")
    print("You should be able to connect using EC2 Instance Connect once it's ready.")
except ClientError as e:
    print(f"Error launching EC2 instance: {e}")