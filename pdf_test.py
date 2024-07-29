import streamlit as st
import PyPDF2
import spacy
from collections import Counter

# Load the SpaCy model
nlp = spacy.load('en_core_web_sm')

# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract named entities
def extract_named_entities(doc):
    return [ent.text for ent in doc.ents]

# Function to extract keywords
def extract_keywords(doc, top_n=10):
    words = [token.text for token in doc if not token.is_stop and not token.is_punct and token.pos_ in ['NOUN', 'PROPN', 'ADJ']]
    return Counter(words).most_common(top_n)

# Function to highlight similarities and differences
def highlight_similarities_differences(doc1, doc2):
    # Named Entities
    ents1 = set(extract_named_entities(doc1))
    ents2 = set(extract_named_entities(doc2))
    common_ents = ents1.intersection(ents2)
    unique_ents1 = ents1 - ents2
    unique_ents2 = ents2 - ents1

    # Keywords
    kw1 = dict(extract_keywords(doc1))
    kw2 = dict(extract_keywords(doc2))
    common_kw = set(kw1.keys()).intersection(set(kw2.keys()))
    unique_kw1 = set(kw1.keys()) - set(kw2.keys())
    unique_kw2 = set(kw2.keys()) - set(kw1.keys())

    return {
        "common_entities": common_ents,
        "unique_entities1": unique_ents1,
        "unique_entities2": unique_ents2,
        "common_keywords": common_kw,
        "unique_keywords1": unique_kw1,
        "unique_keywords2": unique_kw2,
    }

# Streamlit app
st.title("PDF Text Comparison App")

# File upload
file1 = st.file_uploader("Upload First PDF", type=["pdf"])
file2 = st.file_uploader("Upload Second PDF", type=["pdf"])

if file1 and file2:
    # Extract text from the uploaded files
    text1 = extract_text_from_pdf(file1)
    text2 = extract_text_from_pdf(file2)

    # Apply NLP processing to the extracted text
    doc1 = nlp(text1)
    doc2 = nlp(text2)

    # Calculate similarity scores between the texts
    score_1_2 = doc1.similarity(doc2)

    # Display similarity score
    st.header("Similarity Score")
    st.write(f"Similarity between text from the two files: {score_1_2:.2f}")

    # Highlight similarities and differences
    highlights = highlight_similarities_differences(doc1, doc2)

    st.header("Highlights of Similarities and Differences")

    st.subheader("Named Entities")
    st.write(f"Common: {', '.join(list(highlights['common_entities'])[:5])}...")
    st.write(f"Unique to File 1: {', '.join(list(highlights['unique_entities1'])[:5])}...")
    st.write(f"Unique to File 2: {', '.join(list(highlights['unique_entities2'])[:5])}...")

    st.subheader("Keywords")
    st.write(f"Common: {', '.join(list(highlights['common_keywords'])[:5])}...")
    st.write(f"Unique to File 1: {', '.join(list(highlights['unique_keywords1'])[:5])}...")
    st.write(f"Unique to File 2: {', '.join(list(highlights['unique_keywords2'])[:5])}...")
