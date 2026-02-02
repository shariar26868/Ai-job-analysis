# 🔌 WireQuote AI Backend

AI-powered electrical quote estimation system using OpenAI GPT-4 and FastAPI.

## 🌟 Features

- ✅ AI-powered job analysis using OpenAI
- ✅ Intelligent time estimation
- ✅ Automatic price calculation
- ✅ Emergency job handling with uplift pricing
- ✅ Job complexity assessment
- ✅ Recommended actions for each job
- ✅ RESTful API with FastAPI
- ✅ CORS enabled for frontend integration
- ✅ Comprehensive error handling
- ✅ Interactive API documentation (Swagger UI)

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- pip (Python package manager)

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd wirequote-ai-backend
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Get your OpenAI API key from: https://platform.openai.com/api-keys

## 🎯 Running the Application

### Method 1: Using run.py

```bash
python run.py
```

### Method 2: Using uvicorn directly

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### 1. Analyze Job - Multiple Suggestions (NEW! ⭐)

**POST** `/api/v1/analyze-job-multiple`

Get **MULTIPLE AI-powered suggestions** for a job, sorted by confidence/match percentage.

**Request Body:**
```json
{
  "job_description": "Install 5 new LED downlights in the kitchen. The ceiling is plasterboard and there's existing lighting I want to replace.",
  "is_emergency": false
}
```

**Response:**
```json
{
  "original_description": "Install 5 new LED downlights...",
  "priority": "standard",
  "currency": "GBP",
  "total_suggestions": 3,
  "suggestions": [
    {
      "job_title": "Kitchen LED Downlight Installation",
      "job_description": "Install 5 LED downlights with existing wiring replacement",
      "estimated_hours": 3.5,
      "calculated_price": 415.0,
      "call_out_fee": 65.0,
      "labour_cost": 350.0,
      "emergency_uplift": null,
      "job_complexity": "moderate",
      "confidence_score": 95.0,
      "match_reason": "Description clearly specifies 5 LED downlights in kitchen with plasterboard ceiling",
      "recommended_actions": [
        "Verify ceiling access for wiring",
        "Confirm LED compatibility with existing circuit",
        "Schedule electrical safety testing"
      ]
    },
    {
      "job_title": "Basic LED Downlight Replacement",
      "job_description": "Simple replacement of 5 downlight fixtures",
      "estimated_hours": 2.0,
      "calculated_price": 265.0,
      "call_out_fee": 65.0,
      "labour_cost": 200.0,
      "emergency_uplift": null,
      "job_complexity": "simple",
      "confidence_score": 75.0,
      "match_reason": "If only fixture replacement without rewiring",
      "recommended_actions": [
        "Confirm fixtures are compatible",
        "Quick installation possible"
      ]
    },
    {
      "job_title": "Comprehensive Kitchen Lighting Upgrade",
      "job_description": "Full kitchen lighting upgrade with circuit work",
      "estimated_hours": 6.0,
      "calculated_price": 665.0,
      "call_out_fee": 65.0,
      "labour_cost": 600.0,
      "emergency_uplift": null,
      "job_complexity": "complex",
      "confidence_score": 60.0,
      "match_reason": "If additional circuit work or modifications needed",
      "recommended_actions": [
        "Site survey recommended",
        "Check if circuit upgrade required",
        "Plan for potential additional work"
      ]
    }
  ]
}
```

**Benefits:**
- ✅ Shows user multiple options (quick fix, standard, comprehensive)
- ✅ Sorted by confidence (best match first)
- ✅ Each has separate pricing and time estimate
- ✅ User can choose which option fits their needs and budget

### 2. Analyze Job (Single Best Match)

**POST** `/api/v1/analyze-job`

Analyze electrical job description and get AI-powered estimates.

**Request Body:**
```json
{
  "job_description": "Install 5 new LED downlights in the kitchen. The ceiling is plasterboard and there's existing lighting I want to replace.",
  "is_emergency": false,
  "customer_email": "customer@example.com"
}
```

**Response:**
```json
{
  "job_description": "Install 5 new LED downlights in the kitchen...",
  "estimated_hours": 3.5,
  "calculated_price": 415.0,
  "priority": "standard",
  "status": "pending",
  "currency": "GBP",
  "call_out_fee": 65.0,
  "labour_cost": 350.0,
  "emergency_uplift": null,
  "ai_reasoning": "Installing 5 LED downlights requires cutting holes, wiring, and testing. Estimated 3.5 hours including setup and certification.",
  "job_complexity": "moderate",
  "recommended_actions": [
    "Verify ceiling access for wiring",
    "Confirm LED compatibility with existing circuit",
    "Schedule electrical safety testing after installation"
  ]
}
```

