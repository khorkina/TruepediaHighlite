import streamlit as st
import json
import os
import re
import time

# Path to the highlights storage file
HIGHLIGHTS_FILE = "data/highlights.json"

def ensure_data_dir_exists():
    """Ensure the data directory exists"""
    os.makedirs("data", exist_ok=True)

def load_highlights():
    """
    Load all highlights from the JSON file
    
    Returns:
        dict: Dictionary of all highlights
    """
    ensure_data_dir_exists()
    
    if not os.path.exists(HIGHLIGHTS_FILE):
        return {}
    
    try:
        with open(HIGHLIGHTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted or doesn't exist, return empty dict
        return {}

def save_highlights(highlights_data):
    """
    Save all highlights to the JSON file
    
    Args:
        highlights_data (dict): Dictionary of all highlights
    """
    ensure_data_dir_exists()
    
    with open(HIGHLIGHTS_FILE, 'w') as f:
        json.dump(highlights_data, f, indent=2)

def get_highlights(article_id):
    """
    Get highlights for a specific article
    
    Args:
        article_id (str): Unique identifier for the article
        
    Returns:
        list: List of highlight objects for the article
    """
    all_highlights = load_highlights()
    return all_highlights.get(article_id, [])

def save_highlight(article_id, text_to_highlight, context):
    """
    Save a new highlight for an article
    
    Args:
        article_id (str): Unique identifier for the article
        text_to_highlight (str): Text to be highlighted
        context (str): Section or context where the highlight is made
    """
    if not text_to_highlight or len(text_to_highlight.strip()) == 0:
        return
    
    # Load existing highlights
    all_highlights = load_highlights()
    
    # Get highlights for this article or create empty list
    article_highlights = all_highlights.get(article_id, [])
    
    # Create a new highlight object
    new_highlight = {
        "text": text_to_highlight.strip(),
        "context": context,
        "timestamp": time.time()
    }
    
    # Add the new highlight
    article_highlights.append(new_highlight)
    
    # Update the highlights for this article
    all_highlights[article_id] = article_highlights
    
    # Save all highlights
    save_highlights(all_highlights)

def apply_highlights_to_text(text, highlights):
    """
    Apply highlights to a text by wrapping the highlighted phrases in <mark> tags
    
    Args:
        text (str): The original text
        highlights (list): List of highlight objects
        
    Returns:
        str: Text with highlight markup
    """
    if not text or not highlights:
        return text
    
    # Sort highlights by length (longest first) to handle nested highlights
    highlights_texts = sorted([h["text"] for h in highlights], key=len, reverse=True)
    
    # Replace each highlight with a marked version
    for highlight_text in highlights_texts:
        # Escape special regex characters
        escaped_text = re.escape(highlight_text)
        # Replace the text with a marked version
        # Use regex with word boundaries where possible to avoid partial word matches
        pattern = f"(?<![a-zA-Z0-9]){escaped_text}(?![a-zA-Z0-9])" 
        try:
            text = re.sub(
                pattern, 
                f"<mark>{highlight_text}</mark>", 
                text, 
                flags=re.IGNORECASE
            )
        except re.error:
            # Fallback for complex patterns
            text = text.replace(highlight_text, f"<mark>{highlight_text}</mark>")
    
    return text

def create_highlight_interface(text, article_id, context):
    """
    Create an interface for highlighting text
    
    Args:
        text (str): The text that can be highlighted
        article_id (str): Unique identifier for the article
        context (str): Section or context identifier
    """
    # Text input for the highlighted text
    highlight_text = st.text_area(
        "Part for review:", 
        key=f"highlight_input_{context}",
        help="Enter the exact text from the article that you want to review"
    )
    
    # Save highlight button
    if st.button("Mark for Review", key=f"highlight_btn_{context}", 
                 help="Mark this text for review - visible to all users"):
        if highlight_text:
            # Check if the text is actually in the content
            if highlight_text in text:
                save_highlight(article_id, highlight_text, context)
                st.success("Section marked for review! It will now be visible to all users.")
                # Rerun to show the highlight without trying to clear the input
                st.rerun()
            else:
                st.error("The text you entered wasn't found in this section. Please copy and paste the exact text from the article.")
        else:
            st.warning("Please enter some text to mark for review.")
