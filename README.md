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
3. **Results:**

#### Load Test Summary

**Test Configuration:** k6 simulated up to **100 virtual users** over **2 minutes** across three stages (ramp to 50 VUs, sustain 100 VUs, ramp down). The test targeted a local Flask application backed by SQLite.

**Overall Result:** **Partially Failed** — The **p(95) latency threshold** (`< 500 ms`) was breached, while the **error rate threshold** (`< 5%`) passed comfortably.

---

#### Key Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| **Total Requests** | 14,535 | ~121 req/s throughput |
| **Iterations** | 4,845 | Each iteration = 3 requests (health + create + get) |
| **Error Rate** | **0.00%** | Excellent — only 1 HTTP request failed across the entire test |
| **Avg Response Time** | 136.39 ms | Acceptable under load |
| **p(95) Response Time** | **691.18 ms** | **Failed** threshold of 500 ms |
| **Max Response Time** | 6.22 s | Indicates sporadic latency spikes |

---

#### Check-Level Breakdown

| Check | Pass Rate | Notes |
|-------|-----------|-------|
| Health status `200` | 100% | App remained reachable |
| Health response `< 200 ms` | 100% | Lightweight endpoint performed well |
| Create task status `201` | 99% | 1 failure (likely a transient timeout or CSRF/token issue at peak load) |
| Create task response `< 500 ms` | **84%** | **Primary bottleneck** — 739 requests exceeded 500 ms |
| Get tasks status `200` | 100% | Read operations succeeded |
| Get tasks response `< 300 ms` | **80%** | 927 requests exceeded 300 ms |

---

#### Analysis

1. **Functional Stability:** The application did not crash. With a **0.00% HTTP failure rate**, the Flask app handled the concurrency functionally.
2. **Latency Degradation:** Under 100 VUs, the **p(95) latency hit 691 ms**, breaching the 500 ms threshold. The worst offenders were the **POST /tasks** and **GET /tasks** endpoints.
3. **Root Cause (Likely):** SQLite uses file-level locking. With 100 concurrent VUs hitting write operations (`POST`) and reads (`GET`) against a local SQLite database, contention and I/O blocking cause the observed tail latency (p95/p99) and the 6.22 s max spike. This is expected for a local file-based database under load.

---

#### Recommendation

For a production-like setup, replace SQLite with a proper RDBMS (PostgreSQL/MySQL) or use an in-memory store for load testing. For this assignment, the results are valid: you successfully simulated 100 users, measured response times, identified a latency threshold breach, and demonstrated that the application remains functionally stable (0% failures) even when performance degrades.

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
├── entrypoint.sh
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