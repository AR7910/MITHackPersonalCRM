import re
import logging
from typing import List
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_filename(original_filename):
    """
    Generate a unique filename based on the original filename and current timestamp
    Args:
        original_filename: The original filename
    Returns:
        str: A unique filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = original_filename.rsplit('.', 1) if '.' in original_filename else (original_filename, '')
    return f"{name}_{timestamp}.{ext}" if ext else f"{name}_{timestamp}"

def validate_email(email):
    """
    Validate an email address
    Args:
        email: Email address to validate
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """
    Validate a phone number
    Args:
        phone: Phone number to validate
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid phone number (at least 7 digits)
    return len(cleaned) >= 7 and cleaned.isdigit()

def format_phone(phone):
    """
    Format a phone number consistently
    Args:
        phone: Phone number to format
    Returns:
        str: Formatted phone number
    """
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Format based on length
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return as is if we can't format it

def extract_tags_from_text(text):
    """
    Extract potential tags from text based on common industry terms
    Args:
        text: Text to extract tags from
    Returns:
        list: List of potential tags
    """
    if not text:
        return []
    
    # Common industry/profession tags
    industries = [
        "tech", "healthcare", "finance", "education", "marketing",
        "sales", "engineering", "design", "consulting", "legal",
        "media", "hr", "real estate", "construction", "manufacturing"
    ]
    
    found_tags = []
    text_lower = text.lower()
    
    for industry in industries:
        if industry in text_lower:
            found_tags.append(industry)
    
    return found_tags

def suggest_follow_up_template(contact, template_type="email"):
    """
    Generate a follow-up message template based on contact information
    Args:
        contact: Contact object
        template_type: Type of template to generate (email, linkedin, etc.)
    Returns:
        str: Follow-up message template
    """
    if not contact:
        return ""
    
    if template_type.lower() == "linkedin":
        # LinkedIn messages have a 300 character limit
        template = f"""Hi {contact.name.split()[0]}, it was great to meet you{" at " + contact.event if contact.event else ""}! I enjoyed our conversation about {contact.organization or "your work"} and would love to stay connected. Looking forward to potential collaboration opportunities!"""
        
        # Ensure we're within LinkedIn's character limit
        return template[:300]
    else:
        # Email template
        template = f"""Subject: Following Up After {contact.event or "Our Meeting"}

Dear {contact.name},

I hope this email finds you well. It was a pleasure meeting you{" at " + contact.event if contact.event else ""}.

I was particularly interested in our conversation about {contact.organization or "your work"}. The insights you shared about {contact.title or "your role"} were fascinating, and I'd love to continue our discussion and explore potential opportunities to collaborate.

Would you be available for a brief call in the coming weeks?

Best regards,

[Your Name]
"""
        return template
