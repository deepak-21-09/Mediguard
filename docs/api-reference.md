# API Reference

This document describes backend API endpoints, request payloads, and expected responses.

> All API routes are served from `http://localhost:8000` in local development.

## Authentication

### `POST /api/v1/auth/register`

Register a new user or sync user data.

Request body:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "Jane Doe"
}
```

Response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "user@example.com" }
}
```

### `POST /api/v1/auth/token`

Issue a JWT for development mode.

Request body:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

Response:

```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

### `GET /api/v1/auth/supabase/status`

Check Supabase connectivity.

Response:

```json
{ "configured": true, "url": "https://...supabase.co", "status": "connected" }
```

## Profile

### `GET /api/v1/profile`

Get the authenticated user's profile.

Response:

```json
{
  "id": 1,
  "user_id": 1,
  "age": 45,
  "gender": "female",
  "blood_type": "O+",
  "allergies": ["penicillin"],
  "conditions": ["hypertension"]
}
```

### `PUT /api/v1/profile`

Update the user's profile.

Request body:

```json
{
  "age": 45,
  "weight": 72,
  "blood_type": "O+",
  "allergies": ["penicillin"],
  "conditions": ["hypertension"]
}
```

Response:

```json
{ "success": true, "profile": { ... } }
```

### `GET /api/v1/profile/emergency-card`

Get emergency card information.

Response:

```json
{
  "blood_type": "O+",
  "allergies": ["penicillin"],
  "active_medications": [ ... ],
  "emergency_contact": { "name": "John Doe", "phone": "123-456-7890" }
}
```

## Medications

### `GET /api/v1/medications`

List medications for the authenticated user.

Response:

```json
[ { "id": 1, "name": "Metformin", "dosage": "500mg", "frequency": "twice daily" } ]
```

### `POST /api/v1/medications`

Add a medication.

Request body:

```json
{
  "name": "Metformin",
  "dosage": "500mg",
  "frequency": "twice daily",
  "start_date": "2026-08-01",
  "doctor": "Dr. Smith"
}
```

Response:

```json
{ "id": 1, "name": "Metformin", "status": "active" }
```

### `PUT /api/v1/medications/{id}`

Update an existing medication.

Request body:

```json
{ "dosage": "1000mg", "frequency": "once daily" }
```

Response:

```json
{ "success": true, "medication": { ... } }
```

### `DELETE /api/v1/medications/{id}`

Delete a medication.

Response:

```json
{ "success": true }
```

### `POST /api/v1/medications/scan-prescription`

Upload a prescription image for OCR extraction.

Request body must be `multipart/form-data` with an `image` file.

Response:

```json
{
  "medications": [ { "name": "Lisinopril", "dosage": "10mg" } ]
}
```

## Symptoms

### `GET /api/v1/symptoms`

List symptom logs.

Response:

```json
[ { "id": 1, "description": "Nausea", "severity": "moderate" } ]
```

### `POST /api/v1/symptoms`

Log a symptom.

Request body:

```json
{ "description": "Nausea", "severity": "moderate", "notes": "After breakfast" }
```

Response:

```json
{ "id": 1, "analysis": "Possible Metformin side effect" }
```

## Appointments

### `GET /api/v1/appointments`

Retrieve appointments.

Response:

```json
[ { "id": 1, "date": "2026-09-10", "doctor": "Dr. Lee" } ]
```

### `POST /api/v1/appointments`

Create an appointment.

Request body:

```json
{ "date": "2026-09-10", "doctor": "Dr. Lee", "notes": "Annual checkup" }
```

Response:

```json
{ "id": 1, "date": "2026-09-10" }
```

### `POST /api/v1/appointments/{id}/summary`

Generate an AI pre-visit summary.

Response:

```json
{ "summary": "Your medication history and symptom timeline for the appointment..." }
```

## Reminders

### `GET /api/v1/reminders`

List reminders.

Response:

```json
[ { "id": 1, "title": "Take Metformin", "time": "08:00" } ]
```

### `POST /api/v1/reminders`

Create a reminder.

Request body:

```json
{ "title": "Take Metformin", "time": "08:00", "repeat": "daily" }
```

Response:

```json
{ "id": 1, "success": true }
```

## Chat

### `POST /api/v1/chat`

Send a message to MedAgent.

Request body:

```json
{ "message": "Do these two meds interact?" }
```

Response:

```json
{ "reply": "There is a low-severity interaction between..." }
```

### `GET /api/v1/chat/sessions`

List AI chat sessions.

Response:

```json
[ { "session_id": 1, "created_at": "2026-08-10T12:00:00Z" } ]
```

## Reports

### `GET /api/v1/reports/health-report.pdf`

Download a generated PDF report.

Response: PDF file stream.

## Dashboard

### `GET /api/v1/dashboard`

Get aggregated dashboard data.

Response:

```json
{ "medication_count": 4, "uptime": 98, "next_appointment": "2026-09-10" }
```

## Health

### `GET /health`

Check server health and active environment.

Response:

```json
{ "status": "ok", "environment": "development", "database": "sqlite" }
```

## Notes

- All protected endpoints require a valid bearer token.
- Use `Authorization: Bearer <token>` header for authenticated requests.
- If the app is configured with Supabase, the auth flow may include Supabase or Clerk token validation.