### 2. Quick Estimate

**POST** `/api/v1/quick-estimate`

Get a quick estimate with minimal response.

**Query Parameters:**
- `job_description` (required): Job description text
- `is_emergency` (optional): Boolean, default false

**Example:**
```
POST /api/v1/quick-estimate?job_description=Replace broken socket&is_emergency=false
```

**Response:**
```json
{
  "estimated_hours": 1.5,
  "estimated_price": 215.0,
  "complexity": "simple",
  "currency": "GBP"
}
```

### 3. Pricing Information

**GET** `/api/v1/pricing-info`

Get current pricing configuration.

**Response:**
```json
{
  "base_hourly_rate": 100.0,
  "call_out_fee": 65.0,
  "emergency_uplift_percent": 50.0,
  "currency": "GBP"
}
```

### 4. Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "app_name": "WireQuote AI Backend",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 💰 Pricing Logic

The system calculates quotes based on:

1. **Call-out Fee**: £65 (fixed)
2. **Labour Cost**: Estimated hours × £100/hour
3. **Emergency Uplift**: +50% of labour cost (if emergency)

**Example Calculation (Standard Job):**
```
Call-out fee:  £65
Labour (3.5h):  £350
Total:         £415
```

**Example Calculation (Emergency Job):**
```
Call-out fee:       £65
Labour (3.5h):      £350
Emergency uplift:   £175 (50% of £350)
Total:              £590
```

## 🧠 AI Analysis

The AI considers:

- **Scope of work**: Number of items to install/repair
- **Complexity**: Simple replacement vs complex rewiring
- **Access difficulty**: Ceiling work, outdoor installations
- **Safety requirements**: Testing and certification time
- **Material considerations**: Compatibility and requirements
- **Setup and cleanup time**: Travel, preparation, and finishing

## ⚙️ Configuration

Edit `app/config.py` or `.env` to customize:

```python
# Pricing
base_hourly_rate = 100.0      # £100 per hour
emergency_uplift = 0.50       # 50% extra for emergencies
call_out_fee = 65.0           # £65 call-out fee

# OpenAI
openai_model = "gpt-4o-mini"  # Cost-effective model

# CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173"
]
```

## 🧪 Testing the API

### Using cURL

```bash
# Analyze a job
curl -X POST "http://localhost:8000/api/v1/analyze-job" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Replace 3 power sockets in living room",
    "is_emergency": false
  }'

# Quick estimate
curl -X POST "http://localhost:8000/api/v1/quick-estimate?job_description=Fix broken light switch&is_emergency=true"

# Health check
curl http://localhost:8000/health
```

### Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze-job",
    json={
        "job_description": "Install new consumer unit and rewire kitchen",
        "is_emergency": False
    }
)

print(response.json())
```

## 🔧 Troubleshooting

### OpenAI API Key Error
```
ValueError: OPENAI_API_KEY is not set in environment variables
```
**Solution**: Make sure you've created `.env` file and added your OpenAI API key.

### Port Already in Use
```
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8000)
```
**Solution**: Change the port in `.env` or kill the process using port 8000.

### Module Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Make sure you've installed dependencies: `pip install -r requirements.txt`

## 📊 Project Structure

```
wirequote-ai-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py    # OpenAI integration
│   │   └── quote_service.py # Price calculation
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Helper functions
├── .env                     # Environment variables (create this)
├── .env.example            # Example environment file
├── .gitignore
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── run.py                 # Application entry point
```

## 🎨 Integration with Frontend

### Example React Integration

```javascript
const analyzeJob = async (jobDescription, isEmergency) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/analyze-job', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        job_description: jobDescription,
        is_emergency: isEmergency,
      }),
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};

// Usage
const result = await analyzeJob(
  "Install new HVAC system in commercial building",
  false
);

console.log(`Estimated Hours: ${result.estimated_hours}`);
console.log(`Total Price: £${result.calculated_price}`);
console.log(`Complexity: ${result.job_complexity}`);
```

## 📝 License

This project is for demonstration purposes.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check OpenAI API status: https://status.openai.com/

## 🎯 Next Steps

To enhance the system:
- [ ] Add database for storing quotes
- [ ] Implement authentication
- [ ] Add email notifications
- [ ] Create admin dashboard
- [ ] Add quote approval workflow
- [ ] Implement payment integration
- [ ] Add customer management

---

Built with ❤️ using FastAPI and OpenAI