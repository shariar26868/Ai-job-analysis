# Quote Persistence Layer

## Overview

The backend now includes a complete quote persistence and tracking system using MongoDB. This allows quotes to be saved, retrieved, and managed through the API.

## Features

✅ **Save Quotes** - Generate and persist quotes to database  
✅ **Retrieve Quotes** - Get quotes by ID, electrician, or customer email  
✅ **Track Status** - Update quote status (pending → accepted/rejected)  
✅ **Quote History** - Maintain complete audit trail with timestamps  
✅ **Error Handling** - Graceful degradation if database unavailable  

## Database Schema

### Quote Collection

```mongodb
{
  "_id": ObjectId,
  "electricianId": string,
  "electricianName": string,
  "electricianEmail": string,
  "job_description": string,
  "estimatedHours": float,
  "jobComplexity": "simple|moderate|complex",
  "callOutFee": float,
  "hourlyRate": float,
  "labourCost": float,
  "emergencyUplift": float | null,
  "minimumCharge": float,
  "totalQuote": float,
  "isEmergency": boolean,
  "status": "pending|accepted|rejected",
  "aiReasoning": string,
  "customerEmail": string | null,
  "createdAt": ISODate,
  "updatedAt": ISODate
}
```

## API Endpoints

### 1. Save a Quote
```http
POST /api/v1/quotes/save
Content-Type: application/json

{
  "electricianId": "123",
  "electricianName": "John Smith",
  "electricianEmail": "john@example.com",
  "job_description": "Install 10 LED downlights",
  "estimatedHours": 3.5,
  "jobComplexity": "moderate",
  "callOutFee": 65.0,
  "hourlyRate": 100.0,
  "labourCost": 350.0,
  "emergencyUplift": null,
  "minimumCharge": 65.0,
  "totalQuote": 415.0,
  "priority": "standard",
  "aiReasoning": "Standard LED installation work"
}

Response (201 Created):
{
  "id": "507f1f77bcf86cd799439011",
  "electricianId": "123",
  "electricianName": "John Smith",
  "status": "pending",
  "totalQuote": 415.0,
  "createdAt": "2026-05-08T10:30:00Z",
  "updatedAt": "2026-05-08T10:30:00Z",
  ...
}
```

### 2. Get Quote by ID
```http
GET /api/v1/quotes/{quote_id}

Response (200 OK):
{
  "id": "507f1f77bcf86cd799439011",
  "electricianId": "123",
  "electricianName": "John Smith",
  "status": "pending",
  "totalQuote": 415.0,
  ...
}
```

### 3. Get Electrician's Quotes
```http
GET /api/v1/quotes/history/electrician/{electrician_id}

Response (200 OK):
[
  {
    "id": "507f1f77bcf86cd799439011",
    "electricianId": "123",
    "status": "pending",
    ...
  },
  ...
]
```

### 4. Get Customer's Quotes
```http
GET /api/v1/quotes/history/customer/{customer_email}

Response (200 OK):
[
  {
    "id": "507f1f77bcf86cd799439011",
    "customerEmail": "customer@example.com",
    "status": "accepted",
    ...
  },
  ...
]
```

### 5. Get All Quotes (with optional filtering)
```http
GET /api/v1/quotes?status_filter=pending&limit=50

Query Parameters:
  - status_filter: pending|accepted|rejected (optional)
  - limit: Maximum quotes to return (default 100)

Response (200 OK):
[
  {...},
  {...}
]
```

### 6. Update Quote Status
```http
PATCH /api/v1/quotes/{quote_id}/status
Content-Type: application/json

{
  "status": "accepted",
  "notes": "Customer confirmed and ready to proceed"
}

Response (200 OK):
{
  "id": "507f1f77bcf86cd799439011",
  "status": "accepted",
  "updatedAt": "2026-05-08T11:00:00Z",
  ...
}
```

### 7. Delete Quote
```http
DELETE /api/v1/quotes/{quote_id}

Response (204 No Content)
```

## Environment Configuration

Add to `.env`:

```dotenv
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=wirequote_db
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MongoDB
```bash
# Using Docker (recommended)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or using Docker Compose
docker-compose up -d
```

### 3. Run Application
```bash
python run.py
```

The application will automatically:
- Connect to MongoDB on startup
- Create necessary indexes
- Run in degraded mode if database is unavailable

## Error Handling

### Database Unavailable
If MongoDB is not running, the application will:
1. Log a warning during startup
2. Continue running in degraded mode
3. Return 503 Service Unavailable for persistence endpoints
4. Quote generation endpoints continue to work

### Quote Not Found
```json
{
  "detail": "Quote with ID '507f1f77bcf86cd799439011' not found"
}
```
Status: 404 Not Found

### Invalid Status Update
```json
{
  "detail": "Invalid status. Must be one of: pending, accepted, rejected"
}
```
Status: 400 Bad Request

## Data Retention

- Quotes are automatically deleted after 90 days (TTL index)
- Indexes are automatically created on first connection
- Database supports horizontal scaling with MongoDB Atlas

## Testing

```bash
# Test saving a quote
curl -X POST http://localhost:8001/api/v1/quotes/save \
  -H "Content-Type: application/json" \
  -d '{"electricianId":"123",...}'

# Test retrieving a quote
curl http://localhost:8001/api/v1/quotes/507f1f77bcf86cd799439011

# Test updating status
curl -X PATCH http://localhost:8001/api/v1/quotes/507f1f77bcf86cd799439011/status \
  -H "Content-Type: application/json" \
  -d '{"status":"accepted"}'
```

## Performance Considerations

- Indexes created on: `electricianId`, `customerEmail`, `status`, `createdAt`
- TTL index automatically removes old quotes after 90 days
- Queries are optimized for common patterns (by electrician, by customer, by status)
- Connection pooling enabled in Motor async driver

## Security Notes

- All database operations use parameterized queries (safe from injection)
- No sensitive data logged in database
- MongoDB connection string should use environment variables
- Consider using MongoDB authentication in production
