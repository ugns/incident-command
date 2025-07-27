# Incident Command API Architecture (Mermaid)

```mermaid
flowchart TD
    subgraph ICS API
        AGW[API Gateway]
        AGW -- /auth/login --> LambdaAuth[Lambda: auth_callback]
        AGW -- /openapi.json --> LambdaOpenAPI[Lambda: openapi_export]
        AGW -- /reports --> LambdaReports[Lambda: reports]
        AGW -- /reports/{reportType} --> LambdaReports[Lambda: reports]
        AGW -- /activitylogs --> LambdaActivityLogs[Lambda: activitylogs]
        AGW -- /activitylogs/{volunteerId} --> LambdaActivityLogs
        AGW -- /periods --> LambdaPeriods[Lambda: periods]
        AGW -- /periods/{periodId} --> LambdaPeriods
        AGW -- /volunteers --> LambdaVolunteers[Lambda: volunteers]
        AGW -- /volunteers/{volunteerId} --> LambdaVolunteers
        AGW -- /volunteers/{volunteerId}/dispatch --> LambdaVolunteers
        AGW -- /volunteers/{volunteerId}/checkin --> LambdaVolunteers
        AGW -- /volunteers/{volunteerId}/checkout --> LambdaVolunteers
    end

    subgraph Data
        LambdaAuth -- DynamoDB: volunteers, activity_logs --> DynamoDB[(DynamoDB)]
        LambdaReports -- DynamoDB: periods, activity_logs --> DynamoDB
        LambdaActivityLogs -- DynamoDB: activity_logs --> DynamoDB
        LambdaPeriods -- DynamoDB: periods --> DynamoDB
        LambdaVolunteers -- DynamoDB: volunteers, activity_logs --> DynamoDB
        LambdaOpenAPI -- API Gateway Export --> AGW
    end

    subgraph Infrastructure as Code
        Terraform[Terraform]
        Terraform --provisions--> AGW
        Terraform --provisions--> LambdaAuth
        Terraform --provisions--> LambdaReports
        Terraform --provisions--> LambdaActivityLogs
        Terraform --provisions--> LambdaPeriods
        Terraform --provisions--> LambdaVolunteers
        Terraform --provisions--> LambdaOpenAPI
        Terraform --provisions--> DynamoDB
    end
```

---

- All Lambda functions are provisioned and connected via Terraform.
- API Gateway routes requests to the appropriate Lambda handler.
- Lambdas interact with DynamoDB tables as needed.
- The OpenAPI export Lambda fetches the API spec from API Gateway.
- CORS and binary media types are configured in API Gateway via Terraform.
