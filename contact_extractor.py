from langchain.prompts import PromptTemplate
import google.generativeai as genai
import json
import os
import logging
from dotenv import load_dotenv
from models import Contact

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini LLM
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.warning("GOOGLE_API_KEY not found in environment variables")

# Configure the Gemini API
genai.configure(api_key=api_key)

# Set up the model
generation_config = {
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# Define prompt template
CONTACT_EXTRACTION_PROMPT = """
You are a contact information extraction assistant. Given the following text from {source_type},
extract all people's contact information in a structured format.

Extract the following fields if available:
- Full Name
- Job Title
- Organization/Company
- Email Address
- Phone Number
- LinkedIn URL (if present)

Only extract real people with contact details. Ignore generic information, headers, footers, and non-contact text.

Text:
{text_content}

Format your response as a JSON array of contact objects with the fields listed above.
Use null for missing fields. If you can't find any contact information, return an empty array.

ONLY respond with the JSON data. Do not include any explanations or additional text.
"""

prompt_template = PromptTemplate(
    input_variables=["source_type", "text_content"],
    template=CONTACT_EXTRACTION_PROMPT
)

def extract_contacts(text, source_name, source_type="document"):
    """
    Extract contact information from text using Gemini LLM
    Args:
        text (str): The text to extract contacts from
        source_name (str): Name of the source document
        source_type (str): Type of source (document, business card, etc.)
    Returns:
        list: List of Contact objects
    """
    try:
        # Create prompt
        prompt = prompt_template.format(source_type=source_type, text_content=text)
        
        # Get response from Gemini
        logger.info(f"Extracting contacts from {source_type}")
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config
        )
        
        response = model.generate_content(prompt).text
        
        # Parse response
        try:
            # Try to extract JSON from the response
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            contacts_data = json.loads(json_str)
            
            # Convert to Contact objects
            contacts = []
            for contact_data in contacts_data:
                contact = Contact(
                    name=contact_data.get("Full Name", "Unknown"),
                    title=contact_data.get("Job Title"),
                    organization=contact_data.get("Organization/Company"),
                    email=contact_data.get("Email Address"),
                    phone=contact_data.get("Phone Number"),
                    linkedin=contact_data.get("LinkedIn URL"),
                    source_document=source_name
                )
                contacts.append(contact)
            
            return contacts
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
            logger.debug(f"Raw response: {response}")
            return []
    except Exception as e:
        logger.error(f"Error extracting contacts: {str(e)}")
        return []
