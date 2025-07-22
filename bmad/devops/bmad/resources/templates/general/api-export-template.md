# API Export Template

## API Overview
- **Version:** 1.0.0
- **Base URL:** https://api.example.com/v1
- **Authentication:** Bearer Token
- **Rate Limit:** 1000 requests/hour

## Endpoints

### GET /api/v1/users
- **Description:** Retrieve user list
- **Parameters:** page, limit, search
- **Response:** User array
- **Status:** Active

### POST /api/v1/users
- **Description:** Create new user
- **Body:** User object
- **Response:** Created user
- **Status:** Active

### PUT /api/v1/users/{id}
- **Description:** Update user
- **Body:** User object
- **Response:** Updated user
- **Status:** Active

### DELETE /api/v1/users/{id}
- **Description:** Delete user
- **Response:** Success message
- **Status:** Active

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error