# Personal CRM Assistant

A privacy-focused Personal CRM assistant that extracts contact information from various sources, organizes it into a searchable database, and helps users maintain their professional network.

## Features

- Extract contact details from PDF documents and images (business cards, conference agendas)
- Parse names, titles, organizations, emails, and phone numbers
- Store contacts in a structured database
- Search and filter contacts
- Simple UI dashboard for interaction

## Getting Started

### Prerequisites

- Python 3.8+
- Required libraries listed in `requirements.txt`
- A Google API key for Gemini (or OpenAI API key for GPT-4)

### Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### Running the Application

```
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application
- `document_processor.py`: Functions for extracting text from documents
- `contact_extractor.py`: LLM-based contact information extraction using Gemini
- `db.py`: Database functionality for storing and retrieving contacts
- `models.py`: Data models for the application
- `utils.py`: Utility functions

## Usage

1. Upload a document (PDF) or image (business card)
2. The system will extract contacts automatically
3. View, search, and manage your contacts through the UI
4. Add contacts manually if needed 