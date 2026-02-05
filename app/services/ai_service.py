# import json
# from openai import OpenAI
# from app.config import settings

# class AIService:
#     """Service for AI-powered job analysis using OpenAI"""
    
#     def __init__(self):
#         self.client = OpenAI(api_key=settings.openai_api_key)
#         self.model = settings.openai_model
    
#     def analyze_job_with_multiple_suggestions(
#         self, 
#         job_description: str, 
#         is_emergency: bool = False
#     ) -> dict:
#         """
#         Analyze job and return multiple possible interpretations/suggestions
        
#         Args:
#             job_description: The electrical work description
#             is_emergency: Whether this is an emergency job
            
#         Returns:
#             dict: Multiple job suggestions with confidence scores
#         """
        
#         system_prompt = """You are an expert electrical contractor with 20+ years of experience in the UK.
# Analyze the job description and provide MULTIPLE possible interpretations, from most likely to least likely.

# For each interpretation, provide:
# 1. A clear job title (5-8 words max)
# 2. Refined job description
# 3. Estimated hours
# 4. Job complexity (simple/moderate/complex)
# 5. Confidence score (0-100) - how well this matches the description
# 6. Match reason - why this interpretation makes sense
# 7. Recommended actions (2-4 items)

# Consider different scopes:
# - Minimum viable work (quick fix)
# - Standard comprehensive work (most likely)
# - Extended scope (if additional work needed)

# Return as JSON:
# {
#     "suggestions": [
#         {
#             "job_title": "Kitchen LED Downlight Installation",
#             "refined_description": "Install 5 LED downlights...",
#             "estimated_hours": 3.5,
#             "job_complexity": "moderate",
#             "confidence_score": 95,
#             "match_reason": "Description clearly specifies...",
#             "recommended_actions": ["action1", "action2"]
#         }
#     ]
# }

# Provide 2-4 suggestions, sorted by confidence (highest first)."""

#         user_prompt = f"""Analyze this electrical job and provide multiple interpretations:

# Job Description: {job_description}
# Emergency Job: {"Yes" if is_emergency else "No"}

# Provide 2-4 different interpretations sorted by confidence."""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_prompt}
#                 ],
#                 temperature=0.4,
#                 max_tokens=1500,
#                 response_format={"type": "json_object"}
#             )
            
#             analysis = json.loads(response.choices[0].message.content)
#             suggestions = analysis.get("suggestions", [])
            
#             # Validate and sanitize suggestions
#             validated_suggestions = []
#             for suggestion in suggestions[:4]:  # Max 4 suggestions
#                 hours = float(suggestion.get("estimated_hours", 2.0))
#                 hours = max(0.5, min(100.0, hours))
                
#                 complexity = suggestion.get("job_complexity", "moderate")
#                 if complexity not in ["simple", "moderate", "complex"]:
#                     complexity = "moderate"
                
#                 confidence = float(suggestion.get("confidence_score", 80))
#                 confidence = max(0, min(100, confidence))
                
#                 validated_suggestions.append({
#                     "job_title": suggestion.get("job_title", "Electrical Work"),
#                     "refined_description": suggestion.get("refined_description", job_description),
#                     "estimated_hours": round(hours, 1),
#                     "job_complexity": complexity,
#                     "confidence_score": round(confidence, 1),
#                     "match_reason": suggestion.get("match_reason", "Based on job description"),
#                     "recommended_actions": suggestion.get("recommended_actions", [])[:4]
#                 })
            
#             # Sort by confidence (highest first)
#             validated_suggestions.sort(key=lambda x: x["confidence_score"], reverse=True)
            
#             return {"suggestions": validated_suggestions}
            
#         except Exception as e:
#             print(f"OpenAI API Error: {str(e)}")
#             return self._get_fallback_suggestions(job_description, is_emergency)
    
#     def _get_fallback_suggestions(self, job_description: str, is_emergency: bool) -> dict:
#         """Provide fallback suggestions if OpenAI fails"""
#         description_lower = job_description.lower()
        
#         suggestions = []
        
#         # Determine base scenario
#         if any(word in description_lower for word in ['socket', 'plug', 'outlet']):
#             suggestions.append({
#                 "job_title": "Power Socket Replacement",
#                 "refined_description": "Replace or install power sockets",
#                 "estimated_hours": 1.5,
#                 "job_complexity": "simple",
#                 "confidence_score": 85,
#                 "match_reason": "Job mentions sockets/plugs",
#                 "recommended_actions": ["Check circuit capacity", "Test after installation"]
#             })
        
#         if any(word in description_lower for word in ['light', 'lighting', 'downlight', 'led']):
#             suggestions.append({
#                 "job_title": "Lighting Installation/Upgrade",
#                 "refined_description": "Install or upgrade lighting fixtures",
#                 "estimated_hours": 3.0,
#                 "job_complexity": "moderate",
#                 "confidence_score": 80,
#                 "match_reason": "Job involves lighting work",
#                 "recommended_actions": ["Verify ceiling access", "Check compatibility", "Schedule testing"]
#             })
        
