import boto3
from datetime import datetime

# Initialize AWS Inspector2 client
inspector_client = boto3.client("inspector2")

# Initialize DynamoDB client
dynamodb_client = boto3.client("dynamodb")
table_name = "InspectorFindings2"

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
        finding_arn = finding.get("findingArn", "N/A")
        description = finding.get("description", "N/A")
        title = finding.get("title", "N/A")
        status = finding.get("status", "UNKNOWN")
        severity = finding.get("severity", "UNKNOWN")
        score = finding.get("inspectorScore", 0)
        aws_account_id = finding.get("awsAccountId", "N/A")
        current_date = datetime.utcnow().isoformat()

        # Initialize fields with default values
        platform = "N/A"
        pushed_at = "N/A"
        repository_name = "N/A"
        image_hash = "N/A"
        region = "N/A"

        # Extract nested fields from resources
        resources = finding.get("resources", [])
        if resources:
            for resource in resources:
                if resource["type"] == "AWS_ECR_CONTAINER_IMAGE" and "details" in resource:
                    platform = resource["details"]["awsEcrContainerImage"].get("platform", "N/A")
                    pushed_at = resource["details"]["awsEcrContainerImage"].get("pushedAt", "N/A")
                    if isinstance(pushed_at, datetime):
                        pushed_at = pushed_at.isoformat()
                    repository_name = resource["details"]["awsEcrContainerImage"].get("repositoryName", "N/A")
                    image_hash = resource["details"]["awsEcrContainerImage"].get("imageHash", "N/A")
                    region = resource.get("region", "N/A")
                    break
        if status == "CLOSED":
            # Delete the finding from DynamoDB if the status is CLOSED
            dynamodb_client.delete_item(
                TableName=table_name,
                Key={
                    "FindingARN": {"S": finding_arn}
                }
            )
            print(f"Deleted finding {finding_arn} from DynamoDB")
        else:
            # Store or update the finding in DynamoDB
            dynamodb_client.put_item(
                TableName=table_name,
                Item={
                    "FindingARN": {"S": finding_arn},
                    "Description": {"S": description},
                    "Title": {"S": title},
                    "Status": {"S": status},
                    "Severity": {"S": severity},
                    "Score": {"N": str(score)},
                    "Platform": {"S": platform},
                    "PushedAt": {"S": pushed_at},
                    "RepositoryName": {"S": repository_name},
                    "ImageHash": {"S": image_hash},
                    "Region": {"S": region},
                    "AwsAccountId": {"S": aws_account_id},
                    "LastUpdated": {"S": current_date}
            }
        )
        print(f"Stored or updated finding {finding_arn} in DynamoDB")
    except Exception as e:
        print(f"Error processing finding {finding_arn} in DynamoDB:", str(e))
