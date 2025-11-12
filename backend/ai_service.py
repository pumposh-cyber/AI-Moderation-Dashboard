"""AI service interface and mock implementation."""
from typing import Protocol

from backend.models import Priority


class AIService(Protocol):
    """Protocol defining the AI service interface."""
    
    def generate_summary(self, content: str, content_type: str) -> str:
        """Generate an AI summary for the flagged content."""
        ...
    
    def calculate_priority(self, content: str) -> Priority:
        """Calculate priority level for the flagged content."""
        ...


class MockAIService:
    """Mock AI service implementation for MVP."""
    
    # Keywords that indicate high priority
    HIGH_PRIORITY_KEYWORDS = [
        "violence", "threat", "harassment", "abuse", "illegal",
        "drug", "weapon", "hate", "discrimination", "suicide"
    ]
    
    # Keywords that indicate medium priority
    MEDIUM_PRIORITY_KEYWORDS = [
        "spam", "scam", "inappropriate", "offensive", "bullying"
    ]
    
    def generate_summary(self, content: str, content_type: str) -> str:
        """Generate a mock summary based on content type."""
        content_preview = content[:100] + "..." if len(content) > 100 else content
        
        if content_type == "message":
            return f"Message contains potentially problematic content: {content_preview}. Review recommended for policy compliance."
        elif content_type == "image":
            return f"Image flagged for review. Content description unavailable in mock mode. Manual review required."
        elif content_type == "report":
            return f"User report received. Content: {content_preview}. Requires moderator attention."
        else:
            return f"Flagged {content_type} content requires review: {content_preview}"
    
    def calculate_priority(self, content: str) -> Priority:
        """Calculate priority based on keyword matching."""
        content_lower = content.lower()
        
        # Check for high priority keywords
        for keyword in self.HIGH_PRIORITY_KEYWORDS:
            if keyword in content_lower:
                return "high"
        
        # Check for medium priority keywords
        for keyword in self.MEDIUM_PRIORITY_KEYWORDS:
            if keyword in content_lower:
                return "medium"
        
        # Default to low priority
        return "low"


# Global instance for use throughout the application
ai_service: AIService = MockAIService()

