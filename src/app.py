import streamlit as st
import speech_recognition as sr
from htmlTemplates import css, bot_template, user_template
from audio_recorder_streamlit import audio_recorder
from scripts.youtube import *
from scripts.search_keywords import *
from scripts.train import *
import shutil
import base64
import pickle
from PIL import Image
import os

@st.cache_data
def delete_image_if_exists(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    os.makedirs(folder_path)

def handle_userinput(user_question, chat):
    response = chat["conversation"]({'question': user_question})
    chat["chat_history"] = response['chat_history']
    chat["timestamps"].extend([0, get_frame(user_question)])
    chat["slides"].extend([0, check_slides(user_question)])

def load_conversation_chain(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data

# Function to transcribe audio to text
def transcribe_audio_to_text(audio_location):
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_location) as source:
        audio_data = recognizer.record(source)
        
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        print ("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        return None
    
def print_chat(i, chat):
    selected_chat = i
    if not chat:
        st.session_state.chats[selected_chat] = {"chat_history": [], "timestamps": [], "slides": [], "conversation": None}
    else:
        token=(False, None)

        for i, message in enumerate(chat["chat_history"]):
            if i % 2 == 0:
                st.write(user_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)
                if os.path.exists(f"conversation_images/{message.content}.jpg"):
                    token=(True, message.content)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                if token[0] and chat["timestamps"][i][1] and chat["slides"][i][2]:
                    # if chat["timestamps"][i][2] > chat["slides"][i][3]:
                    st.image(
                        f"conversation_images/{token[1]}.jpg",
                        caption=f"https://www.youtube.com/watch?v={chat['timestamps'][i][1]}&t={int(chat['timestamps'][i][0])}"
                    )  
                    # if chat["timestamps"][i][2] < chat["slides"][i][3]:
                    img = Image.open(chat["slides"][i][2])
                    st.image(
                        img,
                        caption=f"Page {chat['slides'][i][0]} of {chat['slides'][i][1]}"
                    )
                elif token[0] and chat["timestamps"][i][1]:
                    st.image(
                        f"conversation_images/{token[1]}.jpg",
                        caption=f"https://www.youtube.com/watch?v={chat['timestamps'][i][1]}&t={int(chat['timestamps'][i][0])}"
                    )    
                elif chat["slides"][i][2]:
                    img = Image.open(chat["slides"][i][2])
                    st.image(
                        img,
                        caption=f"Page {chat['slides'][i][0]} of {chat['slides'][i][1]}"
                    )

                token=(False, None)

def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
@st.cache_data(show_spinner=False)
def read_pdf(my_pdf):
    with open('beckendrof/raydiant/master/data/piazza_data.txt', 'r', encoding='utf-8') as file:
        piazza_text = file.read()
    pdf_text = get_pdf_text(my_pdf)
    raw_text = piazza_text + pdf_text
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    return get_conversation_chain(vectorstore)

    
def main():
    st.set_page_config(
        page_title="Chat",
        page_icon=":teacher:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    delete_image_if_exists("conversation_images")
    load_dotenv()
    st.write(css, unsafe_allow_html=True)

    st.title("Raydiant Teaching Assistant")

    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = 0

    img_path = "beckendrof/raydiant/master/data/logo.png"
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    with st.sidebar:
        if "chats" not in st.session_state:
            st.session_state.chats = [{"chat_history": [], "timestamps": [], "slides": [], "conversation": None}]

        if st.button("New Chat"):
            selected_chat = len(st.session_state.chats)
            st.session_state.chats.append({"chat_history": [], "timestamps": [], "slides": [], "conversation": None})

        chat_options = [f"Chat {i+1}" for i in range(len(st.session_state.chats))]
        selected_chat = st.sidebar.radio("Select Chat:", chat_options)

        st.session_state.selected_chat = int(selected_chat.split()[-1]) - 1

    st.sidebar.markdown("---")
    st.sidebar.markdown("Upload any relevent documents here so that Raydiant can help you with your questions better.")
    my_upload = st.sidebar.file_uploader("", type=["pdf"], label_visibility="collapsed", accept_multiple_files = True)

    if st.session_state.chats[st.session_state.selected_chat]["conversation"] is None:
        st.session_state.chats[st.session_state.selected_chat]["conversation"] = load_conversation_chain("beckendrof/raydiant/master/data/conversation_chain.pickle")

    if my_upload is not None:
        if not st.session_state.chats[st.session_state.selected_chat]["chat_history"]:
            st.session_state.chats[st.session_state.selected_chat]["conversation"] = read_pdf(my_upload)
        else:
            st.sidebar.markdown("Please start a new chat to upload a new document.")

    audio_bytes = audio_recorder("", "")
    if audio_bytes:
        audio_location = "beckendrof/raydiant/master/data/audio_file.wav"
        with open(audio_location, "wb") as f:
            f.write(audio_bytes)
        user_question = transcribe_audio_to_text(audio_location)
        if user_question:
            st.chat_input("Ask questions")
            handle_userinput(user_question, st.session_state.chats[st.session_state.selected_chat])
    else:
        user_question = st.chat_input("Ask questions")
        if user_question:
            handle_userinput(user_question, st.session_state.chats[st.session_state.selected_chat])

    print_chat(st.session_state.selected_chat, st.session_state.chats[st.session_state.selected_chat])

if __name__ == '__main__':
    main()
