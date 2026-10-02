# OpenFaaS Serverless Migration and CI/CD Project

A practical cloud-native serverless project demonstrating how a Python function can be developed, containerised, tested, published and deployed using **OpenFaaS, Docker, Kubernetes, GitHub Container Registry and GitHub Actions**.

The project began as an OpenFaaS serverless deployment exercise and was extended to explore secure authentication, container-registry integration, automated testing, Continuous Integration and Continuous Delivery (CI/CD), monitoring and cloud migration considerations.

---

## Project Overview

I developed a stateless Python serverless function and deployed it through OpenFaaS onto a local Kubernetes cluster provided by Docker Desktop.

Rather than stopping after the function was successfully deployed, I extended the implementation by integrating GitHub Container Registry (GHCR), automated testing with pytest and a GitHub Actions CI/CD workflow.

The resulting workflow is:

**Source Code → Automated Test → OpenFaaS Build → GHCR → OpenFaaS → Kubernetes → Function Endpoint**

The project also documents the security decisions and troubleshooting involved in building the environment.

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
             pytest              faas-cli
              Tests                Build
                                     |
                                     v
                        GitHub Container Registry
                               (GHCR)
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
                          HTTP JSON Response
