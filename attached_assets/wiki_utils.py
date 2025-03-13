import wikipediaapi
import wikipedia
from translate import Translator
import streamlit as st
import time

@st.cache_data(ttl=3600)
def get_wikipedia_search_results(query, language="en"):
    """
    Search Wikipedia for articles matching the query in specified language
    
    Args:
        query (str): The search term
        language (str): Language code (e.g., 'en', 'es', 'fr')
        
    Returns:
        list: List of article titles matching the query
    """
    if not query:
        return []
    
    try:
        # Set the language for the Wikipedia API
        wikipedia.set_lang(language)
        # Search for articles with the given query
        search_results = wikipedia.search(query, results=10)
        return search_results
    except Exception as e:
        st.error(f"Error searching Wikipedia: {str(e)}")
        return []

@st.cache_data(ttl=3600)
def get_article_content(title, language="en"):
    """
    Get the content of a Wikipedia article
    
    Args:
        title (str): The title of the article
        language (str): Language code (e.g., 'en', 'es', 'fr')
        
    Returns:
        dict: Dictionary containing article title, summary, content and URL
    """
    if not title:
        return None
    
    try:
        # Initialize Wikipedia API with the specified language and a proper user agent
        user_agent = "TruePedia/1.0 (https://replit.com/; truepedia@example.com) python-wikipediaapi"
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent=user_agent,
            language=language
        )
        # Get the page
        page = wiki_wiki.page(title)
        
        if not page.exists():
            return None
        
        return {
            "title": page.title,
            "summary": page.summary,
            "content": page.text,
            "url": page.fullurl
        }
    except Exception as e:
        st.error(f"Error retrieving article: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_available_languages(title, source_lang="en"):
    """
    Get available languages for a Wikipedia article
    
    Args:
        title (str): The title of the article
        source_lang (str): Source language code
        
    Returns:
        dict: Dictionary of language codes and titles
    """
    if not title:
        return {}
    
    try:
        # Initialize Wikipedia API with proper user agent
        user_agent = "TruePedia/1.0 (https://replit.com/; truepedia@example.com) python-wikipediaapi"
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent=user_agent,
            language=source_lang
        )
        # Get the page
        page = wiki_wiki.page(title)
        
        if not page.exists():
            return {}
        
        # Get langlinks (article versions in other languages)
        langlinks = page.langlinks
        available_langs = {lang: langlinks[lang].title for lang in langlinks}
        
        # Add the source language
        available_langs[source_lang] = title
        
        return available_langs
    except Exception as e:
        st.error(f"Error retrieving language versions: {str(e)}")
        return {}

@st.cache_data(ttl=3600)
def get_article_in_language(title, lang):
    """
    Get article content in the specified language
    
    Args:
        title (str): Title of the article in the specified language
        lang (str): Language code
        
    Returns:
        dict: Article content in the specified language
    """
    return get_article_content(title, lang)

def translate_text(text, to_lang, from_lang='auto'):
    """
    Translate text using free translation library
    
    Args:
        text (str): Text to translate
        to_lang (str): Target language code
        from_lang (str): Source language code
        
    Returns:
        str: Translated text
    """
    if not text:
        return ""
    
    try:
        # Using translate library (free but with limitations)
        translator = Translator(to_lang=to_lang, from_lang=from_lang)
        
        # For long texts, we need to split it into smaller chunks
        # to avoid exceeding translate library's limits
        chunk_size = 500  # Characters
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        translated_chunks = []
        for chunk in chunks:
            translation = translator.translate(chunk)
            translated_chunks.append(translation)
            # Add a small delay to avoid rate limiting
            time.sleep(0.5)
        
        return ' '.join(translated_chunks)
    except Exception as e:
        st.warning(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails

# Dictionary mapping language codes to language names
LANGUAGE_DICT = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'ko': 'Korean',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'fi': 'Finnish',
    'no': 'Norwegian',
    'da': 'Danish',
    'pl': 'Polish',
    'uk': 'Ukrainian',
    'el': 'Greek',
    'he': 'Hebrew',
    'id': 'Indonesian',
    'vi': 'Vietnamese',
    'fa': 'Persian',
    'tr': 'Turkish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'th': 'Thai'
}

# Dictionary mapping language codes to native language names
NATIVE_LANGUAGE_DICT = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'ru': 'Русский',
    'ja': '日本語',
    'zh': '中文',
    'ar': 'العربية',
    'hi': 'हिन्दी',
    'ko': '한국어',
    'nl': 'Nederlands',
    'sv': 'Svenska',
    'fi': 'Suomi',
    'no': 'Norsk',
    'da': 'Dansk',
    'pl': 'Polski',
    'uk': 'Українська',
    'el': 'Ελληνικά',
    'he': 'עברית',
    'id': 'Bahasa Indonesia',
    'vi': 'Tiếng Việt',
    'fa': 'فارسی',
    'tr': 'Türkçe',
    'cs': 'Čeština',
    'hu': 'Magyar',
    'ro': 'Română',
    'th': 'ไทย'
}

def get_language_name(lang_code):
    """
    Get the full language name from a language code
    
    Args:
        lang_code (str): Language code (e.g., 'en', 'es')
        
    Returns:
        str: Full language name
    """
    return LANGUAGE_DICT.get(lang_code, lang_code)

def get_native_language_name(lang_code):
    """
    Get the native language name from a language code
    
    Args:
        lang_code (str): Language code (e.g., 'en', 'es')
        
    Returns:
        str: Native language name
    """
    return NATIVE_LANGUAGE_DICT.get(lang_code, lang_code)

def split_content_into_sections(content):
    """
    Split article content into sections for collapsible viewing
    
    Args:
        content (str): Article content text
        
    Returns:
        list: List of dictionaries with section titles and content
    """
    if not content:
        return []
    
    # Simple section detection by looking for lines that might be headers
    lines = content.split('\n')
    sections = []
    current_section = {"title": "Introduction", "content": ""}
    
    for line in lines:
        # Check if line looks like a section header (not perfect but works for basic cases)
        if line.strip() and len(line.strip()) < 100 and not line.strip().endswith('.'):
            # If we've accumulated content in the current section, add it to sections
            if current_section["content"].strip():
                sections.append(current_section)
            
            # Start a new section
            current_section = {
                "title": line.strip(),
                "content": ""
            }
        else:
            # Add line to current section
            current_section["content"] += line + "\n"
    
    # Add the last section if it has content
    if current_section["content"].strip():
        sections.append(current_section)
    
    return sections

def display_collapsible_sections(sections):
    """
    Display content sections in collapsible expanders
    
    Args:
        sections (list): List of dictionaries with section titles and content
    """
    if not sections:
        st.write("No content available")
        return
    
    # Display each section in an expander
    for i, section in enumerate(sections):
        # First section expanded by default, others collapsed
        with st.expander(section["title"], expanded=(i == 0)):
            st.markdown(section["content"])
