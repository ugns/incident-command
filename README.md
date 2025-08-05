# Incident Command API

This project provides a serverless API for managing security incident command operations, including volunteer check-in, dispatch, location tracking, and ICS-214 activity log generation. The API is built using AWS Lambda, API Gateway, and DynamoDB, and is provisioned via Terraform.

## Base URL

```
https://<api-id>.execute-api.<region>.amazonaws.com/<stage>
```

## Endpoints

### Authentication

  - Response:
    ```json
    {
      "token": "<backend_token>",
      "user": {
        "email": "string",
        "name": "string",
        "org_id": "string"
      }
    }
    ```

  - Notes:
    - The returned `token` must be sent in the `Authorization: Bearer <token>` header for all subsequent API requests.
    - This endpoint does not require authentication.

### Volunteers

- **GET /volunteers**
  - Description: List all volunteers
  - Response:
    ```json
    [ ...volunteer objects... ]
    ```

- **POST /volunteers**
  - Description: Add a new volunteer (check-in)
  - Request body:
    ```json
    {
      "name": "string",
      "contactInfo": "string",
      "currentLocation": "string",
      "notes": "string"
    }
    ```
  - Response:
    ```json
    {
      "volunteerId": "string"
    }
    ```

- **GET /volunteers/{volunteerId}**
  - Description: Get details for a volunteer
  - Response:
    ```json
    { ...volunteer object... }
    ```

- **PUT /volunteers/{volunteerId}**
  - Description: Update volunteer info/status/location
  - Request body: any updatable volunteer fields
  - Response: `204 No Content`

- **POST /volunteers/{volunteerId}/dispatch**
  - Description: Dispatch a volunteer (update status/location, log event)
  - Request body:
  - Response: `204 No Content`

- **POST /volunteers/{volunteerId}/checkin**
  - Description: Check in a volunteer for a new day (multi-day check-in)
  - Request body:
    ```json
    {
      "checkin_time": "2024-06-01T08:00:00Z"
    }
    ```
    (Optional, defaults to now)
  - Response:
    ```json
    {
      "message": "Volunteer checked in",
      "volunteerId": "abc123",
      "checkin_time": "2024-06-01T08:00:00Z"
    }
    ```

- **POST /volunteers/{volunteerId}/checkout**
  - Description: Check out a volunteer (update status, log event)
  - Response: `204 No Content`

### Activity Logs

- **GET /activitylogs**
  - Description: List all activity logs
  - Response:
    ```json
    [ ...activity log objects... ]
    ```

- **GET /activitylogs/{volunteerId}**
  - Description: List activity logs for a specific volunteer
  - Response:
    ```json
    [ ...activity log objects... ]
    ```

### ICS-214

- **POST /periods**
  - Description: Create a new ICS-214 operating period
  - Request body:
    ```json
    {
      "startTime": "string (optional)",
      "endTime": "string (optional)",
      "name": "string",
      ...additional metadata...
    }
    ```
  - Response:
    ```json
    {
      "periodId": "string",
      "startTime": "string",
      "endTime": "string",
      "name": "string",
      ...additional metadata...
    }
    ```

- **GET /periods**
  - Description: List all ICS-214 operating periods
  - Response:
    ```json
    [ 
      {
        "periodId": "string",
        "startTime": "string",
        "endTime": "string",
        "name": "string",
        ...additional metadata...
      }
    ]
    ```

- **GET /periods/{periodId}**
  - Description: Get ICS-214 log for a specific operating period
  - Response:
    ```json
    [ ...activity log objects for the period... ]
    ```

- **PUT /periods/{periodId}**
  - Description: Update an ICS-214 operating period (e.g., close period by setting end_time)
  - Request body:
    ```json
    {
      "startTime": "string",
      "endTime": "string",
      "name": "string",
      ...additional metadata...
    }
    ```
  - Response: `204 No Content`

- **DELETE /periods/{periodId}**
  - Description: Delete an ICS-214 operating period
  - Response: `204 No Content`

- **GET /ics214**
  - Description: Get activity logs for the current day by default. If a `periodId` query parameter is provided, returns logs for that period instead.
  - Query string: `?periodId=<period_id>` (optional)
  - Response:
    ```json
    [ ...activity log objects... ]
    ```



## Models

### Volunteer

```json
{
  "volunteerId": "string",
  "org_id": "string",
  "name": "string",
  "contactInfo": "string",
  "currentLocation": "string",
  "notes": "string",
  "status": "string",
  ...additional metadata...
}
```

### Activity Log

```json
{
  "logId": "string",
  "org_id": "string",
  "periodId": "string",
  "volunteerId": "string",
  "timestamp": "ISO8601 string",
  "action": "string",
  "location": "string",
  "details": "string",
  ...additional metadata...
}
```

### Period

```json
{
  "periodId": "string",
  "org_id": "string",
  "startTime": "ISO8601 string",
  "endTime": "ISO8601 string",
  "name": "string",
  ...additional metadata...
}
```

## CORS

All endpoints support CORS (OPTIONS preflight requests and appropriate headers).

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
