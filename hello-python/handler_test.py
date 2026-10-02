import json
from handler import handle


def test_handle():
    response = handle(None, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["service"] == "OpenFaaS Serverless Demo"
    assert body["status"] == "running"
    assert body["platform"] == "Kubernetes"
    assert "timestamp" in body
