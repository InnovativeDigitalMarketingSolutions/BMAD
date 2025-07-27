# API Endpoint Template

## Endpoint Details
- **Method**: {{method}}
- **Path**: {{path}}
- **Description**: {{description}}

## Request
```json
{{request_schema}}
```

## Response
```json
{{response_schema}}
```

## Status Codes
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Example Usage
```bash
curl -X {{method}} {{base_url}}{{path}} \
  -H "Content-Type: application/json" \
  -d '{{request_example}}'
```

## Notes
{{notes}} 