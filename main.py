import streamlit as st
import json
import os
from wiki_utils import (
    get_wikipedia_search_results,
    get_article_content,
    get_available_languages,
    get_article_in_language,
    translate_text,
    get_language_name,
    get_native_language_name,
    split_content_into_sections,
    LANGUAGE_DICT
)
from highlight_utils import (
    get_highlights,
    save_highlight,
    apply_highlights_to_text,
    create_highlight_interface
)

# Page configuration
st.set_page_config(
    page_title="TruePedia - Multilingual Wikipedia Search",
    page_icon="📚",
    layout="wide"
)

# CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .subheader {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .article-title {
        font-size: 2rem;
        font-weight: bold;
        color: #1565C0;
        margin-bottom: 1rem;
    }
    .article-summary {
        font-size: 1.1rem;
        color: #424242;
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .lang-button {
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .article-content {
        font-size: 1rem;
        line-height: 1.5;
    }
    .wiki-link {
        color: #1565C0;
        text-decoration: none;
    }
    .wiki-link:hover {
        text-decoration: underline;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #757575;
    }
    .search-tag {
        display: inline-block;
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 8px 16px;
        margin: 4px;
        border-radius: 20px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s;
        border: 1px solid #BBDEFB;
    }
    .search-tag:hover {
        background-color: #BBDEFB;
        border-color: #1565C0;
    }
    mark {
        background-color: #FFFF00;
        padding: 0 2px;
    }
    .highlight-active {
        cursor: crosshair;
    }
    .highlight-btn {
        background-color: #FFF59D;
        color: #333;
        border: 1px solid #FBC02D;
    }
    .highlight-btn:hover {
        background-color: #FFEB3B;
    }
    .highlight-instructions {
        background-color: #FFF9C4;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'current_article' not in st.session_state:
    st.session_state.current_article = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'available_languages' not in st.session_state:
    st.session_state.available_languages = {}
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'en'
if 'translate_to' not in st.session_state:
    st.session_state.translate_to = None
if 'show_translation' not in st.session_state:
    st.session_state.show_translation = False
if 'highlight_mode' not in st.session_state:
    st.session_state.highlight_mode = False

# Title and description
st.markdown('<div class="main-header">TruePedia</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Multilingual Wikipedia Search & Translation</div>', unsafe_allow_html=True)

# Sidebar for search and settings
with st.sidebar:
    st.subheader("Search Wikipedia")
    
    # Language selection for search
    search_lang = st.selectbox(
        "Search Language", 
        options=list(LANGUAGE_DICT.keys()),
        format_func=lambda x: f"{get_language_name(x)} ({x})"
    )
    
    # Search box
    search_query = st.text_input("Enter your search query", key="search_box")
    
    if st.button("Search"):
        if search_query:
            with st.spinner(f"Searching Wikipedia in {get_language_name(search_lang)}..."):
                st.session_state.search_results = get_wikipedia_search_results(search_query, search_lang)
                st.session_state.current_article = None
                st.session_state.available_languages = {}
                st.session_state.current_language = search_lang
                st.session_state.show_translation = False
    
    # Show search results if available - as tags now
    if st.session_state.search_results:
        st.write("### Search Results")
        # Use columns to create a tag-like display
        cols = st.columns([1, 1])
        for idx, result in enumerate(st.session_state.search_results):
            col_idx = idx % 2
            with cols[col_idx]:
                tag_html = f"""
                <div class="search-tag" onclick="
                    const data = {{value: '{result}'}};
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        selectedTag: data
                    }}, '*');
                ">
                    {result}
                </div>
                """
                st.markdown(tag_html, unsafe_allow_html=True)
        
        # Hidden component to receive the tag click
        selected_tag = st.text_input("", key="selected_tag", label_visibility="collapsed")
        
        if selected_tag:
            with st.spinner(f"Loading article: {selected_tag}..."):
                st.session_state.current_article = get_article_content(selected_tag, st.session_state.current_language)
                if st.session_state.current_article:
                    st.session_state.available_languages = get_available_languages(
                        selected_tag, 
                        st.session_state.current_language
                    )
                    st.session_state.show_translation = False
                    # Clear the selected tag after loading
                    st.session_state.selected_tag = ""
                    st.rerun()
    
    # Translation settings
    if st.session_state.current_article:
        st.subheader("Translation")
        st.session_state.translate_to = st.selectbox(
            "Translate To",
            options=list(LANGUAGE_DICT.keys()),
            format_func=lambda x: f"{get_language_name(x)} ({x})",
            key="translate_lang"
        )
        
        if st.button("Translate Article"):
            st.session_state.show_translation = True
    
    # Highlighting controls
    if st.session_state.current_article:
        st.subheader("Collaborative Highlighting")
        
        highlight_toggle = st.toggle("Enable Highlighting Mode", value=st.session_state.highlight_mode)
        if highlight_toggle != st.session_state.highlight_mode:
            st.session_state.highlight_mode = highlight_toggle
            st.rerun()
            
        if st.session_state.highlight_mode:
            st.markdown("""
            <div class="highlight-instructions">
                <strong>How to highlight:</strong><br>
                1. Select text in the article<br>
                2. Click 'Save Highlight'<br>
                3. Your highlights will be visible to all users
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="footer">
        TruePedia uses Wikipedia API and free translation libraries<br>
        💡 Search in any language, explore articles, and collaborate with highlights
    </div>
    """, unsafe_allow_html=True)

# Main content area
if st.session_state.current_article:
    article = st.session_state.current_article
    
    # Display article title and summary
    st.markdown(f'<div class="article-title">{article["title"]}</div>', unsafe_allow_html=True)
    
    # Display Wikipedia link
    st.markdown(f'<a href="{article["url"]}" target="_blank" class="wiki-link">📖 View on Wikipedia</a>', unsafe_allow_html=True)
    
    # Display language options in an organized dropdown
    with st.expander("Available Languages", expanded=True):
        # Group languages by region/script for better organization
        st.write("Select a language to view this article in:")
        
        # Create a selectbox with native language names
        # Get the list of available languages with their native names
        language_options = []
        for lang_code, lang_title in st.session_state.available_languages.items():
            native_name = get_native_language_name(lang_code)
            display_name = f"{native_name} - {get_language_name(lang_code)} ({lang_code})"
            language_options.append((lang_code, lang_title, display_name))
        
        # Sort by display name
        language_options.sort(key=lambda x: x[2])
        
        # Create the dropdown
        if 'selected_language' not in st.session_state:
            st.session_state.selected_language = st.session_state.current_language
            
        selected_lang_index = 0
        for i, (code, _, _) in enumerate(language_options):
            if code == st.session_state.current_language:
                selected_lang_index = i
                break
                
        selected_option = st.selectbox(
            "Choose Language",
            options=range(len(language_options)),
            format_func=lambda i: language_options[i][2],
            index=selected_lang_index,
            key="language_selector"
        )
        
        # Button to load the selected language
        if st.button("View in Selected Language", use_container_width=True):
            lang_code, lang_title, _ = language_options[selected_option]
            with st.spinner(f"Loading article in {get_language_name(lang_code)}..."):
                st.session_state.current_article = get_article_in_language(lang_title, lang_code)
                st.session_state.current_language = lang_code
                st.session_state.show_translation = False
                st.rerun()
    
    # Create tabs for summary and full content
    summary_tab, content_tab = st.tabs(["Summary", "Full Content"])
    
    with summary_tab:
        # If translation is requested, show translated summary
        if st.session_state.show_translation and st.session_state.translate_to != st.session_state.current_language:
            with st.spinner(f"Translating summary to {get_language_name(st.session_state.translate_to)}..."):
                translated_summary = translate_text(
                    article["summary"],
                    st.session_state.translate_to,
                    st.session_state.current_language
                )
                
                # Get and apply highlights
                article_id = f"{article['title']}_{st.session_state.current_language}"
                highlights = get_highlights(article_id)
                
                # Apply highlights to the summary
                highlighted_text = apply_highlights_to_text(translated_summary, highlights)
                
                # Show the highlighted text
                st.markdown(f'<div class="article-summary">{highlighted_text}</div>', unsafe_allow_html=True)
                
                # Add highlighting interface if needed
                if st.session_state.highlight_mode:
                    create_highlight_interface(translated_summary, article_id, "summary")
        else:
            # Get and apply highlights
            article_id = f"{article['title']}_{st.session_state.current_language}"
            highlights = get_highlights(article_id)
            
            # Apply highlights to the summary
            highlighted_text = apply_highlights_to_text(article["summary"], highlights)
            
            # Show the highlighted text
            st.markdown(f'<div class="article-summary">{highlighted_text}</div>', unsafe_allow_html=True)
            
            # Add highlighting interface if needed
            if st.session_state.highlight_mode:
                create_highlight_interface(article["summary"], article_id, "summary")
    
    with content_tab:
        # Make article content collapsible in sections
        if st.session_state.show_translation and st.session_state.translate_to != st.session_state.current_language:
            with st.spinner(f"Translating content to {get_language_name(st.session_state.translate_to)}..."):
                # Only translate a portion of the content to avoid rate limits
                content_preview = article["content"][:3000] + "..." if len(article["content"]) > 3000 else article["content"]
                translated_content = translate_text(
                    content_preview,
                    st.session_state.translate_to,
                    st.session_state.current_language
                )
                
                # Article ID for highlighting
                article_id = f"{article['title']}_{st.session_state.current_language}"
                
                # Split content into sections for collapsible viewing
                sections = split_content_into_sections(translated_content)
                
                # Get highlights
                highlights = get_highlights(article_id)
                
                # For each section, apply highlights and create highlight interface
                for i, section in enumerate(sections):
                    with st.expander(section["title"], expanded=(i == 0)):
                        highlighted_content = apply_highlights_to_text(section["content"], highlights)
                        st.markdown(highlighted_content, unsafe_allow_html=True)
                        
                        if st.session_state.highlight_mode:
                            create_highlight_interface(section["content"], article_id, f"section_{i}")
                
                if len(article["content"]) > 3000:
                    st.info("Only a portion of the content has been translated due to length limitations.")
        else:
            # Split content into sections for collapsible viewing
            sections = split_content_into_sections(article["content"])
            
            # Article ID for highlighting
            article_id = f"{article['title']}_{st.session_state.current_language}"
            
            # Get highlights
            highlights = get_highlights(article_id)
            
            # For each section, apply highlights and create highlight interface
            for i, section in enumerate(sections):
                with st.expander(section["title"], expanded=(i == 0)):
                    highlighted_content = apply_highlights_to_text(section["content"], highlights)
                    st.markdown(highlighted_content, unsafe_allow_html=True)
                    
                    if st.session_state.highlight_mode:
                        create_highlight_interface(section["content"], article_id, f"section_{i}")
else:
    # Welcome message when no article is selected
    st.info("👈 Search for a Wikipedia article in any language to get started!")
    
    # Brief instructions
    st.markdown("""
    ### How to use TruePedia:
    
    1. 🔍 **Search**: Enter a query and select your preferred language
    2. 📝 **Select**: Choose an article from the search results (displayed as tags)
    3. 🌐 **Explore**: View the article in different languages
    4. 🔄 **Translate**: Translate the article content to your preferred language
    5. ✨ **Collaborate**: Highlight important passages for other users to see
    
    TruePedia gives you access to Wikipedia content across multiple languages, provides translation capabilities, and now allows collaborative highlighting for better knowledge sharing.
    """)
