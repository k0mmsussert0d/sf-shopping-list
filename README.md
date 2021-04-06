# 🛒 sf-shopping-list
Shared lists web-app hosted in AWS with Serverless Framework

## Using:
- API Gateway
- Lambda
- DynamoDB
- Cognito
- S3

## Progress:
- Cognito:
    - IdP using User Pool - ✅
    - External IdPs - ❌
- DynamoDB:
    - lists table - ✅
        - user-to-lists relation - ✅
    - invitations table with ttl - ✅
    - fine-tuning - ❌
- REST API:
    - Lists CRUD - ✅
    - Sharing lists - ✅
    - CORS configuration - ❌
- SES integration - in progress
- Front-end:
    - Authentication - ✅
    - Modifying lists - ✅
    - Sharing lists - ❌
    - User profile - ❌
    - Live demo hosting - ❌
- S3:
    - Resources uploading - ✅ 
  
## Usage:
```
git clone https://github.com/k0mmsussert0d/sf-shopping-list
cd sf-shopping-list/
yarn
sls deploy
```