#         # Add a general comprehensive option
#         suggestions.append({
#             "job_title": "General Electrical Work",
#             "refined_description": job_description,
#             "estimated_hours": 3.5,
#             "job_complexity": "moderate",
#             "confidence_score": 70,
#             "match_reason": "Standard electrical work estimate",
#             "recommended_actions": ["Site visit recommended", "Safety testing required"]
#         })
        
#         return {"suggestions": suggestions[:3]}
    
#     def analyze_job_description(self, job_description: str, is_emergency: bool = False) -> dict:
#         """
#         Analyze job description using OpenAI and return structured estimates
        
#         Args:
#             job_description: The electrical work description
#             is_emergency: Whether this is an emergency job
            
#         Returns:
#             dict: Structured analysis with estimates
#         """
        
#         system_prompt = """You are an expert electrical contractor with 20+ years of experience in the UK. 
# Your job is to analyze electrical work descriptions and provide accurate time and complexity estimates.

# Consider factors like:
# - Scope of work (number of items to install/repair)
# - Complexity (simple socket replacement vs rewiring)
# - Access difficulty (ceiling work, outdoor work)
# - Safety requirements (testing, certification)
# - Material requirements
# - Travel and setup time

# Return your analysis as a JSON object with this exact structure:
# {
#     "estimated_hours": <float between 0.5 and 100>,
#     "job_complexity": "<simple|moderate|complex>",
#     "reasoning": "<brief explanation of your estimate>",
#     "recommended_actions": ["<action1>", "<action2>"]
# }

# Guidelines:
# - Simple jobs (socket replacement, light fixture): 0.5-2 hours
# - Moderate jobs (multiple fixtures, minor repairs): 2-6 hours
# - Complex jobs (rewiring, consumer unit, outdoor): 6+ hours
# - Always add buffer time for testing and certification
# - Emergency work should already be flagged, don't add extra time for that"""

#         user_prompt = f"""Analyze this electrical job:

# Job Description: {job_description}
# Emergency Job: {"Yes" if is_emergency else "No"}

# Provide accurate time estimate and complexity assessment."""

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_prompt}
#                 ],
#                 temperature=0.3,  # Lower temperature for more consistent estimates
#                 max_tokens=500,
#                 response_format={"type": "json_object"}
#             )
            
#             # Parse the JSON response
#             analysis = json.loads(response.choices[0].message.content)
            
#             # Validate and sanitize the response
#             estimated_hours = float(analysis.get("estimated_hours", 2.0))
#             estimated_hours = max(0.5, min(100.0, estimated_hours))  # Clamp between 0.5 and 100
            
#             complexity = analysis.get("job_complexity", "moderate")
#             if complexity not in ["simple", "moderate", "complex"]:
#                 complexity = "moderate"
            
#             reasoning = analysis.get("reasoning", "Standard electrical work estimate")
#             recommended_actions = analysis.get("recommended_actions", [])
            
#             if not isinstance(recommended_actions, list):
#                 recommended_actions = []
            
#             return {
#                 "estimated_hours": round(estimated_hours, 1),
#                 "job_complexity": complexity,
#                 "reasoning": reasoning,
#                 "recommended_actions": recommended_actions[:5]  # Limit to 5 actions
#             }
            
#         except Exception as e:
#             print(f"OpenAI API Error: {str(e)}")
#             # Fallback to default values if API fails
#             return self._get_fallback_estimate(job_description, is_emergency)
    
#     def _get_fallback_estimate(self, job_description: str, is_emergency: bool) -> dict:
#         """
#         Provide fallback estimates if OpenAI API fails
#         """
#         description_lower = job_description.lower()
        
#         # Simple keyword-based estimation
#         if any(word in description_lower for word in ['socket', 'plug', 'light', 'bulb', 'switch']):
#             hours = 1.5
#             complexity = "simple"
#         elif any(word in description_lower for word in ['rewire', 'consumer unit', 'fuse box', 'panel']):
#             hours = 12.0
#             complexity = "complex"
#         else:
#             hours = 3.5
#             complexity = "moderate"
        
#         return {
#             "estimated_hours": hours,
#             "job_complexity": complexity,
#             "reasoning": "Estimate based on job description keywords (AI service temporarily unavailable)",
#             "recommended_actions": [
#                 "Site visit recommended for accurate quote",
#                 "Electrical safety testing required"
#             ]
#         }

# # Create singleton instance
# ai_service = AIService()



import json
from openai import OpenAI
from app.config import settings

