import json
import hashlib
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError
from app.config import settings

class AIService:
    """Service for AI-powered job analysis using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self._estimate_cache: dict = {}  # Cache for consistent time estimates
    
    def analyze_job_with_multiple_suggestions(
        self, 
        job_description: str, 
        is_emergency: bool = False
    ) -> dict:
        """
        Analyze job and return multiple possible interpretations/suggestions
        
        Args:
            job_description: The electrical work description
            is_emergency: Whether this is an emergency job
            
        Returns:
            dict: Multiple job suggestions with confidence scores
        """
        
        system_prompt = """You are an expert electrical contractor with 20+ years of experience in the UK.
Analyze the job description and provide MULTIPLE possible interpretations, from most likely to least likely.

For each interpretation, provide:
1. A clear job title (5-8 words max)
2. Refined job description
3. Estimated hours
4. Job complexity (simple/moderate/complex)
5. Confidence score (0-100) - how well this matches the description
6. Match reason - why this interpretation makes sense
7. Recommended actions (2-4 items)

Consider different scopes:
- Minimum viable work (quick fix)
- Standard comprehensive work (most likely)
- Extended scope (if additional work needed)

Return as JSON:
{
    "suggestions": [
        {
            "job_title": "Kitchen LED Downlight Installation",
            "refined_description": "Install 5 LED downlights...",
            "estimatedHours": 3.5,
            "jobComplexity": "moderate",
            "confidence_score": 95,
            "match_reason": "Description clearly specifies...",
            "recommendedActions": ["action1", "action2"]
        }
    ]
}

Provide 2-4 suggestions, sorted by confidence (highest first)."""

        user_prompt = f"""Analyze this electrical job and provide multiple interpretations:

Job Description: {job_description}
Emergency Job: {"Yes" if is_emergency else "No"}

