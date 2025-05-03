import streamlit as st
import pandas as pd
import tempfile
import os
import logging
from models import Contact
from document_processor import process_document
from contact_extractor import extract_contacts
import db
import utils
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Personal CRM Assistant",
    page_icon="📇",
    layout="wide"
)

# Initialize session state
if "contacts" not in st.session_state:
    st.session_state.contacts = []
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "show_add_contact" not in st.session_state:
    st.session_state.show_add_contact = False
if "show_contact_details" not in st.session_state:
    st.session_state.show_contact_details = None
if "extracted_contacts" not in st.session_state:
    st.session_state.extracted_contacts = []
if "review_mode" not in st.session_state:
    st.session_state.review_mode = False

# Helper functions
def load_contacts():
    """Load contacts from database"""
    st.session_state.contacts = db.load_all_contacts()

def search_contacts():
    """Search contacts based on query"""
    query = st.session_state.search_query
    st.session_state.contacts = db.search_contacts(query)

def toggle_add_contact():
    """Toggle add contact form"""
    st.session_state.show_add_contact = not st.session_state.show_add_contact
    st.session_state.show_contact_details = None

def view_contact(contact_id):
    """View contact details"""
    st.session_state.show_contact_details = contact_id
    st.session_state.show_add_contact = False

def save_extracted_contacts():
    """Save extracted contacts to database"""
    if st.session_state.extracted_contacts:
        db.save_contacts(st.session_state.extracted_contacts)
        st.session_state.extracted_contacts = []
        st.session_state.review_mode = False

load_contacts()

# Page title
st.title("Personal CRM Assistant")
st.markdown("A privacy-focused tool to manage your professional network")

# Sidebar
with st.sidebar:
    st.header("Tools")
    
    # Document upload
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Upload a PDF document or business card image",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Upload a PDF or image to extract contact information"
    )
    
    source_type = st.selectbox(
        "Source Type",
        ["Document", "Business Card", "Conference Agenda", "Meeting Notes"],
        help="Select the type of document you're uploading"
    )
    
    event_name = st.text_input(
        "Event Name (Optional)",
        help="Enter the name of the event where you collected this document"
    )
    
    process_button = st.button("Process Document")
    st.divider()
    
    # Manual add contact
    if st.button("Add Contact Manually"):
        toggle_add_contact()
    st.divider()
    
    # Search
    st.subheader("Search")
    st.text_input(
        "Search Contacts",
        key="search_query",
        on_change=search_contacts,
        placeholder="Name, organization, email..."
    )
    
    st.divider()
    
    # About
    st.subheader("About")
    st.markdown("""
        This Personal CRM Assistant helps you:
        - Extract contacts from documents
        - Organize your professional network
        - Keep track of important connections
        """)

# Main content area
if st.session_state.review_mode and st.session_state.extracted_contacts:
    # Review extracted contacts
    st.header("Review Extracted Contacts")
    st.markdown("Please review the extracted contacts before saving to your database")
    
    for i, contact in enumerate(st.session_state.extracted_contacts):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(contact.name)
            if contact.title:
                st.write(f"**Title:** {contact.title}")
            if contact.organization:
                st.write(f"**Organization:** {contact.organization}")
            if contact.email:
                st.write(f"**Email:** {contact.email}")
            if contact.phone:
                st.write(f"**Phone:** {contact.phone}")
            st.write(f"**Source:** {contact.source_document}")
        
        with col2:
            # Allow editing if needed (in a real app, we'd implement inline editing)
            if st.button(f"Remove", key=f"remove_{i}"):
                st.session_state.extracted_contacts.pop(i)
                st.rerun()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save All Contacts", use_container_width=True):
            save_extracted_contacts()
            st.success("Contacts saved successfully!")
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.extracted_contacts = []
            st.session_state.review_mode = False
            st.rerun()

