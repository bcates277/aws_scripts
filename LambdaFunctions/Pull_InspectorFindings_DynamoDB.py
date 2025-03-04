import boto3
from datetime import datetime

# Initialize AWS Inspector2 client
inspector_client = boto3.client("inspector2")

# Initialize DynamoDB client
dynamodb_client = boto3.client("dynamodb")
table_name = "InspectorFindings"

def lambda_handler(event, context):
    try:
        # Fetch findings from Amazon Inspector
        response = inspector_client.list_findings(maxResults=50)  # Adjust maxResults as needed
        findings = response.get("findings", [])

        # Process each finding
        for finding in findings:
            store_finding_in_dynamodb(finding)

        return {
            'statusCode': 200,
            'body': 'Findings processed successfully'
        }
    except Exception as e:
        print("Error fetching findings:", str(e))
        return {
            'statusCode': 500,
            'body': 'Error fetching findings'
        }

def store_finding_in_dynamodb(finding):
    try:
        finding_arn = finding["findingArn"]
        finding_status = finding.get("status", "UNKNOWN")
        current_date = datetime.utcnow().isoformat()

        # Store the finding in DynamoDB
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                "FindingARN": {"S": finding_arn},
                "Type": {"S": finding.get("type", "UNKNOWN")},
                "Severity": {"S": finding.get("severity", "UNKNOWN")},
                "Title": {"S": finding.get("title", "N/A")},
                "Status": {"S": finding_status},
                "LastUpdated": {"S": current_date}
            }
        )
        print(f"Stored finding {finding_arn} in DynamoDB")
    except Exception as e:
        print(f"Error storing finding {finding_arn} in DynamoDB:", str(e))