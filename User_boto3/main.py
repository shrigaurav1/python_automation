import boto3
import json
import time

iam = boto3.client('iam')

def create_user_with_policies(username, policy_file):
    # Load policy data
    with open(policy_file) as f:
        data = json.load(f)
    
    managed_policies = data.get("managed_policies", [])
    custom_policies = data.get("custom_policies", [])

    print(f"Creating IAM user: {username}")
    iam.create_user(UserName=username)

    # Create and attach custom policies
    for policy in custom_policies:
        policy_name = policy["name"]
        policy_doc = json.dumps(policy["document"])
        print(f"Creating custom policy: {policy_name}")
        response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=policy_doc
        )
        policy_arn = response["Policy"]["Arn"]

        # AWS may need a short delay before attaching a newly created policy
        time.sleep(2)

        print(f"Attaching custom policy {policy_name} to user {username}")
        iam.attach_user_policy(UserName=username, PolicyArn=policy_arn)

    # Attach AWS managed policies
    for arn in managed_policies:
        print(f"Attaching managed policy {arn} to user {username}")
        iam.attach_user_policy(UserName=username, PolicyArn=arn)

    # Create access keys for the user
    access_keys = iam.create_access_key(UserName=username)
    print("\n User created successfully with access keys:")
    print(f"Access Key ID: {access_keys['AccessKey']['AccessKeyId']}")
    print(f"Secret Access Key: {access_keys['AccessKey']['SecretAccessKey']}")

if __name__ == "__main__":
    username = input("Enter the IAM username to create: ")
    create_user_with_policies(username,"policies.json")

