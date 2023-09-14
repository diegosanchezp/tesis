# AWS CLI configuration

# Prerequisites

# Steps

- Login into the AWS access portal
- Click "Command line or programmatic access"

- Configure the `tesis-infra` profile

```bash
aws configure sso --profile tesis-infra
```

Input the values from `AWS IAM Identity Center credentials (Recommended)` section

And these values

```
SSO session name (Recommended): tesis-infra-sso
CLI default client Region [None]: us-east-1
CLI default output format [None]:
```

# Troubleshoot

If this error appears then, execute

Error when retrieving token from sso: Token has expired and refresh failed

```bash
aws sso login
```
