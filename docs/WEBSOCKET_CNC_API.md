# WebSocket Command & Control (CNC) API Design

## Overview
This document describes the WebSocket-based CNC API for real-time updates in the incident-command system. It is designed to work alongside the existing REST API, using AWS API Gateway (WebSocket), Lambda, and DynamoDB.

---

## WebSocket Routes

| Route         | Purpose                | Lambda Handler         |
|---------------|------------------------|------------------------|
| $connect      | Handle new connection  | wsConnectLambda        |
| $disconnect   | Handle disconnect      | wsDisconnectLambda     |
| $default      | Handle client messages | wsDefaultLambda        |

---

## Message Types (Backend → Frontend)

| Type                | Payload Example                                      | Triggers Frontend Action         |
|---------------------|------------------------------------------------------|----------------------------------|
| volunteersUpdated   | `{ "type": "volunteersUpdated", "orgId": "...", "periodId": "..." }`     | refreshVolunteers()              |
| assignmentsUpdated  | `{ "type": "assignmentsUpdated", "orgId": "...", "periodId": "..." }`    | refreshAssignments()             |
| periodsUpdated      | `{ "type": "periodsUpdated", "orgId": "..." }`                  | refreshPeriods()                 |
| unitsUpdated        | `{ "type": "unitsUpdated", "orgId": "..." }`                    | refreshUnits()                   |
| incidentsUpdated    | `{ "type": "incidentsUpdated", "orgId": "..." }`                | refreshIncidents()               |

---

## Integrations

- **DynamoDB Table:** `WebSocketConnections` (stores connectionId, orgId, userId, subscriptions)
- **Lambda Triggers:** On relevant data change (API or DynamoDB Stream), send message to clients via API Gateway Management API

---

## Authentication

- The JWT issued by the `/auth/login` REST endpoint is required for the WebSocket `$connect` route.
- Lambda should validate the JWT and extract user/org info on connect.

---

## Example Flow

1. Client connects to WebSocket API, sending JWT in the connection request.
2. Backend validates JWT, stores connection info in DynamoDB.
3. When a relevant change occurs (e.g., assignment update), Lambda sends a message to all interested clients.
4. Frontend receives the message and triggers the appropriate context refresh.

---

## Notes
- The REST API remains the source of truth for all CRUD operations.
- The WebSocket API is for real-time notifications only.
- Message types and payloads can be extended as needed.

---

_Last updated: 2025-07-30_
