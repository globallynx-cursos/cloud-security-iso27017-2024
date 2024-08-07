import boto3
from botocore.exceptions import ClientError

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Specify your VPC and subnet IDs
VPC_ID = '<your_vpc_id>'
SUBNET_ID = '<your_subnet_id>'

# Read the contents of docker_install.sh
with open('scripts/docker_install.sh', 'r') as file:
    docker_install_script = file.read()

# Create or get existing security group
SECURITY_GROUP_NAME = 'EC2-InstanceConnect-SG'

try:
    print("Creating security group... 🛡️")
    security_group = ec2.create_security_group(
        GroupName=SECURITY_GROUP_NAME,
        Description='Security group for EC2 Instance Connect',
        VpcId=VPC_ID
    )
    print("Security group created! Adding inbound rule for SSH... 🔒")
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
    print("Inbound rule added! 🎉")
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
        print("Security group already exists. Using existing group. ✅")
        security_groups = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [SECURITY_GROUP_NAME]},
                {'Name': 'vpc-id', 'Values': [VPC_ID]}
            ]
        )['SecurityGroups']
        if security_groups:
            security_group = security_groups[0]
        else:
            raise Exception(f"Security group {SECURITY_GROUP_NAME} not found in VPC {VPC_ID}")
    else:
        raise e

# Launch EC2 instance
try:
    print("Launching EC2 instance... 🚀")
    user_data_script = f'''#!/bin/bash
        yum update -y
        yum install -y ec2-instance-connect
        echo "Instance launched with EC2 Instance Connect installed" > /var/log/user-data.log

        # Docker installation script
        {docker_install_script}
    '''

    response = ec2.run_instances(
        ImageId='<your_ami_id>', #Sugested Ubuntu on us-east-1 ami-04a81a99f5ec58529
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        UserData=user_data_script,
        NetworkInterfaces=[{
            'SubnetId': SUBNET_ID,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [security_group['GroupId']]
        }]
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f"EC2 instance created with ID: {instance_id} 🎊")

    print("Setup complete. The instance is launching. ⏳")
    print("Docker will be installed during the instance launch. 🐳")
    print("You should be able to connect using EC2 Instance Connect once it's ready. 🔌")
except ClientError as e:
    print(f"Error launching EC2 instance: {e} ❌")
