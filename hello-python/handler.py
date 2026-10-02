import json
from datetime import datetime, timezone

def handle(event, context):
    response = {
        "service": "OpenFaaS Serverless Demo",
        "status": "running",
        "platform": "Kubernetes",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)
    }
