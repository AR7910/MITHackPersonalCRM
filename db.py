import json
import os
import logging
from models import Contact
from typing import List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database file path
DB_FILE = "contacts_db.json"

def initialize_db():
    """
    Initialize the database file if it doesn't exist
    """
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([], f)
        logger.info(f"Created new database file: {DB_FILE}")

def save_contacts(contacts: List[Contact]):
    """
    Save a list of contacts to the database
    Args:
        contacts: List of Contact objects to save
    """
    try:
        # Initialize DB if needed
        initialize_db()
        
        # Load existing contacts
        existing_contacts = load_all_contacts()
        existing_ids = {contact.id for contact in existing_contacts}
        
        # Add new contacts
        for contact in contacts:
            if contact.id not in existing_ids:
                existing_contacts.append(contact)
        
        # Save to file
        with open(DB_FILE, 'w') as f:
            contacts_data = [contact.to_dict() for contact in existing_contacts]
            json.dump(contacts_data, f, indent=2)
        
        logger.info(f"Saved {len(contacts)} new contacts to database")
    except Exception as e:
        logger.error(f"Error saving contacts: {str(e)}")
        raise

def load_all_contacts() -> List[Contact]:
    """
    Load all contacts from the database
    Returns:
        List of Contact objects
    """
    try:
        # Initialize DB if needed
        initialize_db()
        
        # Load from file
        with open(DB_FILE, 'r') as f:
            contacts_data = json.load(f)
        
        # Convert to Contact objects
        contacts = [Contact.from_dict(data) for data in contacts_data]
        logger.info(f"Loaded {len(contacts)} contacts from database")
        return contacts
    except Exception as e:
        logger.error(f"Error loading contacts: {str(e)}")
        return []

def get_contact_by_id(contact_id: str) -> Optional[Contact]:
    """
    Get a contact by ID
    Args:
        contact_id: The ID of the contact to get
    Returns:
        Contact object if found, None otherwise
    """
    contacts = load_all_contacts()
    for contact in contacts:
        if contact.id == contact_id:
            return contact
    return None

def update_contact(contact: Contact) -> bool:
    """
    Update a contact in the database
    Args:
        contact: Contact object with updated information
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        contacts = load_all_contacts()
        updated = False
        
        for i, existing_contact in enumerate(contacts):
            if existing_contact.id == contact.id:
                contacts[i] = contact
                updated = True
                break
        
        if updated:
            with open(DB_FILE, 'w') as f:
                contacts_data = [c.to_dict() for c in contacts]
                json.dump(contacts_data, f, indent=2)
            logger.info(f"Updated contact: {contact.name}")
            return True
        else:
            logger.warning(f"Contact not found for update: {contact.id}")
            return False
    except Exception as e:
        logger.error(f"Error updating contact: {str(e)}")
        return False

def delete_contact(contact_id: str) -> bool:
    """
    Delete a contact from the database
    Args:
        contact_id: The ID of the contact to delete
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        contacts = load_all_contacts()
        original_count = len(contacts)
        
        # Filter out the contact to delete
        contacts = [c for c in contacts if c.id != contact_id]
        
        if len(contacts) < original_count:
            with open(DB_FILE, 'w') as f:
                contacts_data = [c.to_dict() for c in contacts]
                json.dump(contacts_data, f, indent=2)
            logger.info(f"Deleted contact: {contact_id}")
            return True
        else:
            logger.warning(f"Contact not found for deletion: {contact_id}")
            return False
    except Exception as e:
        logger.error(f"Error deleting contact: {str(e)}")
        return False

def search_contacts(query: str) -> List[Contact]:
    """
    Search contacts by name, organization, or email
    Args:
        query: Search query string
    Returns:
        List of matching Contact objects
    """
    if not query:
        return load_all_contacts()
    
    contacts = load_all_contacts()
    query = query.lower()
    results = []
    
    for contact in contacts:
        # Search in name, organization, and email
        if (contact.name and query in contact.name.lower()) or \
           (contact.organization and query in contact.organization.lower()) or \
           (contact.email and query in contact.email.lower()):
            results.append(contact)
    
    logger.info(f"Found {len(results)} contacts matching '{query}'")
    return results