class AIService:
    """Service for AI-powered job analysis using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
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
            "estimated_hours": 3.5,
            "job_complexity": "moderate",
            "confidence_score": 95,
            "match_reason": "Description clearly specifies...",
            "recommended_actions": ["action1", "action2"]
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
                hours = float(suggestion.get("estimated_hours", 2.0))
                hours = max(0.5, min(100.0, hours))
                
                complexity = suggestion.get("job_complexity", "moderate")
                if complexity not in ["simple", "moderate", "complex"]:
                    complexity = "moderate"
                
                confidence = float(suggestion.get("confidence_score", 80))
                confidence = max(0, min(100, confidence))
                
                validated_suggestions.append({
                    "job_title": suggestion.get("job_title", "Electrical Work"),
                    "refined_description": suggestion.get("refined_description", job_description),
                    "estimated_hours": round(hours, 1),
                    "job_complexity": complexity,
                    "confidence_score": round(confidence, 1),
                    "match_reason": suggestion.get("match_reason", "Based on job description"),
                    "recommended_actions": suggestion.get("recommended_actions", [])[:4]
                })
            
            # Sort by confidence (highest first)
            validated_suggestions.sort(key=lambda x: x["confidence_score"], reverse=True)
            
            return {"suggestions": validated_suggestions}
            
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
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
                "estimated_hours": 1.5,
                "job_complexity": "simple",
                "confidence_score": 85,
                "match_reason": "Job mentions sockets/plugs",
                "recommended_actions": ["Check circuit capacity", "Test after installation"]
            })
        
        if any(word in description_lower for word in ['light', 'lighting', 'downlight', 'led']):
            suggestions.append({
                "job_title": "Lighting Installation/Upgrade",
                "refined_description": "Install or upgrade lighting fixtures",
                "estimated_hours": 3.0,
                "job_complexity": "moderate",
                "confidence_score": 80,
                "match_reason": "Job involves lighting work",
                "recommended_actions": ["Verify ceiling access", "Check compatibility", "Schedule testing"]
            })
        
        # Add a general comprehensive option
        suggestions.append({
            "job_title": "General Electrical Work",
            "refined_description": job_description,
            "estimated_hours": 3.5,
            "job_complexity": "moderate",
            "confidence_score": 70,
            "match_reason": "Standard electrical work estimate",
            "recommended_actions": ["Site visit recommended", "Safety testing required"]
        })
        
        return {"suggestions": suggestions[:3]}
    
    def analyze_job_description(self, job_description: str, is_emergency: bool = False) -> dict:
        """
        Analyze job description using OpenAI and return structured estimates
        
        Args:
            job_description: The electrical work description
            is_emergency: Whether this is an emergency job
            
        Returns:
            dict: Structured analysis with estimates
        """
        
        system_prompt = """You are an expert electrical contractor with 20+ years of experience in the UK. 
Your job is to analyze electrical work descriptions and provide accurate time and complexity estimates.

Consider factors like:
- Scope of work (number of items to install/repair)
- Complexity (simple socket replacement vs rewiring)
- Access difficulty (ceiling work, outdoor work)
- Safety requirements (testing, certification)
- Material requirements
- Travel and setup time

Return your analysis as a JSON object with this exact structure:
{
    "estimated_hours": <float between 0.5 and 100>,
    "job_complexity": "<simple|moderate|complex>",
    "reasoning": "<brief explanation of your estimate>",
    "recommended_actions": ["<action1>", "<action2>"]
}

Guidelines:
- Simple jobs (socket replacement, light fixture): 0.5-2 hours
- Moderate jobs (multiple fixtures, minor repairs): 2-6 hours
- Complex jobs (rewiring, consumer unit, outdoor): 6+ hours
- Always add buffer time for testing and certification
- Emergency work should already be flagged, don't add extra time for that"""

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
            estimated_hours = float(analysis.get("estimated_hours", 2.0))
            estimated_hours = max(0.5, min(100.0, estimated_hours))  # Clamp between 0.5 and 100
            
            complexity = analysis.get("job_complexity", "moderate")
            if complexity not in ["simple", "moderate", "complex"]:
                complexity = "moderate"
            
            reasoning = analysis.get("reasoning", "Standard electrical work estimate")
            recommended_actions = analysis.get("recommended_actions", [])
            
            if not isinstance(recommended_actions, list):
                recommended_actions = []
            
            return {
                "estimated_hours": round(estimated_hours, 1),
                "job_complexity": complexity,
                "reasoning": reasoning,
                "recommended_actions": recommended_actions[:5]  # Limit to 5 actions
            }
            
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            # Fallback to default values if API fails
            return self._get_fallback_estimate(job_description, is_emergency)
    
    def _get_fallback_estimate(self, job_description: str, is_emergency: bool) -> dict:
        """
        Provide fallback estimates if OpenAI API fails
        """
        description_lower = job_description.lower()
        
        # Simple keyword-based estimation
        if any(word in description_lower for word in ['socket', 'plug', 'light', 'bulb', 'switch']):
            hours = 1.5
            complexity = "simple"
        elif any(word in description_lower for word in ['rewire', 'consumer unit', 'fuse box', 'panel']):
            hours = 12.0
            complexity = "complex"
        else:
            hours = 3.5
            complexity = "moderate"
        
        return {
            "estimated_hours": hours,
            "job_complexity": complexity,
            "reasoning": "Estimate based on job description keywords (AI service temporarily unavailable)",
            "recommended_actions": [
                "Site visit recommended for accurate quote",
                "Electrical safety testing required"
            ]
        }

# Create singleton instance
ai_service = AIService()