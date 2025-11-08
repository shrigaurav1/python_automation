# IAM User and Policy Automation Script (Boto3)

This Python script automates the creation and configuration of **AWS IAM users** and their associated **policies** using the AWS SDK for Python (`boto3`).  
It supports both **AWS-managed** and **custom policies** defined in a local JSON file.

---

## 🚀 Features

- ✅ Creates a new IAM user automatically.  
- ⚠️ If the user already exists, prompts for confirmation before making changes.  
- 📜 Creates custom IAM policies from a JSON file (if they don’t already exist).  
- 🔗 Attaches both custom and AWS-managed policies to the user.  
- 🔑 Automatically generates access keys for programmatic access.  
- 🧩 Safe to rerun — skips duplicate policy and user creation gracefully.

---

## 🗂️ Project Structure

.

├── main.py # Main Python script

├── policies.json # JSON file defining policies to attach

└── README.md # Documentation (this file)

markdown
Copy code

---

## ⚙️ Prerequisites

Before running the script, ensure you have:

1. **Python 3.8+**
2. **AWS CLI configured** with IAM permissions  
   (The credentials used must have permission for the following actions:)
   - `iam:CreateUser`
   - `iam:CreatePolicy`
   - `iam:AttachUserPolicy`
   - `iam:ListPolicies`
   - `iam:CreateAccessKey`
3. **boto3 library** installed

```bash
pip install boto3
🧩 policies.json Example
Your policies.json defines which policies to create and attach.

json
Copy code
{
  "managed_policies": [
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    "arn:aws:iam::aws:policy/IAMUserChangePassword"
  ],
  "custom_policies": [
    {
      "name": "EC2DescribeOnlyPolicy",
      "document": {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": ["ec2:Describe*"],
            "Resource": "*"
          }
        ]
      }
    }
  ]
}
🖥️ How to Run
Clone or copy this project.

Make sure policies.json is in the same directory as main.py.

Run the script:

bash
Copy code
python main.py
Enter the IAM username when prompted:

pgsql
Copy code
Enter the IAM username to create: demo-user
