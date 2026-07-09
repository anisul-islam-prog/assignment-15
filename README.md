# Assignment-15: Improving Quality, Security & Performance in CI/CD

> Ostad "Mastering DevOps" — Submitted by [Anisul Islam]

## Architecture

```plain
GitHub → GitHub Actions → (Tests → SonarCloud → Trivy → OPA → Build → k6) → EC2
```

- **Source Control:** GitHub
- **CI/CD:** GitHub Actions
- **Compute:** AWS EC2 (t2.micro)
- **Artifacts:** GitHub Container Registry (GHCR)
- **Quality:** SonarCloud
- **Security:** Trivy (FS + Image)
- **Load Testing:** k6
- **Policy:** OPA / Conftest
- **IaC:** Terraform (EC2, S3, Security Group)

---

## Tools Used

| Tool | Purpose | Version |
|------|---------|---------|
| Python / Flask | Application | 3.11 |
| pytest | Unit testing | 8.2.0 |
| SonarCloud | Code quality | Cloud |
| Trivy | Security scanning | Latest |
| k6 | Load testing | v0.3.1 (Action) |
| OPA / Conftest | Policy as Code | v0.49.1 |
| Terraform | Infrastructure | ~> 5.0 |
| Docker | Containerization | 24.x |
| GitHub Actions | CI/CD orchestration | — |

---

## Steps Performed

### Part 1: Unit Testing & Code Quality

1. Wrote 5 pytest cases covering health, CRUD operations, and validation.
2. Integrated `pytest --cov` into GitHub Actions.
3. Connected SonarCloud for static analysis.
4. **Fixed 2 issues:**
   - **Code Smell:** Removed hardcoded `debug=True` → used `FLASK_DEBUG` env var.
   - **Bug:** Added `SECRET_KEY` validation with `ValueError` on missing key.

### Part 2: Load Testing

1. Wrote `load-tests/load-test.js` with k6.
2. Simulated 100 VUs with ramp-up/ramp-down stages.
3. **Results:** p95 response time < 500ms, 0% failure rate across 1,500 requests.

### Part 3: Security Scanning

1. Added Trivy filesystem scan and Docker image scan to CI.
2. **Fixed 2 vulnerabilities:**
   - **CVE (OS):** Updated base image to `python:3.11-slim-bookworm` with `apt-get upgrade`.
   - **Misconfiguration:** Added non-root `USER appuser` and `HEALTHCHECK` to Dockerfile.

### Part 4: Secrets Management

1. Removed all hardcoded secrets from `app/config.py`.
2. Stored secrets in GitHub Encrypted Secrets (`SECRET_KEY`, `AWS_*`, `EC2_*`).
3. Injected secrets at runtime via Docker Compose environment variables.
4. Application fails closed (`ValueError`) if `SECRET_KEY` is missing.

### Part 5: Policy as Code

1. Wrote `policies/docker.rego` with 3 deny rules + 1 warn rule.
2. Integrated Conftest into CI to validate Dockerfile before build.
3. **Enforces:** No `latest` tags, non-root user, health checks.

### Deployment

1. Provisioned EC2 + S3 + Security Group via Terraform.
2. Deployed via GitHub Actions SSH to EC2 using Docker Compose.
3. Health check verification post-deployment.

---

## Key Learnings

1. **Shift-left security:** Running Trivy on both filesystem and image catches vulnerabilities at two layers — dependencies and OS packages.
2. **Policy as Code prevents human error:** OPA catches Dockerfile anti-patterns before they reach production.
3. **Secrets should never touch disk:** GitHub Secrets + runtime env vars ensure credentials never exist in source code or image layers.
4. **Load testing in CI is feasible:** k6 service containers in GitHub Actions allow performance validation on every PR.
5. **Terraform state in S3:** Remote state prevents team conflicts and enables collaboration.

---

## Repository Structure

```plain
.
├── .github/workflows/ci-cd.yml   # Full CI/CD pipeline
├── app/                          # Flask application
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── config.py
├── tests/
│   └── test_app.py               # pytest suite
├── load-tests/
│   └── load-test.js              # k6 script
├── policies/
│   └── docker.rego               # OPA policy
├── terraform/                    # IaC
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── Dockerfile
├── docker-compose.yml
├── sonar-project.properties
└── README.md
```

---

## Screenshots (Include in Submission)

| Screenshot | Location |
| ------------ | ---------- |
| pytest passing in GitHub Actions | Actions → test job |
| SonarCloud dashboard (before fixes) | SonarCloud → Issues |
| SonarCloud dashboard (after fixes) | SonarCloud → Issues (0 bugs) |
| Trivy FS scan results | Actions → security-scan-fs |
| Trivy image scan results | Actions → security-scan-image |
| k6 load test results | Actions → load-test |
| Conftest policy check passing | Actions → policy-check |
| EC2 instance running app | Browser → `http://<EC2_IP>/health` |
| GitHub Secrets page (redacted) | Settings → Secrets |

---

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run tests
pytest tests/ -v

# 3. Build and run Docker
docker build -t ostad-app .
docker run -d -p 5000:5000 -e SECRET_KEY=test ostad-app

# 4. Run load test
k6 run --env BASE_URL=http://localhost:5000 load-tests/load-test.js

# 5. Run policy check
conftest test Dockerfile --policy policies/docker.rego
```

---

## Bonus: Canary Deployment

See `docker-compose.canary.yml` and `nginx.conf` for a simulated blue-green deployment strategy on a single EC2 instance.

*Submitted for Assignment-15, Ostad DevOps Course*