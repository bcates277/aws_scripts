import json
import boto3
import requests

# Initialize the Secrets Manager client
secrets_client = boto3.client('secretsmanager')

def get_secret(secret_name):
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    return secret

def lambda_handler(event, context):
    # Retrieve the URL and token from Secrets Manager
    secret_name = "jira_webhook_secret"
    secret = get_secret(secret_name)
    url = secret['url']
    token = secret['token']

    headers = {
        'Content-type': 'application/json',
        'X-Automation-Webhook-Token': token
    }

    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            payload = {
                "Records": [record]
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")

    return {
        'statusCode': 200,
        'body': json.dumps('Data processed successfully')
    }