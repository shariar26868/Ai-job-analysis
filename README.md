# WireQuote AI Backend

AI-powered electrical quote estimation system using OpenAI and external pricing API.

## Features

- ✅ AI-powered job analysis using OpenAI GPT-4
- ✅ Integration with external pricing API for worker data
- ✅ Multi-worker quote comparison
- ✅ Emergency job support with automatic uplift
- ✅ Automatic sorting by best price

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
PRICING_API_URL=http://10.0.70.141:5030/api/pricing/all
```

### 3. Run the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the main file:
```bash
python app/main.py
```

## API Endpoints

### 1. Get Worker Quotes (NEW)

**POST** `/api/v1/worker-quotes`

Get quotes from all available workers for a job.

**Request:**
```json
{
  "job_description": "Install 5 LED downlights in kitchen",
  "is_emergency": false,
  "customer_email": "customer@example.com"
}
```

**Response:**
```json
{
  "original_description": "Install 5 LED downlights in kitchen",
  "priority": "standard",
  "currency": "GBP",
  "estimatedHours": 3.5,
  "job_complexity": "moderate",
  "aiReasoning": "Job involves installing multiple LED downlights...",
  "worker_quotes": [
    {
      "workerName": "shahidul",
      "workerEmail": "shahidul@gmail.com",
      "workerLocation": "Bogura",
      "workerDescription": "this some thos fds",
      "estimatedHours": 3.5,
      "hourlyRate": 150.0,
      "callOutFee": 75.0,
      "labourCost": 525.0,
      "emergencyUplift": null,
      "totalQuote": 600.0,
      "job_complexity": "moderate",
      "matchScore": 85.0,
      "recommendedActions": ["Check ceiling access", "Verify power supply"]
    }
  ],
  "totalWorkers": 2
}
```

### 2. Quick Estimate (AI Analysis Only)

**POST** `/api/v1/quick-estimate`

Get AI analysis without worker-specific quotes.

**Request:**
```json
{
  "job_description": "Replace broken light switch",
  "is_emergency": true
}
```

**Response:**
```json
{
  "job_description": "Replace broken light switch",
  "estimatedHours": 1.0,
  "job_complexity": "simple",
  "aiReasoning": "Simple switch replacement requiring minimal work",
  "recommendedActions": ["Check circuit breaker", "Test after installation"],
  "priority": "emergency",
  "status": "pending",
  "currency": "GBP"
}
```

### 3. Get All Workers

**GET** `/api/v1/workers`

Fetch all active workers from the pricing API.

**Response:**
```json
{
  "totalWorkers": 2,
  "workers": [
    {
      "name": "shahidul",
      "email": "shahidul@gmail.com",
      "location": "Bogura",
      "description": "this some thos fds",
      "hourlyRate": 150.0,
      "callOutFee": 75.0,
      "minimum_charge": 150.0,
      "emergencyUplift_percent": 50.0
    }
  ]
}
```

### 4. Health Check

**GET** `/health`

Check API health status.

### 5. Pricing Info

**GET** `/api/v1/pricing-info`

Get default pricing configuration.

## How It Works

### Worker Quotes Flow

1. **Client sends job description** → `/api/v1/worker-quotes`
2. **AI analyzes the job** → Estimates hours, complexity, actions
3. **System fetches all workers** → From external pricing API (`http://10.0.70.141:5030/api/pricing/all`)
4. **Calculate quote for each worker** → Using their rates + AI estimates
5. **Sort by total price** → Lowest price first
6. **Return all quotes** → Client can compare and choose

### Pricing Calculation

For each worker:
```
Labour Cost = estimatedHours × worker.hourlyRate
Emergency Uplift = labourCost × worker.emergencyUplift (if emergency)
Total Quote = worker.callOutFee + labourCost + emergencyUplift
Total Quote = max(Total Quote, worker.minimum_charge)
```

### External API Integration

The system fetches worker data from:
```
GET http://10.0.70.141:5030/api/pricing/all
```

**Expected Response Format:**
```json
[
  {
    "id": "69846059d6cb62df181c739c",
    "electricianId": "69845e3cd6cb62df181c739a",
    "name": "shahidul",
    "email": "shahidul@gmail.com",
    "location": "Bogura",
    "description": "this some thos fds",
    "hourlyRate": 150,
    "callOutFee": 75,
    "minimumCharge": 150,
    "emergencyUplift": 50,
    "currency": "GBP",
    "isActive": true,
    "createdAt": "2026-02-05T09:18:17.418Z",
    "updatedAt": "2026-02-05T09:18:17.418Z"
  }
]
```

**Note:** `emergencyUplift` in API is percentage (e.g., 50 = 50%), converted to decimal (0.50) internally.

## Error Handling

- If pricing API is unavailable → Falls back to default worker
- If OpenAI fails → Uses keyword-based estimation
- All errors return proper HTTP status codes and messages

## Technology Stack

- **FastAPI** - Modern Python web framework
- **OpenAI GPT-4** - AI job analysis
- **Pydantic** - Data validation
- **HTTPX** - Async HTTP client for external API calls
- **Uvicorn** - ASGI server

## Development

### Run with Auto-Reload
```bash
uvicorn app.main:app --reload
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT