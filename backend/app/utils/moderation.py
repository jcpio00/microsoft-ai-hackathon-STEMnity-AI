import re

# --- Basic Keyword-Based Moderation --- 

FLAGGED_PATTERNS = [
    r"\b(?:inappropriate|offensive|harmful)\b", # Example keywords
]

# Compile regex patterns for efficiency
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in FLAGGED_PATTERNS]

def is_content_safe(text: str) -> bool:
    """
    Checks if the input text contains any flagged keywords or patterns.
    Returns True if safe, False if potentially unsafe.
    
    Note: This is a basic implementation and may not be robust.
    """
    
    if not text:
        return True # Empty content is considered safe
        
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            print(f"Moderation: Flagged pattern found: {pattern.pattern}")
            return False # Found a potentially unsafe pattern
            
    return True # No flagged patterns found

MODERATION_REJECTION_MESSAGE = "Let's keep our discussion focused on STEM topics! How can I help with math or science?"
