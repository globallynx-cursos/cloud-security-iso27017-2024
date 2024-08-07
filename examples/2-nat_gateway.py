import boto3
from botocore.exceptions import ClientError

# Placeholder variables for the hardcoded values
VPC_ID = 'vpc-00b45efad34b1c6e5'
PUBLIC_SUBNET_ID = '<your_public_subnet_id>'
PRIVATE_SUBNET_ID = '<your_private_subnet_id>'
ROUTE_TABLE_ID = '<your_route_table_id>'

def create_nat_gateway_and_update_route_table():
    ec2 = boto3.client('ec2')
    
    try:
        # Create an Elastic IP for the NAT Gateway
        print("Creating Elastic IP... 🌐")
        eip_response = ec2.allocate_address(Domain='vpc')
        allocation_id = eip_response['AllocationId']
        print(f"Elastic IP created with Allocation ID: {allocation_id} 📍")

        # Create NAT Gateway in the public subnet
        print("Creating NAT Gateway in the public subnet... 🚀")
        nat_gateway_response = ec2.create_nat_gateway(
            AllocationId=allocation_id,
            SubnetId=PUBLIC_SUBNET_ID,
        )
        nat_gateway_id = nat_gateway_response['NatGateway']['NatGatewayId']
        print(f"NAT Gateway created with ID: {nat_gateway_id} 🛠️")

        # Wait for the NAT Gateway to become available
        print("Waiting for NAT Gateway to become available... ⏳")
        waiter = ec2.get_waiter('nat_gateway_available')
        waiter.wait(NatGatewayIds=[nat_gateway_id])
        print("NAT Gateway is now available! 🎉")

        # Update the existing route table
        print("Updating the route table... 🛣️")
        ec2.create_route(
            RouteTableId=ROUTE_TABLE_ID,
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=nat_gateway_id
        )
        print(f"Route added to route table {ROUTE_TABLE_ID} 📋")

        # Check if the route table is associated with the private subnet
        print("Checking if the route table is associated with the private subnet... 🔍")
        associations = ec2.describe_route_tables(RouteTableIds=[ROUTE_TABLE_ID])['RouteTables'][0]['Associations']
        is_associated = any(assoc['SubnetId'] == PRIVATE_SUBNET_ID for assoc in associations)
        
        if not is_associated:
            print("Associating route table with the private subnet... 🔗")
            ec2.associate_route_table(
                RouteTableId=ROUTE_TABLE_ID,
                SubnetId=PRIVATE_SUBNET_ID
            )
            print(f"Route table {ROUTE_TABLE_ID} associated with private subnet {PRIVATE_SUBNET_ID} ✅")
        else:
            print(f"Route table {ROUTE_TABLE_ID} is already associated with private subnet {PRIVATE_SUBNET_ID} ⚙️")

        return True
    except ClientError as e:
        print(f"Error creating NAT Gateway or configuring routes: {e} ❌")
        return False

def main():
    print("Starting NAT Gateway creation and route configuration... 🚀")
    if create_nat_gateway_and_update_route_table():
        print("NAT Gateway created and routes configured successfully. 🎊")
    else:
        print("Failed to create NAT Gateway or configure routes. 😢")

if __name__ == "__main__":
    main()
