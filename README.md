# Module 5 Part 3 YMB Banking Services

Sharhan Kaji, Student ID 0424551.

This local teaching prototype links a static student portfolio, Flask banking
service, MongoDB database and JavaScript monthly transaction report service
through one NGINX gateway. It extends the supplied Module 5 Part 3 starter.

## Run

Install Docker Desktop with Linux containers. Copy `.env.example` to `.env`
and replace the example session key with a random value. Never commit `.env`.
Run `docker compose up --build -d --wait` in this folder and open
http://localhost. Follow View Banking App to register and log in.
Only NGINX publishes a host port, bound to 127.0.0.1:80 for this local lab.
The backend, database and transactions services have no published host ports.

## Routing and boundaries

- `/` routes to studentportfolio:80.
- `/api/` routes to backend:5000 without removing the `/api/` prefix.
- `/api/transactions` and its trailing-slash form route to transactions:3000.
- The report route first uses an NGINX internal auth_request to validate the
  Flask session. NGINX overwrites X-User-ID with the verified identity.
- MongoDB is on an internal data network. The frontend and gateway do not
  join that network. Backend and transactions use the same bank_app database
  because that is the supplied lab design, not database-per-service isolation.
- NGINX access logs record timestamp, route, status and upstream address.

`docker-compose.annotated.yml` explains the service blocks. The clean
`docker-compose.yml` is the runnable submission file. Compose uses the
current specification, so a deprecated top-level version field is omitted.
YAML order documents dependencies; depends_on with service_healthy enforces
runtime readiness. It does not force dependency images to build first.

## Tests and CI

Backend: `cd backend` then `python -m pytest tests/ -q`.
JavaScript: `cd transactions/src` then `npm ci` and `npm test`.
Real stack: run `python scripts/smoke_test.py` from this folder after startup.
The smoke test registers a unique disposable test account, exercises decimal
amounts and reports, checks logout, and checks that direct ports are closed.

The build-and-test job in `.github/workflows/ci.yml` checks pushes and pull
requests to main, runs both language test suites, builds images and checks
the real stack. It fails on a failed test and always cleans its own CI
containers and volume. It does not deploy to production. Branch protection
must be configured separately to require this job before merging.

Create the required repository `module5-part3-Sharhan-rrc`, push this folder
as the repository root, verify a real green Actions run and invite the exact
instructor account. A local test result is not a GitHub Actions run.

## Changes from the starter

Branding and student profile were updated. The Flask Part 3 app gains only
a session-identity endpoint for gateway authentication; the supplied banking
logic and tests are retained. The JavaScript report is integrated with that
identity check so the gateway actually uses the JavaScript service. Extra
tests check balances and the identity handoff. The Node base is version 22,
and npm uses the checked-in lockfile. The service runs as the node user.

## YMB context and limits

The case study V4.2 describes 24/7 availability and 99.99% uptime on page 43,
secure network zones and internal visibility on page 49, development and
pipeline support on pages 54-55, and internal logging gaps on page 121.
These motivate Kevin AllGood's availability concern, Chris Fun's gateway
boundary and Ben Secure's testing/audit requirements from the Module 5 brief.
This single-host prototype is not highly available. The gateway is a single
point of failure. A volume is persistence, not a backup or tested DR plan.

The supplied bank logic uses floating-point balances, has no real OTP for
large amounts, and retains legacy Flask dependencies. It is for coursework,
not real customer data or money. A production system needs decimal money
types, atomic updates, CSRF protection, TLS, database authentication,
dependency/security scanning, external secrets and tested recovery.

Stop with `docker compose down` after evidence is saved. Use `down -v` only
when intentionally discarding this project's test accounts. Never run a
global image prune to clean this assignment; it may affect other coursework.

## References

- Supplied Module 5 Assignment instructions and starter archives.
- Yarrow-Mullein Bank Case Study 2025-2026 V4.2, pp. 43, 49, 54-55, 104, 121.
- https://docs.docker.com/compose/how-tos/startup-order/
- https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- https://docs.github.com/en/actions/get-started/quickstart
