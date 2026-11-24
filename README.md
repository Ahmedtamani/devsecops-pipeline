# DevSecOps Pipeline — built in public

A learning project: I build a small web API step by step, then the pipeline that automatically checks its security on every change. Each step is a commit, and each lesson is documented here.

> ⚠️ **Learning project.** Upcoming steps will add *intentionally vulnerable* code to practice detection and remediation. Do not deploy it.

## Current state

A Flask + SQLite API with three endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check, returns `{"status": "ok"}` |
| GET | `/users` | Lists all users, or filters with `?name=` |
| GET | `/users/<id>` | Returns one user, or `404` if not found |

Security choices already in place:
- **Parameterized SQL queries**: user input is never concatenated into SQL.
- **Typed routes** (`<int:user_id>`): non-integer IDs never reach the code or the database.

## Tests

6 tests with pytest, each one on an isolated temporary database:

- **Nominal cases**: health check, list, filter, get by ID
- **Error case**: unknown user returns `404`
- **Malicious case**: a SQL injection payload (`' OR '1'='1`) must return an empty list

That last one is a **security regression test**. To check it works, I temporarily replaced the parameterized query with an f-string: the 5 functional tests still passed, and only the security test failed, because the payload returned every user, including the admin. A vulnerability rarely breaks normal behavior; it only shows up when something actively tries to attack.

## Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
flask --app app.main run        # then: curl http://127.0.0.1:5000/health
```

## Roadmap

- [x] API + tests (nominal, error, malicious cases)
- [ ] Intentional vulnerabilities, exploited locally, then fixed
- [ ] Docker image: non-root user, production server instead of the Flask dev server
- [ ] CI pipeline: tests, secret scanning, static analysis, dependency scanning
- [ ] Supply chain: dependency lockfile, SBOM, image signing
- [ ] Deployment and security policies

## Notes for later

- The Flask dev server exposes `Server: Werkzeug/x.y Python/x.y` in every response (information disclosure). It will be replaced in the Docker step.
- `requirements.txt` pins Flask, but not its transitive dependencies. A lockfile is planned.

---

**Ahmed Tamani**, M2 Cybersecurity student at Polytech Nice Sophia, looking for a 6 months CyberSecurity internship from March 2027.
[LinkedIn](https://www.linkedin.com/in/ahmedtamani)