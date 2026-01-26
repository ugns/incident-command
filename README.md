
# Incident Command API

This project provides a robust, serverless API for managing incident command operations, including volunteer check-in, dispatch, location tracking, ICS-214 activity log generation, and organizational resources. The API is built using AWS Lambda, API Gateway, and DynamoDB, with infrastructure managed via Terraform. Shared code and models ensure consistency and production-readiness.

---

## Base URL

```
https://<api-id>.execute-api.<region>.amazonaws.com/<stage>
```

Replace `<api-id>`, `<region>`, and `<stage>` with your actual API Gateway values.

---

## Architecture & Conventions

- **Serverless API**: AWS Lambda handlers (one per resource) in `lambda/`
- **Shared code**: Models, utilities, feature flags, and auth in `src/EventCoord/` (packaged into the `shared/` Lambda layer via `make install-deps`)
- **Infrastructure as code**: Terraform in `terraform/` (DynamoDB, Lambda, API Gateway)
- **CI/CD**: Build/package via Makefile and GitHub Actions
- **Auth**: JWT-based, user info in claims; all protected endpoints require `Authorization` header
- **Feature flags**: LaunchDarkly via `shared/launchdarkly/flags.py`
- **DynamoDB**: All tables scoped by `org_id` (partition key), resource-specific sort keys, GSIs for secondary queries
- **Model methods**: CRUD and GSI helpers per resource
- **Response utility**: All handlers use `build_response` from `src/EventCoord/utils/response.py`
- **CORS**: All endpoints support OPTIONS preflight and CORS headers

---

## Endpoints

All endpoints require JWT authentication unless otherwise noted. All requests and responses use JSON. Resource IDs are passed via path parameters, and POST/PUT bodies are JSON.

### Authentication
- **POST /auth/login**: Authenticate and receive JWT

### Volunteers
- **GET /volunteers**: List all volunteers
- **POST /volunteers**: Add a new volunteer (check-in)
- **GET /volunteers/{volunteerId}**: Get details for a volunteer
- **PUT /volunteers/{volunteerId}**: Update volunteer info/status/location
- **POST /volunteers/{volunteerId}/dispatch**: Dispatch a volunteer (update status/location, log event)
- **POST /volunteers/{volunteerId}/checkin**: Check in a volunteer for a new day (multi-day check-in)
- **POST /volunteers/{volunteerId}/checkout**: Check out a volunteer (update status, log event)

### Activity Logs
- **GET /activitylogs**: List all activity logs
- **GET /activitylogs/{volunteerId}**: List activity logs for a specific volunteer

### ICS-214 Periods
- **POST /periods**: Create a new ICS-214 operating period
- **GET /periods**: List all ICS-214 operating periods
- **GET /periods/{periodId}**: Get ICS-214 log for a specific operating period
- **PUT /periods/{periodId}**: Update an ICS-214 operating period (e.g., close period by setting end_time)
- **DELETE /periods/{periodId}**: Delete an ICS-214 operating period

### ICS-214 Logs
- **GET /ics214**: Get activity logs for the current day by default. If a `periodId` query parameter is provided, returns logs for that period instead.

### Organizations
- **GET /organizations**: List all organizations
- **GET /organizations/{org_id}**: Get details for an organization
- **POST /organizations**: Create a new organization
- **PUT /organizations/{org_id}**: Update organization info
- **DELETE /organizations/{org_id}**: Delete an organization

### Units
- **GET /units**: List all units
- **GET /units/{unitId}**: Get details for a unit
- **POST /units**: Create a new unit
- **PUT /units/{unitId}**: Update unit info
- **DELETE /units/{unitId}**: Delete a unit

### Locations
- **GET /locations**: List all locations
- **GET /locations/{locationId}**: Get details for a location
- **POST /locations**: Create a new location
- **PUT /locations/{locationId}**: Update location info
- **DELETE /locations/{locationId}**: Delete a location

### Radios
- **GET /radios**: List all radios
- **GET /radios/{radioId}**: Get details for a radio
- **POST /radios**: Create a new radio
- **PUT /radios/{radioId}**: Update radio info
- **DELETE /radios/{radioId}**: Delete a radio

### Reports
- **GET /reports**: List all reports
- **GET /reports/{reportType}**: Get a specific report
- **POST /reports/{reportType}**: Generate a report

---

## Models

All models are defined in `shared/models/` and provide CRUD and GSI query helpers. All tables are scoped by `org_id` (partition key). Key model methods follow the pattern: `create(org_id, item: dict)`, `update(org_id, id, item: dict)`, `list(org_id)`, and resource-specific GSI queries.

### Volunteer
- Fields: `volunteerId`, `org_id`, `name`, `email`, `status`, `location`, `checkin_time`, `checkout_time`, ...
- Methods:
  - `Volunteer.get_or_create_by_email(org_id, email)`
  - `Volunteer.list(org_id)`
  - `Volunteer.create(org_id, item)`
  - `Volunteer.update(org_id, volunteerId, item)`

### ActivityLog
- Fields: `activityLogId`, `org_id`, `volunteerId`, `timestamp`, `activity`, ...
- Methods:
  - `ActivityLog.list_by_volunteer(org_id, volunteerId)`
  - `ActivityLog.create(org_id, item)`

