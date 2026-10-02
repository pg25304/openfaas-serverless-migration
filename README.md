# OpenFaaS Serverless Migration and CI/CD Project

A practical cloud-native serverless project demonstrating how a Python function can be developed, containerised, tested, published and deployed using **OpenFaaS, Docker, Kubernetes, GitHub Container Registry and GitHub Actions**.

The project began as an OpenFaaS serverless deployment exercise and was extended to explore secure authentication, container-registry integration, automated testing, Continuous Integration and Continuous Delivery (CI/CD), monitoring, troubleshooting and future cloud migration.

---

## Project Overview

I developed a stateless Python serverless function and deployed it through OpenFaaS onto a local Kubernetes cluster provided by Docker Desktop.

Rather than stopping after successfully deploying the function, I extended the project by integrating **GitHub Container Registry (GHCR)**, automated testing with **pytest**, and a **GitHub Actions CI/CD pipeline**.

The implemented workflow is:

**Source Code → Automated Testing → OpenFaaS Build → GHCR Publication → Controlled Deployment → OpenFaaS → Kubernetes → Function Endpoint**

The project also documents the security decisions, limitations and troubleshooting encountered during implementation.

---

## Architecture

```text
                         GitHub Repository
                                |
                                v
                         GitHub Actions
                                |
                      +---------+---------+
                      |                   |
                      v                   v
                   pytest             faas-cli
                    Tests               Build
                      |                   |
                      +---------+---------+
                                |
                                v
                    GitHub Container Registry
                             (GHCR)
                                |
                   CI/CD AUTOMATION ENDS HERE
                                |
                     Controlled / Manual
                      faas-cli deploy
                                |
                                v
                           OpenFaaS
                                |
                                v
                     Kubernetes Deployment
                                |
                                v
                       hello-python Pod
                                |
                                v
                       OpenFaaS Gateway
                                |
                                v
                         HTTP/JSON Response
```

The current Kubernetes environment runs locally using Docker Desktop.

GitHub Actions automates **testing, building and container-image publication**. Deployment from GHCR to the local OpenFaaS/Kubernetes environment remains a controlled manual stage.

This distinction is intentional so that the project accurately represents what has been automated.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| OpenFaaS | Function-as-a-Service platform |
| Kubernetes | Container orchestration |
| Docker Desktop | Local Kubernetes and container environment |
| Python | Serverless function development |
| Docker | Function containerisation |
| Helm | OpenFaaS installation |
| GitHub | Source control |
| GitHub Actions | CI/CD automation |
| GitHub Container Registry (GHCR) | Container-image registry |
| pytest | Automated function testing |
| Prometheus | Platform and function monitoring |
| Windows Subsystem for Linux (WSL) | Linux build environment |

---

## Serverless Function

I created the function using the official OpenFaaS `python3-http` template.

The function is deliberately stateless and returns a small **JavaScript Object Notation (JSON)** response containing the service name, operational status, platform and **Coordinated Universal Time (UTC)** timestamp.

```python
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
```

Example response:

```json
{
  "service": "OpenFaaS Serverless Demo",
  "status": "running",
  "platform": "Kubernetes",
  "timestamp": "2026-10-02T15:15:51.831720+00:00"
}
```

---

## OpenFaaS and Kubernetes Deployment

OpenFaaS was installed on the local Kubernetes cluster using Helm.

Separate Kubernetes namespaces were used for the platform and functions:

```text
openfaas
openfaas-fn
```

The deployed OpenFaaS environment included components such as:

- OpenFaaS Gateway
- Prometheus
- Alertmanager
- NATS
- Queue Worker

The OpenFaaS Gateway was exposed locally on port `8080`.

The deployment configuration is defined in:

```text
stack.yaml
```

The function container image is stored in GitHub Container Registry:

```text
ghcr.io/pg25304/hello-python:latest
```

Following deployment, Kubernetes reported the function pod as healthy:

```text
READY   STATUS    RESTARTS
1/1     Running   0
```

The function was then successfully invoked through the OpenFaaS Gateway and returned the expected JSON response.

---

## Automated Testing

I added automated testing rather than relying only on manual function invocation.

The pytest test verifies:

- HTTP status code;
- service name;
- operational status;
- Kubernetes platform value; and
- presence of a timestamp.

```python
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
```

The automated test must succeed before the CI/CD pipeline proceeds to the image build and publication stage.

---

## CI/CD Pipeline

I implemented a GitHub Actions workflow to automate the repeatable parts of the delivery process.

When code is pushed to the `main` branch, the pipeline:

1. checks out the repository;
2. configures Python;
3. installs the required test dependencies;
4. executes the pytest test;
5. installs the OpenFaaS Command-Line Interface (CLI);
6. retrieves the OpenFaaS Python template;
7. authenticates to GitHub Container Registry;
8. builds the OpenFaaS function image; and
9. publishes the image to GHCR.

The `build-and-publish` job depends on the successful completion of the testing job.