elif st.session_state.show_add_contact:
    # Manual contact form
    st.header("Add Contact Manually")
    
    with st.form("contact_form"):
        name = st.text_input("Full Name *")
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Job Title")
            email = st.text_input("Email")
        
        with col2:
            organization = st.text_input("Organization")
            phone = st.text_input("Phone")
        
        linkedin = st.text_input("LinkedIn URL")
        event = st.text_input("Event")
        notes = st.text_area("Notes")
        
        tags = st.multiselect(
            "Tags",
            ["Tech", "Healthcare", "Finance", "Education", "Marketing", 
             "Sales", "Engineering", "Design", "Consulting", "Legal"]
        )
        
        submitted = st.form_submit_button("Save Contact")
        
        if submitted:
            if name:
                contact = Contact(
                    name=name,
                    title=title,
                    organization=organization,
                    email=email,
                    phone=phone,
                    linkedin=linkedin,
                    source_document="Manual Entry",
                    event=event,
                    notes=notes,
                    tags=tags
                )
                
                db.save_contacts([contact])
                st.success("Contact added successfully!")
                st.session_state.show_add_contact = False
                load_contacts()
                st.rerun()
            else:
                st.error("Name is required")

elif st.session_state.show_contact_details:
    # Contact details view
    contact = db.get_contact_by_id(st.session_state.show_contact_details)
    
    if contact:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.header(contact.name)
            
            if contact.title and contact.organization:
                st.subheader(f"{contact.title} at {contact.organization}")
            elif contact.title:
                st.subheader(contact.title)
            elif contact.organization:
                st.subheader(contact.organization)
            
            st.divider()
            
            col_a, col_b = st.columns(2)
            with col_a:
                if contact.email:
                    st.markdown(f"**Email:** {contact.email}")
                if contact.phone:
                    st.markdown(f"**Phone:** {contact.phone}")
            
            with col_b:
                if contact.linkedin:
                    st.markdown(f"**LinkedIn:** [{contact.linkedin}]({contact.linkedin})")
                if contact.event:
                    st.markdown(f"**Event:** {contact.event}")
            
            st.divider()
            
            if contact.notes:
                st.subheader("Notes")
                st.write(contact.notes)
            
            if contact.tags:
                st.subheader("Tags")
                for tag in contact.tags:
                    st.markdown(f"{tag}", unsafe_allow_html=True)
        
        with col2:
            st.subheader("Actions")
            
            if st.button("Edit Contact", use_container_width=True):
                # In a full app, we'd implement contact editing
                st.write("Edit functionality would go here")
            
            if st.button("Delete Contact", use_container_width=True):
                db.delete_contact(contact.id)
                st.success("Contact deleted successfully!")
                st.session_state.show_contact_details = None
                load_contacts()
                st.rerun()
            
            st.divider()
            
            st.subheader("Follow Up")
            if st.button("Generate Email Template", use_container_width=True):
                template = utils.suggest_follow_up_template(contact)
                st.text_area("Follow Up Template", template, height=300)
    else:
        st.error("Contact not found")
        st.session_state.show_contact_details = None

else:
    # Main dashboard view
    # Process uploaded document
    if uploaded_file is not None and process_button:
        try:
            st.info("Processing document... This may take a moment.")
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name
            
            # Open and process the file
            with open(temp_file_path, "rb") as file:
                # Extract text from document
                text = process_document(file, uploaded_file.type)
                
                # Extract contacts
                source_name = uploaded_file.name
                if event_name:
                    source_name = f"{event_name} - {source_name}"
                
                contacts = extract_contacts(text, source_name, source_type.lower())
                
                # Add event information if provided
                if event_name:
                    for contact in contacts:
                        contact.event = event_name
                
                # Set extracted contacts for review
                if contacts:
                    st.session_state.extracted_contacts = contacts
                    st.session_state.review_mode = True
                    st.rerun()
                else:
                    st.warning("No contacts found in the document.")
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")
    
    # Display contacts
    load_contacts()
    st.header(f"Contacts ({len(st.session_state.contacts)})")
    
    if not st.session_state.contacts:
        st.info("No contacts found. Upload a document or add contacts manually.")
    else:
        # Create a grid of contact cards
        cols = st.columns(3)
        
        for i, contact in enumerate(st.session_state.contacts):
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(contact.name)
                    
                    if contact.title and contact.organization:
                        st.write(f"{contact.title} at {contact.organization}")
                    elif contact.title:
                        st.write(contact.title)
                    elif contact.organization:
                        st.write(contact.organization)
                    
                    if contact.email:
                        st.write(f"📧 {contact.email}")
                    if contact.phone:
                        st.write(f"📱 {contact.phone}")
                    if contact.source_document:
                        st.write(f"Source: {contact.source_document}")
                    
                    if st.button("View Details", key=f"view_{contact.id}"):
                        view_contact(contact.id)

# Add some styling
st.markdown("""
""", unsafe_allow_html=True)

# Initialize database on first run
db.initialize_db()
