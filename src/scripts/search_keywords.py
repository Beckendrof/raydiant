import os
import fitz
import spacy
import networkx as nx
from difflib import SequenceMatcher

# Load English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    text_per_page = []
    pdf_document = fitz.open(pdf_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        text_per_page.append(text)
    return text_per_page

# Step 2: Extract keywords from each page
def extract_keywords(text, num_keywords=5):
    # Tokenize the text using spaCy
    doc = nlp(text)
    
    # Define irrelevant part-of-speech tags (e.g., verbs)
    irrelevant_pos_tags = ["VERB"]
    
    # Create a graph representation of the text
    G = nx.Graph()
    for sentence in doc.sents:
        # Add nodes (words) to the graph
        words = [token.text for token in sentence if not token.is_stop and token.is_alpha and token.pos_ not in irrelevant_pos_tags]
        G.add_nodes_from(words)
        
        # Add edges between words based on co-occurrence within a window
        for i, word1 in enumerate(words):
            for j, word2 in enumerate(words):
                if i != j:
                    G.add_edge(word1, word2)
    
    # Run PageRank algorithm to calculate node importance
    node_scores = nx.pagerank(G)
    
    # Sort nodes by importance score and extract top keywords
    top_keywords = [keyword for keyword, score in sorted(node_scores.items(), key=lambda x: x[1], reverse=True)[:num_keywords]]
    return top_keywords

def search_keywords(question, text_per_page, pdf_name, output_dir):
    keywords = extract_keywords(question)
    
    # If no keywords are extracted, return "no info found"
    if not keywords:
        return None, None, None, None
    
    # Dictionary to store page scores
    page_scores = {}
    
    # for page_num, text in enumerate(text_per_page, start=1):
    #     # Calculate score for the page based on the presence of keywords
    #     score = SequenceMatcher(None, question.lower(), text.lower()).ratio()
    #     page_scores[page_num] = score
    
    # # Sort pages based on scores in descending order
    # sorted_pages = sorted(page_scores.items(), key=lambda x: x[1], reverse=True)
    # print(sorted_pages)
    # # Return the page with the highest score
    # if sorted_pages:
    #     top_page_num, top_score = sorted_pages[0]
    #     if top_score > 0.4:
    #         img_path = os.path.join(output_dir, f"Page_{top_page_num}.jpg")
    #         print("page score:", top_score)
    #         return top_page_num, pdf_name, img_path, top_score
    #     print("page score: top_score")
    # return None, None, None, None

    page_scores = {}
    
    for page_num, text in enumerate(text_per_page, start=1):
        # Calculate score for the page based on the presence of keywords
        score = sum(keyword.lower() in text.lower() for keyword in keywords)
        page_scores[page_num] = score
    
    # Sort pages based on scores in descending order
    sorted_pages = sorted(page_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return the page with the highest score
    if sorted_pages:
        top_page_num, top_score = sorted_pages[0]
        if top_score > 1:
            img_path = os.path.join(output_dir, f"Page_{top_page_num}.jpg")
            return top_page_num, pdf_name, img_path, top_score
    
    return None, None, None, None

def check_slides(user_question):
    pdf_path = "data/Lecture_slides.pdf"
    output_dir = "data/img"
    text_per_page = extract_text_from_pdf(pdf_path)

    os.makedirs(output_dir, exist_ok=True)

    return search_keywords(user_question, text_per_page, os.path.basename(pdf_path), output_dir)