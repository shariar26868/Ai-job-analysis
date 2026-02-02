from datetime import datetime
from typing import Any, Dict

def format_currency(amount: float, currency: str = "GBP") -> str:
    """
    Format amount as currency string
    
    Args:
        amount: The amount to format
        currency: Currency code (default: GBP)
        
    Returns:
        str: Formatted currency string
    """
    symbols = {
        "GBP": "£",
        "USD": "$",
        "EUR": "€"
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"

def calculate_hours_ago(created_at: datetime) -> int:
    """
    Calculate hours since a datetime
    
    Args:
        created_at: The datetime to compare
        
    Returns:
        int: Hours since the datetime
    """
    delta = datetime.now() - created_at
    return int(delta.total_seconds() / 3600)

def sanitize_job_description(description: str) -> str:
    """
    Sanitize and clean job description
    
    Args:
        description: Raw job description
        
    Returns:
        str: Cleaned description
    """
    # Remove extra whitespace
    description = " ".join(description.split())
    
    # Trim to reasonable length
    if len(description) > 1000:
        description = description[:1000] + "..."
    
    return description

def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid format
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_response_metadata(
    success: bool = True,
    message: str = "",
    extra_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create standardized response metadata
    
    Args:
        success: Whether the operation was successful
        message: Response message
        extra_data: Additional data to include
        
    Returns:
        dict: Response metadata
    """
    metadata = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "message": message
    }
    
    if extra_data:
        metadata.update(extra_data)
    
    return metadata