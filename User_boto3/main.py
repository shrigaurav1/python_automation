import boto3
import json
import time
from botocore.exceptions import ClientError

iam = boto3.client('iam')

def get_existing_policy_arn(policy_name):
    """
    Check if a policy with the given name already exists in the account.
    Returns its ARN if found, else None.
    """
    paginator = iam.get_paginator('list_policies')
    for page in paginator.paginate(Scope='Local'):
        for policy in page['Policies']:
            if policy['PolicyName'] == policy_name:
                return policy['Arn']
    return None


def create_user_with_policies(username, policy_file):
    # Load policy data
    with open(policy_file) as f:
        data = json.load(f)
    
    managed_policies = data.get("managed_policies", [])
    custom_policies = data.get("custom_policies", [])

    print(f"Creating IAM user: {username}")

    # ---------------------- USER CREATION BLOCK ----------------------
    user_already_exists = False
    try:
        iam.create_user(UserName=username)
        print(f" User '{username}' created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f" User '{username}' already exists.")
            #return
            choice = input("Do you want to continue and modify this existing user's policies? Type 'yes' to continue: ").strip().lower()
            if choice != "yes":
                 print(" Skipping any changes to the existing user.")
                 return  # exit the function — do nothing more
            else:
                 print(" Continuing with existing user changes...")
                 user_already_exists = True
        else:
            raise
    # -----------------------------------------------------------------

    # Create and attach custom policies
    for policy in custom_policies:
        policy_name = policy["name"]
        policy_doc = json.dumps(policy["document"])

        print(f" Checking if custom policy '{policy_name}' already exists...")
        existing_arn = get_existing_policy_arn(policy_name)

        if existing_arn:
            print(f" Policy '{policy_name}' already exists. Using existing ARN.")
            policy_arn = existing_arn
        else:
            print(f"Creating custom policy: {policy_name}")
            response = iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=policy_doc
            )
            policy_arn = response["Policy"]["Arn"]
            # Wait a bit for policy propagation
            time.sleep(2)

        print(f"Attaching policy '{policy_name}' to user '{username}'...")
        iam.attach_user_policy(UserName=username, PolicyArn=policy_arn)

    # Attach AWS managed policies
    for arn in managed_policies:
        print(f"Attaching managed policy {arn} to user {username}")
        iam.attach_user_policy(UserName=username, PolicyArn=arn)

    # Create access keys for the user
    print("Creating access keys...")
    try:
        access_keys = iam.create_access_key(UserName=username)
        print("\n User created successfully with access keys:")
        print(f"Access Key ID: {access_keys['AccessKey']['AccessKeyId']}")
        print(f"Secret Access Key: {access_keys['AccessKey']['SecretAccessKey']}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'LimitExceeded':
            print(" This user already has 2 access keys. Cannot create more.")
        else:
            raise


if __name__ == "__main__":
    username = input("Enter the IAM username to create: ")
    create_user_with_policies(username, "policies.json")
