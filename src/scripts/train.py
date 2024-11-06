import os
import fitz
import spacy
import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import OpenAI
import networkx as nx
import pickle

nlp = spacy.load("en_core_web_sm")
load_dotenv()

def extract_keywords(text, num_keywords=5):
    doc = nlp(text)
    
    irrelevant_pos_tags = ["VERB"]
    
    G = nx.Graph()
    for sentence in doc.sents:
        words = [token.text for token in sentence if not token.is_stop and token.is_alpha and token.pos_ not in irrelevant_pos_tags]
        G.add_nodes_from(words)
        
        for i, word1 in enumerate(words):
            for j, word2 in enumerate(words):
                if i != j:
                    G.add_edge(word1, word2)

    node_scores = nx.pagerank(G)
    
    top_keywords = [keyword for keyword, score in sorted(node_scores.items(), key=lambda x: x[1], reverse=True)[:num_keywords]]
    return top_keywords

@st.cache_data(show_spinner=False)
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

@st.cache_data(show_spinner=False)
def preprocess_text(text):
    lines = text.split("\n")
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    processed_text = "\n".join(lines)
    if len(processed_text) > 480:
        return processed_text[:480]
    return processed_text

@st.cache_data(show_spinner=False)
def preprocess_chunks(chunks):
    preprocessed_chunks = []
    for chunk in chunks:
        preprocessed_chunk = preprocess_text(chunk)
        preprocessed_chunks.append(preprocessed_chunk)
        if len(preprocessed_chunk) > 480:
            print(f"Warning: Chunk length exceeds 480 characters after preprocessing. Length: {len(preprocessed_chunk)}")
    return preprocessed_chunks

@st.cache_data(show_spinner=False)
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    chunks = preprocess_chunks(chunks)
    return chunks

@st.cache_data(show_spinner=False)
def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = OpenAI(
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-3.5-turbo-1106"
    )
    # template = """You are a Teaching Assistant having a conversation with a student. The student asks you a question, and you respond with an answer. If you don't know the answer them simply reply with "I do not have enough information to answer that". Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
        
    #     Chat History:
    #     {chat_history}
    #     Follow Up Input: {question}
    #     Standalone question:"""
    
    # custom_prompt_template = PromptTemplate(
    #     input_variables=['chat_history', 'question'],
    #     template=template
    # )
    
    memory = ConversationBufferMemory(llm=llm, memory_key="chat_history", output_key='answer', return_messages=True)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}),
        memory=memory
    )
    
    with open("data/conversation_chain.pickle", 'wb') as f:
        pickle.dump(conversation_chain, f)
        print("Conversation chain saved to file:", "data/conversation_chain.pickle")

    return conversation_chain


def search_keywords(question, text_per_page, pdf_name, output_dir):
    keywords = extract_keywords(question)
    print("Keywords:", keywords)
    
    if not keywords:
        return None, None, None

    page_scores = {}
    
    for page_num, text in enumerate(text_per_page, start=1):
        score = sum(keyword.lower() in text.lower() for keyword in keywords)
        page_scores[page_num] = score
    
    sorted_pages = sorted(page_scores.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_pages:
        top_page_num, top_score = sorted_pages[0]
        if top_score > 1:
            img_path = os.path.join(output_dir, f"Page_{top_page_num}.jpg")
            return top_page_num, pdf_name, img_path
    
    return None, None, None

def save_image(pdf_path, output_dir):
    pdf_document = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(os.path.join(output_dir, f"Page_{page_num + 1}.jpg"))

def main():
    pdf_path = "data/Lecture_slides.pdf"
    output_dir = "data/img"
    save_image(pdf_path, output_dir)
    with open('data/piazza_data.txt', 'r', encoding='utf-8') as file:
        raw_text = file.read()

    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    get_conversation_chain(vectorstore)


if __name__ == '__main__':
    main()