```text
Git Push
   |
   v
Automated Test
   |
   v
OpenFaaS Build
   |
   v
GHCR Publication
```

This means that a failed automated test prevents the container-image publication stage from proceeding.

The final deployment into my local Kubernetes environment remains manually controlled.

---

## Security Implementation

Security was treated as an important part of the implementation rather than an afterthought.

### Secure OpenFaaS Authentication

The OpenFaaS administrator password was retrieved from the Kubernetes Secret and passed securely to the OpenFaaS CLI through standard input.

The password was not hard-coded into the project files.

### Least-Privilege Access

I separated repository access from container-registry access rather than using one broadly privileged credential.

Permissions were restricted to those required for each operation.

The GitHub Actions workflow uses the automatically generated `GITHUB_TOKEN` for GHCR publication with:

```yaml
permissions:
  contents: read
  packages: write
```

This avoids storing a personal GHCR access token inside the workflow.

### Credential Rotation

During implementation, a **Personal Access Token (PAT)** was accidentally visible in a screenshot.

I treated the credential as compromised and immediately:

1. revoked the exposed token;
2. generated a replacement;
3. restricted its permissions;
4. applied a short expiration period; and
5. ensured the exposed credential was excluded from published evidence.

This became a practical security lesson from the project and reinforced the importance of reviewing screenshots, terminal output and documentation before publication.

### Container Registry Security

The function image was made public because of the OpenFaaS Community Edition constraint encountered during the lab.

Public visibility should **not** be interpreted as a security advantage.

For a production implementation, I would prefer controlled private-registry access where supported, combined with measures such as:

- vulnerability scanning;
- image signing and attestation;
- immutable image versions;
- stronger software-supply-chain controls; and
- controlled deployment permissions.

---

## Troubleshooting and Lessons Learned

An important part of this project was documenting failures and their resolutions rather than presenting only the final successful configuration.

### Windows OpenFaaS Build Issue

The initial OpenFaaS function build failed under Windows because the Windows drive path was incorrectly interpreted while the OpenFaaS template was being processed.

Running the same process through Git Bash did not resolve the problem.

I therefore moved the build process to Ubuntu 24.04 using **Windows Subsystem for Linux (WSL)**.

Docker integration was verified against the Docker Desktop engine, and the OpenFaaS function subsequently built successfully in the Linux environment.

### WSL and VPN Connectivity

A second problem occurred when installation of the Linux OpenFaaS CLI failed because outbound **Hypertext Transfer Protocol Secure (HTTPS)** connections from WSL were timing out.

Testing showed that my active **Virtual Private Network (VPN)** was interfering with WSL connectivity.

After disabling the VPN, connectivity to GitHub was restored and the OpenFaaS CLI installation completed successfully.

This demonstrated how local networking and VPN configuration can affect cloud-development tooling.

### GitHub Container Registry Permission Issue

The first automated image-publication attempt failed with:

```text
permission_denied: write_package
```

Authentication itself had succeeded.

The problem was traced to the GHCR package's GitHub Actions access configuration.

After granting the repository **Write** access to the package, I reran the workflow.

Both the testing and `build-and-publish` jobs then completed successfully, and GHCR showed the newly published image.

This demonstrated that repository-level workflow permissions and package-level registry permissions both need to be considered when implementing CI/CD.

---

## Monitoring

Prometheus was deployed as part of the OpenFaaS platform.

I generated requests against the deployed function and confirmed that the invocation metrics increased.

This demonstrated that the platform was collecting operational data about function execution.

Monitoring provides a foundation for:

- invocation monitoring;
- performance analysis;
- alerting;
- troubleshooting; and
- capacity planning.

---

## Scaling Experiment

I also explored OpenFaaS scaling behaviour.

Minimum and maximum replica labels were configured and both burst and sustained request loads were generated against the function.

Prometheus successfully recorded the requests, but the function remained at one replica during the experiment.

For this reason, I do **not** claim that automatic horizontal scaling was successfully demonstrated.

This was still a useful result because it reinforced the importance of understanding edition-specific OpenFaaS capabilities and verifying actual platform behaviour rather than assuming that configuration alone proves autoscaling.

---

## Evidence

Evidence captured during the project includes:

- Kubernetes cluster readiness;
- OpenFaaS platform deployment;
- OpenFaaS Gateway configuration;
- Python function creation;
- successful container build;
- GHCR image publication;
- Kubernetes function pod running successfully;
- successful HTTP function invocation;
- automated pytest execution;
- successful GitHub Actions CI/CD pipeline;
- automated GHCR publication;
- WSL and VPN troubleshooting;
- GitHub repository configuration; and
- GHCR workflow-permission troubleshooting.

Sensitive credentials are excluded or redacted from any evidence intended for publication.

---

## Key Outcomes

The project successfully demonstrated:

- development of a working Python serverless function;
- OpenFaaS deployment on Kubernetes;
- Docker-based function containerisation;
- GitHub Container Registry integration;
- successful Kubernetes workload execution;
- automated function testing;
- automated OpenFaaS container building;
- automated GHCR publication;
- Prometheus monitoring;
- secure credential handling;
- least-privilege access controls;
- CI/CD troubleshooting;
- credential revocation and rotation; and
- documentation of implementation limitations.

The project reinforced an important cloud-computing principle:

> **Serverless does not eliminate infrastructure; it changes how infrastructure responsibilities are managed.**

---

## Current Limitations

The implementation is currently a local proof of concept rather than a production cloud deployment.

The main limitations are:

- Kubernetes currently runs locally through Docker Desktop.
- Deployment from GHCR into the local OpenFaaS cluster remains manually triggered.
- The current container image uses the mutable `latest` tag.
- The Community Edition implementation required a public function image.
- Automatic horizontal scaling was investigated but not successfully demonstrated.

These limitations are documented deliberately rather than hidden.

---

## Future Improvements

### Azure Kubernetes Service

The main future development would be migrating the deployment from Docker Desktop Kubernetes to **Azure Kubernetes Service (AKS)**.

AKS would move the project from a local proof of concept to a managed cloud Kubernetes environment and provide an opportunity to investigate a more production-oriented OpenFaaS architecture.

Future work could include:

- deploying OpenFaaS to AKS;
- cloud-based automated deployment;
- Azure identity and access management;
- stronger network segmentation;
- centralised logging and monitoring;
- secure secrets management;
- controlled private-registry integration where appropriate;
- vulnerability scanning;
- container-image signing and attestation;
- deployment environments and approval controls; and
- improved availability and resilience.

### Immutable Container Images

The current `latest` image tag should eventually be replaced with an immutable version based on a Git commit identifier or container-image digest.

This would improve:

- deployment traceability;
- rollback capability;
- reproducibility; and
- auditability.

### Full Continuous Deployment

The existing pipeline automates testing, building and container publication.

A future cloud implementation could extend this to controlled automatic deployment into AKS after successful validation, with suitable authentication, environment protection and approval controls.

---

## Repository Structure

```text
openfaas-serverless-migration/
│
├── .github/
│   └── workflows/
│       └── openfaas-ci.yml
│
├── hello-python/
│   ├── handler.py
│   ├── handler_test.py
│   └── requirements.txt
│
├── .gitignore
├── stack.yaml
└── README.md
```

---

## What I Learned

This project gave me a clearer understanding of what happens behind a serverless function.

The Python handler itself was relatively simple. The more valuable learning came from integrating the function with Kubernetes, Docker, OpenFaaS, a container registry, automated testing and CI/CD.

I also gained practical experience troubleshooting build environments, networking and registry permissions while applying security principles such as least privilege, credential separation and immediate credential rotation following accidental exposure.

Most importantly, the project demonstrated that cloud automation is valuable only when **security, monitoring and operational controls are designed alongside it**.

---

## Future Direction

This repository provides the technical record of my local OpenFaaS implementation.

The next logical development stage is to migrate the architecture to Azure Kubernetes Service and investigate a secure end-to-end cloud deployment pipeline.

---

## References

GitHub (2026) *GITHUB_TOKEN*. GitHub Docs. Available at:  
https://docs.github.com/en/actions/concepts/security/github_token  
(Accessed: 2 October 2026).

GitHub (2026) *Publishing and installing a package with GitHub Actions*. GitHub Docs. Available at:  
https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions  
(Accessed: 2 October 2026).

Kubernetes (2026) *Self-Healing*. Kubernetes Documentation. Available at:  
https://kubernetes.io/docs/concepts/architecture/self-healing/  
(Accessed: 2 October 2026).

Microsoft (2026) *What is Azure Kubernetes Service (AKS)?* Microsoft Learn. Available at:  
https://learn.microsoft.com/en-us/azure/aks/what-is-aks  
(Accessed: 2 October 2026).

Microsoft (2026) *Secure your Azure Kubernetes Service (AKS) deployment*. Microsoft Learn. Available at:  
https://learn.microsoft.com/en-us/azure/aks/secure-aks  
(Accessed: 2 October 2026).

OpenFaaS (2026) *OpenFaaS Documentation*. Available at:  
https://docs.openfaas.com/  
(Accessed: 2 October 2026).

OpenFaaS (2026) *Auto-scaling your functions*. Available at:  
https://docs.openfaas.com/architecture/autoscaling/  
(Accessed: 2 October 2026).

OpenFaaS (2026) *CI/CD with OpenFaaS*. Available at:  
https://docs.openfaas.com/reference/cicd/intro/  
(Accessed: 2 October 2026).

OpenFaaS (2026) *Working with image tags*. Available at:  
https://docs.openfaas.com/cli/tags/  
(Accessed: 2 October 2026).

---

## Author

**Payman Ghorbani**

MSc Cybersecurity  
University of Essex Online

Cloud Computing | Cloud Security | Microsoft Azure | Kubernetes | DevSecOps
