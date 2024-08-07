import boto3
import json
import time
from botocore.exceptions import ClientError

# Placeholder variables for the hardcoded values
VPC_ID = '<your_vpc_id>'
SUBNET_ID = '<your_subnet_id>'
SECURITY_GROUP_NAME = 'UbuntuSessionManagerSG'
IAM_ROLE_NAME = 'SSMInstanceRole'
IAM_INSTANCE_PROFILE_NAME = 'SSMInstanceProfile'

def create_iam_role_and_instance_profile():
    iam = boto3.client('iam')
    
    # Create IAM role
    try:
        print("Creating IAM role... 👤")
        trust_relationship = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        iam.create_role(
            RoleName=IAM_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_relationship)
        )
        print(f"IAM role '{IAM_ROLE_NAME}' created. ✅")

        # Attach the AmazonSSMManagedInstanceCore policy
        print("Attaching AmazonSSMManagedInstanceCore policy... 📄")
        iam.attach_role_policy(
            RoleName=IAM_ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
        )
        print("Policy attached. 🔒")

        # Create the instance profile
        print("Creating instance profile... 📂")
        iam.create_instance_profile(InstanceProfileName=IAM_INSTANCE_PROFILE_NAME)
        print(f"Instance profile '{IAM_INSTANCE_PROFILE_NAME}' created. ✅")

        # Add the role to the instance profile
        print("Adding role to instance profile... 🔗")
        iam.add_role_to_instance_profile(
            InstanceProfileName=IAM_INSTANCE_PROFILE_NAME,
            RoleName=IAM_ROLE_NAME
        )
        print(f"Role '{IAM_ROLE_NAME}' added to instance profile. 🔗")

        # Wait for the instance profile to become available
        print("Waiting for the instance profile to become available... ⏳")
        time.sleep(10)

    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("IAM role or instance profile already exists. Continuing... ✅")
        else:
            print(f"Error creating IAM role or instance profile: {e} ❌")
            return False

    return True

def get_or_create_security_group():
    ec2 = boto3.client('ec2')
    try:
        print("Checking for existing security group... 🔍")
        response = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [SECURITY_GROUP_NAME]},
                {'Name': 'vpc-id', 'Values': [VPC_ID]}
            ]
        )
        
        if response['SecurityGroups']:
            security_group_id = response['SecurityGroups'][0]['GroupId']
            print(f"Existing security group found with ID: {security_group_id} 🔒")
            return security_group_id
        
        print("Creating new security group... 🛡️")
        security_group = ec2.create_security_group(
            GroupName=SECURITY_GROUP_NAME,
            Description='Security group for Ubuntu with Session Manager access',
            VpcId=VPC_ID
        )
        
        security_group_id = security_group['GroupId']

        try:
            print("Authorizing egress rules for the security group... 🔓")
            ec2.authorize_security_group_egress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': '-1',
                        'FromPort': -1,
                        'ToPort': -1,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'InvalidPermission.Duplicate':
                raise
            print("Egress rule already exists, continuing... ✅")

        print(f"New security group created with ID: {security_group_id} 🆕")
        return security_group_id
    except ClientError as e:
        print(f"Error handling security group: {e} ❌")
        return None

def create_ubuntu_instance(security_group_id):
    ec2 = boto3.resource('ec2')
    
    try:
        print("Creating Ubuntu instance... 🖥️")
        instances = ec2.create_instances(
            ImageId='ami-04a81a99f5ec58529',  # Ubuntu on us-east-1
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1,
            NetworkInterfaces=[{
                'SubnetId': SUBNET_ID,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': [security_group_id]
            }],
            IamInstanceProfile={'Name': IAM_INSTANCE_PROFILE_NAME},
            UserData='''#!/bin/bash
                apt-get update
                apt-get install -y snapd
                snap install amazon-ssm-agent --classic
                systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
                systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service
            ''',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'UbuntuSessionManagerInstance'
                        },
                    ]
                },
            ]
        )
        
        instance = instances[0]
        print("Waiting for instance to start... ⏳")
        instance.wait_until_running()
        instance.reload()
        
        print(f"Ubuntu instance created with ID: {instance.id} 🎉")
        print(f"Private IP: {instance.private_ip_address} 📍")
        print(f"Public IP: {instance.public_ip_address} 🌐")

        return instance
    except ClientError as e:
        print(f"Error creating the instance: {e} ❌")
        return None

def main():
    print("Starting IAM role, security group, and instance setup... 🚀")
    if create_iam_role_and_instance_profile():
        security_group_id = get_or_create_security_group()
        if security_group_id:
            instance = create_ubuntu_instance(security_group_id)
            if instance:
                print("Ubuntu instance created successfully for use with Session Manager. 🎊")
            else:
                print("Failed to create the Ubuntu instance. 😢")
        else:
            print("Failed to get or create the security group. 😢")
    else:
        print("Failed to create IAM role or instance profile. 😢")

if __name__ == "__main__":
    main()
