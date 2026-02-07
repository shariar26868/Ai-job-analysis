# WireQuote AI Backend

AI-powered electrical quote estimation system using OpenAI and external pricing API.

## ✨ Features

- ✅ AI-powered job analysis using OpenAI GPT-4
- ✅ Integration with external pricing API for worker data
- ✅ Multi-worker quote comparison
- ✅ Emergency job support with automatic uplift
- ✅ **ElectricianId tracking** for each worker
- ✅ Automatic sorting by best price
- ✅ camelCase API responses for consistency

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-actual-key-here
PRICING_API_URL=http://10.0.70.141:5030/api/pricing/all
```

### 3. Run the Server
```bash
python app/main.py
```

Or using uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the API
```bash
python test_api.py
```

## 📡 API Endpoints

### 1. Get Worker Quotes (Multi-worker comparison)

**POST** `/api/v1/worker-quotes`

Get quotes from all available workers with **electricianId** included.

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
  "jobComplexity": "moderate",
  "aiReasoning": "Job involves installing multiple LED downlights...",
  "worker_quotes": [
    {
      "electricianId": "698459ad54091b0398eb9fbd",
      "workerName": "Chris Evans",
      "workerEmail": "chris.evans@wirequote.com",
      "workerLocation": "Reading, UK",
      "workerDescription": "Domestic electrician...",
      "estimatedHours": 3.5,
      "hourlyRate": 125.0,
      "callOutFee": 100.0,
      "labourCost": 437.5,
      "emergencyUplift": null,
      "totalQuote": 537.5,
      "jobComplexity": "moderate",
      "matchScore": 85.0,
      "recommendedActions": ["Check ceiling access", "Verify power supply"]
    }
  ],
  "totalWorkers": 2
}
```

### 2. Quick Estimate (AI Analysis Only)

**POST** `/api/v1/quick-estimate`

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
  "jobComplexity": "simple",
  "aiReasoning": "Simple switch replacement requiring minimal work",
  "recommendedActions": ["Check circuit breaker", "Test after installation"],
  "priority": "emergency",
  "status": "pending",
  "currency": "GBP"
}
```

### 3. Get All Workers

**GET** `/api/v1/workers`

**Response:**
```json
{
  "totalWorkers": 2,
  "workers": [
    {
      "electricianId": "698459ad54091b0398eb9fbd",
      "name": "Chris Evans",
      "email": "chris.evans@wirequote.com",
      "location": "Reading, UK",
      "description": "Domestic electrician...",
      "hourlyRate": 125.0,
      "callOutFee": 100.0,
      "minimum_charge": 125.0,
      "emergencyUplift_percent": 180.0
    }
  ]
}
```

### 4. Health Check

**GET** `/health`

### 5. Pricing Info

**GET** `/api/v1/pricing-info`

## 🔧 How It Works

### Worker Quotes Flow

1. **Client sends job description** → `/api/v1/worker-quotes`
2. **AI analyzes the job** → Estimates hours, complexity, actions
3. **System fetches all workers** → From external pricing API with **electricianId**
4. **Calculate quote for each worker** → Using their rates + AI estimates
5. **Sort by total price** → Lowest price first
6. **Return all quotes** → Client can compare and choose

### Pricing Calculation

For each worker:
```
labourCost = estimatedHours × worker.hourlyRate
emergencyUplift = labourCost × worker.emergencyUplift (if emergency)
totalQuote = worker.callOutFee + labourCost + emergencyUplift
totalQuote = max(totalQuote, worker.minimum_charge)
```

## 🗄️ External API Integration

The system fetches worker data from:
```
GET http://10.0.70.141:5030/api/pricing/all
```

**Expected Response Format:**
```json
[
  {
    "_id": {"$oid": "698459ba54091b0398eb9fbe"},
    "electricianId": {"$oid": "698459ad54091b0398eb9fbd"},
    "name": "Chris Evans",
    "email": "chris.evans@wirequote.com",
    "location": "Reading, UK",
    "description": "Domestic electrician with a focus on safety...",
    "hourlyRate": 125,
    "callOutFee": 100,
    "minimumCharge": 125,
    "emergencyUplift": 180,
    "currency": "GBP",
    "isActive": true,
    "createdAt": {"$date": "2026-02-05T08:50:02.335Z"},
    "updatedAt": {"$date": "2026-02-05T09:27:34.494Z"}
  }
]
```

### Important Notes:

- **electricianId** can be ObjectId format `{"$oid": "..."}` or string - both are handled
- **emergencyUplift** in API is percentage (180 = 180%), converted to decimal (1.80) internally
- Only **isActive: true** workers are included
- **camelCase** is used consistently in responses

## 📁 Project Structure

```
app/
├── main.py                    # FastAPI app
├── config.py                  # Settings (camelCase properties)
├── models.py                  # Data models (camelCase fields)
├── api/
│   └── routes.py             # API endpoints
└── services/
    ├── ai_service.py         # OpenAI integration
    ├── pricing_service.py    # External API integration
    └── quote_service.py      # Quote calculations
```

## 🎯 Key Features

### 1. ElectricianId Tracking
Every worker and quote includes `electricianId` for proper tracking and reference.

### 2. Flexible ID Handling
Handles MongoDB ObjectId format automatically:
```javascript
// Both formats work:
"electricianId": "698459ad54091b0398eb9fbd"
"electricianId": {"$oid": "698459ad54091b0398eb9fbd"}
```

### 3. camelCase Consistency
All API responses use camelCase for consistency:
- `estimatedHours` (not estimated_hours)
- `jobComplexity` (not job_complexity)
- `callOutFee` (not call_out_fee)

## 🛠️ Error Handling

- If pricing API is unavailable → Falls back to default worker
- If OpenAI fails → Uses keyword-based estimation
- All errors return proper HTTP status codes and messages

## 💻 Technology Stack

- **FastAPI** - Modern Python web framework
- **OpenAI GPT-4** - AI job analysis
- **Pydantic** - Data validation
- **HTTPX** - Async HTTP client for external API calls
- **Uvicorn** - ASGI server

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Run test suite
python test_api.py

# Manual testing with curl
curl -X POST http://localhost:8000/api/v1/worker-quotes \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Install 5 LED downlights",
    "is_emergency": false
  }'
```

## 📝 License

MIT