### Period
- Fields: `periodId`, `org_id`, `startTime`, `endTime`, `name`, ...
- Methods:
  - `Period.list(org_id)`
  - `Period.create(org_id, item)`
  - `Period.update(org_id, periodId, item)`
  - `Period.list_by_unit(org_id, unitId)`

### Organization
- Fields: `org_id`, `name`, `contact`, ...
- Methods:
  - `Organization.list()`
  - `Organization.create(item)`
  - `Organization.update(org_id, item)`

### Unit
- Fields: `unitId`, `org_id`, `name`, `type`, ...
- Methods:
  - `Unit.list(org_id)`
  - `Unit.create(org_id, item)`
  - `Unit.update(org_id, unitId, item)`

### Location
- Fields: `locationId`, `org_id`, `name`, `coordinates`, ...
- Methods:
  - `Location.list(org_id)`
  - `Location.create(org_id, item)`
  - `Location.update(org_id, locationId, item)`

### Radio
- Fields: `radioId`, `org_id`, `serial`, `assignedTo`, ...
- Methods:
  - `Radio.list(org_id)`
  - `Radio.create(org_id, item)`
  - `Radio.update(org_id, radioId, item)`

### Report
- Fields: `reportType`, `org_id`, `generatedAt`, `data`, ...
- Methods:
  - `Report.list(org_id)`
  - `Report.generate(org_id, reportType, params)`

All models use DynamoDB tables and GSIs as defined in Terraform. For details, see `shared/models/<resource>.py`.

---

## Deployment

- Infrastructure is managed with Terraform in the `terraform/` directory:
  - Lambda functions: `lambda.tf`
  - DynamoDB tables: `dynamodb.tf`
  - API Gateway: `api_gateway_<resource>.tf` (one per model)
  - IAM policies include table and GSI ARNs for all models
- Lambda source code is in the `lambda/` directory (one handler per resource)
- Shared code (models, utils, feature flags, auth) is in `src/EventCoord/` and is packaged into the Lambda Layer at `shared/` via `make install-deps`
- See `requirements.txt` for Python dependencies
- Build Lambda Layer: `make install-deps` (creates `shared/` for Terraform to zip)
- Local dev venv: `make dev-venv`
- Deploy: `terraform apply` in `terraform/`
- CI/CD: Artifacts built and uploaded via GitHub Actions (see workflow YAML)

---

## Notes

- All DynamoDB tables are scoped by `org_id` and use resource-specific sort keys. See Terraform for table and GSI names.
- All timestamps are in ISO8601 UTC format.
- Feature flags are checked via LaunchDarkly (`shared/launchdarkly/flags.py`).
- All handlers use shared code and standard response utilities.
- Error handling: Handlers return consistent error responses (400 for missing IDs, 404 for not found, 405 for method not allowed)

---

For questions or contributions, please open an issue or pull request.

### ICS-214 Periods
- **POST /periods**: Create a new ICS-214 operating period
- **GET /periods**: List all ICS-214 operating periods
- **GET /periods/{periodId}**: Get ICS-214 log for a specific operating period
- **PUT /periods/{periodId}**: Update an ICS-214 operating period (e.g., close period by setting end_time)
- **DELETE /periods/{periodId}**: Delete an ICS-214 operating period

### ICS-214 Logs
- **GET /ics214**: Get activity logs for the current day by default. If a `periodId` query parameter is provided, returns logs for that period instead.

### Organizations
- **GET /organizations**: List all organizations
- **GET /organizations/{org_id}**: Get details for an organization
- **POST /organizations**: Create a new organization
- **PUT /organizations/{org_id}**: Update organization info
- **DELETE /organizations/{org_id}**: Delete an organization

### Units
- **GET /units**: List all units
- **GET /units/{unitId}**: Get details for a unit
- **POST /units**: Create a new unit
- **PUT /units/{unitId}**: Update unit info
- **DELETE /units/{unitId}**: Delete a unit

### Locations
- **GET /locations**: List all locations
- **GET /locations/{locationId}**: Get details for a location
- **POST /locations**: Create a new location
- **PUT /locations/{locationId}**: Update location info
- **DELETE /locations/{locationId}**: Delete a location

### Radios
- **GET /radios**: List all radios
- **GET /radios/{radioId}**: Get details for a radio
- **POST /radios**: Create a new radio
- **PUT /radios/{radioId}**: Update radio info
- **DELETE /radios/{radioId}**: Delete a radio

### Reports
- **GET /reports**: List all reports
- **GET /reports/{reportType}**: Get a specific report
- **POST /reports/{reportType}**: Generate a report
## Deployment

- Infrastructure is managed with Terraform in the `terraform/` directory.
- Lambda source code is in the `lambda/` directory.
- See `requirements.txt` for Python dependencies.

## Notes

- Replace `<api-id>`, `<region>`, and `<stage>` with your actual API Gateway values.
- DynamoDB tables: `volunteers`, `activity_logs`.
- All timestamps are in ISO8601 UTC format.

---

For questions or contributions, please open an issue or pull request.
