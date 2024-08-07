import boto3
import json
from botocore.exceptions import ClientError

# Placeholder variables for the hardcoded values
VPC_ID = '<your_vpc_id>'
PRIVATE_SUBNET_ID = '<your_private_subnet_id>'
SECURITY_GROUP_NAME = 'PrivateInstanceSSMSG'
IAM_ROLE_NAME = 'SSMInstanceRole'
IAM_INSTANCE_PROFILE_NAME = 'SSMInstanceProfile'

def get_or_create_security_group():
    ec2 = boto3.client('ec2')
    try:
        # Attempt to get the existing security group
        print("Checking for existing security group... 🔍")
        response = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [SECURITY_GROUP_NAME]},
                {'Name': 'vpc-id', 'Values': [VPC_ID]}
            ]
        )
        if response['SecurityGroups']:
            security_group_id = response['SecurityGroups'][0]['GroupId']
            print(f"Existing security group '{SECURITY_GROUP_NAME}' found with ID: {security_group_id} 🔒")
            return security_group_id
        
        # If it doesn't exist, create a new one
        print("Creating new security group... 🛡️")
        response = ec2.create_security_group(
            GroupName=SECURITY_GROUP_NAME,
            Description='Security group for private instance with Session Manager access',
            VpcId=VPC_ID
        )
        security_group_id = response['GroupId']
        print(f"New security group '{SECURITY_GROUP_NAME}' created with ID: {security_group_id} 🆕")

        # Add the egress rule
        try:
            print("Adding egress rule to the security group... 🔓")
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
            print("Egress rule added to the security group. ✅")
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
                print("Egress rule already exists in the security group. ✅")
            else:
                raise

        return security_group_id
    except ClientError as e:
        print(f"Error handling the security group: {e} ❌")
        return None

def create_iam_role_and_instance_profile():
    iam = boto3.client('iam')
    
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

        print("Attaching AmazonSSMManagedInstanceCore policy to the role... 📄")
        iam.attach_role_policy(
            RoleName=IAM_ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
        )
        print("Policy attached to the role. 🔒")

        print("Creating instance profile... 📂")
        iam.create_instance_profile(InstanceProfileName=IAM_INSTANCE_PROFILE_NAME)
        print(f"Instance profile '{IAM_INSTANCE_PROFILE_NAME}' created. ✅")

        print("Adding role to instance profile... 🔗")
        iam.add_role_to_instance_profile(
            InstanceProfileName=IAM_INSTANCE_PROFILE_NAME,
            RoleName=IAM_ROLE_NAME
        )
        print(f"Role '{IAM_ROLE_NAME}' added to instance profile. 🔗")

        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("IAM role or instance profile already exists. Continuing... ✅")
            return True
        else:
            print(f"Error creating IAM role or instance profile: {e} ❌")
            return False

def create_private_instance(security_group_id):
    ec2 = boto3.resource('ec2')
    
    try:
        print("Creating private Ubuntu instance... 🖥️")
        instances = ec2.create_instances(
            ImageId='ami-04a81a99f5ec58529',  # Ubuntu 22.04 LTS
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1,
            NetworkInterfaces=[{
                'SubnetId': PRIVATE_SUBNET_ID,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': False,
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
                            'Value': 'PrivateInstanceWithSessionManager'
                        },
                    ]
                },
            ]
        )
        
        instance = instances[0]
        print("Waiting for instance to start... ⏳")
        instance.wait_until_running()
        instance.reload()
        
        print(f"Private instance created with ID: {instance.id} 🎉")
        print(f"Private IP: {instance.private_ip_address} 📍")

        return instance
    except ClientError as e:
        print(f"Error creating the instance: {e} ❌")
        return None

def main():
    print("Starting IAM role, security group, and instance setup... 🚀")
    if create_iam_role_and_instance_profile():
        security_group_id = get_or_create_security_group()
        if security_group_id:
            instance = create_private_instance(security_group_id)
            if instance:
                print("Private instance created successfully for use with Session Manager. 🎊")
            else:
                print("Failed to create the private instance. 😢")
        else:
            print("Failed to get or create the security group. 😢")
    else:
        print("Failed to create IAM role or instance profile. 😢")

if __name__ == "__main__":
    main()