Provide 2-4 different interpretations sorted by confidence."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            suggestions = analysis.get("suggestions", [])
            
            # Validate and sanitize suggestions
            validated_suggestions = []
            for suggestion in suggestions[:4]:  # Max 4 suggestions
                hours = float(suggestion.get("estimatedHours", 2.0))
                hours = max(0.5, min(100.0, hours))
                
                complexity = suggestion.get("jobComplexity", "moderate")
                if complexity not in ["simple", "moderate", "complex"]:
                    complexity = "moderate"
                
                confidence = float(suggestion.get("confidence_score", 80))
                confidence = max(0, min(100, confidence))
                
                validated_suggestions.append({
                    "job_title": suggestion.get("job_title", "Electrical Work"),
                    "refined_description": suggestion.get("refined_description", job_description),
                    "estimatedHours": round(hours, 1),
                    "jobComplexity": complexity,
                    "confidence_score": round(confidence, 1),
                    "match_reason": suggestion.get("match_reason", "Based on job description"),
                    "recommendedActions": suggestion.get("recommendedActions", [])[:4]
                })
            
            # Sort by confidence (highest first)
            validated_suggestions.sort(key=lambda x: x["confidence_score"], reverse=True)
            
            return {"suggestions": validated_suggestions}
            
        except AuthenticationError as e:
            print(f"❌ OpenAI Authentication Error - Invalid API key: {str(e)}")
            return self._get_fallback_suggestions(job_description, is_emergency)
        except RateLimitError as e:
            print(f"❌ OpenAI Rate Limit Error - Quota exceeded: {str(e)}")
            return self._get_fallback_suggestions(job_description, is_emergency)
        except APIConnectionError as e:
            print(f"❌ OpenAI Connection Error - Cannot reach API: {str(e)}")
            return self._get_fallback_suggestions(job_description, is_emergency)
        except APITimeoutError as e:
            print(f"❌ OpenAI Timeout Error - Request timed out: {str(e)}")
            return self._get_fallback_suggestions(job_description, is_emergency)
        except Exception as e:
            print(f"❌ OpenAI Unexpected Error ({type(e).__name__}): {str(e)}")
            return self._get_fallback_suggestions(job_description, is_emergency)
    
    def _get_fallback_suggestions(self, job_description: str, is_emergency: bool) -> dict:
        """Provide fallback suggestions if OpenAI fails"""
        description_lower = job_description.lower()
        
        suggestions = []
        
        # Determine base scenario
        if any(word in description_lower for word in ['socket', 'plug', 'outlet']):
            suggestions.append({
                "job_title": "Power Socket Replacement",
                "refined_description": "Replace or install power sockets",
                "estimatedHours": 1.5,
                "jobComplexity": "simple",
                "confidence_score": 85,
                "match_reason": "Job mentions sockets/plugs",
                "recommendedActions": ["Check circuit capacity", "Test after installation"]
            })
        
        if any(word in description_lower for word in ['light', 'lighting', 'downlight', 'led']):
            suggestions.append({
                "job_title": "Lighting Installation/Upgrade",
                "refined_description": "Install or upgrade lighting fixtures",
                "estimatedHours": 3.0,
                "jobComplexity": "moderate",
                "confidence_score": 80,
                "match_reason": "Job involves lighting work",
                "recommendedActions": ["Verify ceiling access", "Check compatibility", "Schedule testing"]
            })
        
        # Add a general comprehensive option
        suggestions.append({
            "job_title": "General Electrical Work",
            "refined_description": job_description,
            "estimatedHours": 3.5,
            "jobComplexity": "moderate",
            "confidence_score": 70,
            "match_reason": "Standard electrical work estimate",
            "recommendedActions": ["Site visit recommended", "Safety testing required"]
        })
        
        return {"suggestions": suggestions[:3]}
    
    def analyze_job_description(self, job_description: str, is_emergency: bool = False) -> dict:
        """
        Analyze job description using OpenAI and return structured estimates.
        Results are cached per (job_description, is_emergency) to ensure consistency.
        """
        # Build a stable cache key from the inputs
        cache_key = hashlib.md5(f"{job_description.strip().lower()}|{is_emergency}".encode()).hexdigest()
        if cache_key in self._estimate_cache:
            print(f"✅ Returning cached estimate for job (key: {cache_key[:8]}...)")
            return self._estimate_cache[cache_key]
        
        system_prompt = """You are an expert electrical contractor with 20+ years of experience in the UK.
Your job is to analyze electrical work descriptions and provide accurate time estimates for the ACTUAL WORK only.
The call-out fee is charged separately — do NOT include travel or call-out time in estimatedHours.

IMPORTANT: estimatedHours means hands-on work time only. The billing system adds the call-out fee on top automatically.

Use these UK electrician benchmarks as your reference:

SIMPLE jobs (0.5 – 2 hours):
- Replace 1 socket or switch: 0.5h
- Replace 2–4 sockets or switches: 1h
- Replace 5–8 sockets or switches: 1.5–2h
- Replace a single light fitting: 0.5h
- Replace 2–4 light fittings: 1–1.5h
- Install 1–2 LED downlights: 1h
- Fix a tripped breaker / reset fuse: 0.5h
- Replace a single outdoor light: 1h

MODERATE jobs (2 – 6 hours):
- Install 5–10 LED downlights: 2–3h
- Install 10–20 LED downlights: 3–5h
- Replace multiple sockets in one room (8–12): 2–3h
- Install a new circuit (single room): 3–4h
- Fault finding and repair (unknown fault): 2–4h
- Install outdoor socket or garden lighting: 2–3h
- Install EV charger (standard): 3–4h
- Replace bathroom extractor fan: 1.5–2h
- Install security lighting (2–3 lights): 2–3h

COMPLEX jobs (6+ hours):
- Replace consumer unit / fuse board: 6–8h
- Rewire a single room: 4–6h
- Rewire a 1-bed flat: 10–14h
- Rewire a 2-bed house: 14–18h
- Rewire a 3-bed house: 20–28h
- Rewire a 4-bed house: 28–36h
- Install new distribution board: 6–8h
- Full electrical inspection (EICR) 1-bed: 3–4h
- Full electrical inspection (EICR) 3-bed: 5–7h
- Install solar panel system: 8–12h

QUANTITY RULES — always scale by quantity mentioned:
- If description says "a socket" or "one socket" → treat as 1 item
- If description says "sockets" without a number → assume 4–6 items
- If description says "throughout the house" or "whole house" → treat as complex full-scope
- If description says "a few" → assume 3–4 items
- If description says "several" → assume 5–7 items

Return your analysis as a JSON object with this exact structure:
{
    "estimatedHours": <float between 0.5 and 100>,
    "jobComplexity": "<simple|moderate|complex>",
    "reasoning": "<brief explanation referencing the specific benchmark used>",
    "recommendedActions": ["<action1>", "<action2>"]
}

Rules:
- Always pick the closest benchmark and scale by quantity
- Never estimate below 0.5h
- For vague descriptions with no quantity, use the mid-range of the relevant benchmark
- Emergency flag does NOT change the hours — it only affects pricing, which is handled separately"""

        user_prompt = f"""Analyze this electrical job:

Job Description: {job_description}
Emergency Job: {"Yes" if is_emergency else "No"}

Provide accurate time estimate and complexity assessment."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent estimates
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            analysis = json.loads(response.choices[0].message.content)
            
            # Validate and sanitize the response
            estimatedHours = float(analysis.get("estimatedHours", 2.0))
            estimatedHours = max(0.5, min(100.0, estimatedHours))  # Clamp between 0.5 and 100
            
            complexity = analysis.get("jobComplexity", "moderate")
            if complexity not in ["simple", "moderate", "complex"]:
                complexity = "moderate"
            
            reasoning = analysis.get("reasoning", "Standard electrical work estimate")
            recommendedActions = analysis.get("recommendedActions", [])
            
            if not isinstance(recommendedActions, list):
                recommendedActions = []
            
            result = {
                "estimatedHours": round(estimatedHours, 1),
                "jobComplexity": complexity,
                "reasoning": reasoning,
                "recommendedActions": recommendedActions[:5]  # Limit to 5 actions
            }
            self._estimate_cache[cache_key] = result
            return result
            
        except AuthenticationError as e:
            print(f"❌ OpenAI Authentication Error - Invalid API key: {str(e)}")
            return self._get_fallback_estimate(job_description, is_emergency)
        except RateLimitError as e:
            print(f"❌ OpenAI Rate Limit Error - Quota exceeded: {str(e)}")
            return self._get_fallback_estimate(job_description, is_emergency)
        except APIConnectionError as e:
            print(f"❌ OpenAI Connection Error - Cannot reach API: {str(e)}")
            return self._get_fallback_estimate(job_description, is_emergency)
        except APITimeoutError as e:
            print(f"❌ OpenAI Timeout Error - Request timed out: {str(e)}")
            return self._get_fallback_estimate(job_description, is_emergency)
        except Exception as e:
            print(f"❌ OpenAI Unexpected Error ({type(e).__name__}): {str(e)}")
            return self._get_fallback_estimate(job_description, is_emergency)
    
    def _get_fallback_estimate(self, job_description: str, is_emergency: bool) -> dict:
        """
        Provide fallback estimates if OpenAI API fails.
        Uses quantity-aware, scope-based estimation aligned with UK electrician benchmarks.
        """
        description_lower = job_description.lower()

        # --- Quantity detection ---
        import re
        quantity = 1
        # Look for explicit numbers (e.g. "5 sockets", "install 3 lights")
        number_match = re.search(r'\b(\d+)\b', description_lower)
        if number_match:
            quantity = int(number_match.group(1))
        elif any(w in description_lower for w in ['few', 'a few']):
            quantity = 3
        elif any(w in description_lower for w in ['several']):
            quantity = 6
        elif any(w in description_lower for w in ['throughout', 'whole house', 'entire house', 'full house']):
            quantity = 99  # signals whole-house scope

        # --- Whole-house / full rewire ---
        if quantity == 99 or any(w in description_lower for w in ['rewire', 'full rewire', 'complete rewire']):
            if any(w in description_lower for w in ['1 bed', '1-bed', 'one bed', 'flat', 'apartment']):
                hours, complexity = 12.0, "complex"
            elif any(w in description_lower for w in ['2 bed', '2-bed', 'two bed']):
                hours, complexity = 16.0, "complex"
            elif any(w in description_lower for w in ['3 bed', '3-bed', 'three bed']):
                hours, complexity = 24.0, "complex"
            elif any(w in description_lower for w in ['4 bed', '4-bed', 'four bed']):
                hours, complexity = 32.0, "complex"
            else:
                hours, complexity = 20.0, "complex"

        # --- Consumer unit / fuse board ---
        elif any(w in description_lower for w in ['consumer unit', 'fuse box', 'fuse board', 'distribution board', 'fuseboard']):
            hours, complexity = 7.0, "complex"

        # --- EV charger ---
        elif any(w in description_lower for w in ['ev charger', 'electric vehicle', 'car charger']):
            hours, complexity = 3.5, "moderate"

        # --- EICR / inspection ---
        elif any(w in description_lower for w in ['eicr', 'inspection', 'electrical report', 'condition report']):
            hours, complexity = 5.0, "moderate"

        # --- Sockets / plugs ---
        elif any(w in description_lower for w in ['socket', 'plug', 'outlet', 'power point']):
            if quantity == 1:
                hours, complexity = 0.5, "simple"
            elif quantity <= 4:
                hours, complexity = 1.0, "simple"
            elif quantity <= 8:
                hours, complexity = 1.5, "simple"
            elif quantity <= 12:
                hours, complexity = 2.5, "moderate"
            else:
                hours, complexity = 4.0, "moderate"

        # --- Downlights / spotlights ---
        elif any(w in description_lower for w in ['downlight', 'spotlight', 'recessed light', 'can light']):
            if quantity <= 2:
                hours, complexity = 1.0, "simple"
            elif quantity <= 5:
                hours, complexity = 2.0, "moderate"
            elif quantity <= 10:
                hours, complexity = 3.0, "moderate"
            elif quantity <= 20:
                hours, complexity = 4.5, "moderate"
            else:
                hours, complexity = 6.0, "complex"

        # --- General lighting / light fittings ---
        elif any(w in description_lower for w in ['light', 'lighting', 'bulb', 'fitting', 'fixture', 'led']):
            if quantity == 1:
                hours, complexity = 0.5, "simple"
            elif quantity <= 4:
                hours, complexity = 1.5, "simple"
            elif quantity <= 8:
                hours, complexity = 2.5, "moderate"
            else:
                hours, complexity = 4.0, "moderate"

        # --- Switches ---
        elif any(w in description_lower for w in ['switch', 'dimmer']):
            if quantity <= 2:
                hours, complexity = 0.5, "simple"
            elif quantity <= 6:
                hours, complexity = 1.0, "simple"
            else:
                hours, complexity = 2.0, "moderate"

        # --- Fault finding ---
        elif any(w in description_lower for w in ['fault', 'tripping', 'trip', 'not working', 'no power', 'dead']):
            hours, complexity = 2.5, "moderate"

        # --- Outdoor / garden ---
        elif any(w in description_lower for w in ['outdoor', 'garden', 'external', 'outside', 'security light']):
            hours, complexity = 2.5, "moderate"

        # --- New circuit ---
        elif any(w in description_lower for w in ['new circuit', 'extra circuit', 'additional circuit']):
            hours, complexity = 3.5, "moderate"

        # --- Default fallback ---
        else:
            hours, complexity = 3.0, "moderate"

        return {
            "estimatedHours": hours,
            "jobComplexity": complexity,
            "reasoning": "Estimate based on UK electrician benchmarks (AI service temporarily unavailable)",
            "recommendedActions": [
                "Site visit recommended for accurate quote",
                "Electrical safety testing required"
            ]
        }

# Create singleton instance
ai_service = AIService()