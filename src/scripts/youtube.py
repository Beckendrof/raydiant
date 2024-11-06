import cv2
import networkx as nx
import yt_dlp as youtube_dl
from difflib import SequenceMatcher
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import spacy

load_dotenv()

import en_core_web_sm
nlp = en_core_web_sm.load()

def save_frame_as_image(frame, output_path):
    cv2.imwrite(output_path, frame)

def extract_frame_from_youtube(video_url, start_time, output_path):
    try:
        start_time = float(start_time) 

        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])
            for format in formats:
                try:
                    format['filesize'] = int(format.get('filesize', 0))
                except:
                    format['filesize'] = 0
            best_format = max(formats, key=lambda x: x.get('filesize', 0))

        cap = cv2.VideoCapture(best_format['url'])

        if not cap.isOpened():
            print("Error: Could not open the video stream.")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(start_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if ret:
            save_frame_as_image(frame, output_path)
        else:
            print("Error: Could not read frame.")

        cap.release()

    except Exception as e:
        print("Error:", e)


def find_best_timestamp(transcript, query, start, duration, chunk_length=100):
    chunks = [transcript[i:i+chunk_length] for i in range(0, len(transcript), chunk_length)]
    best_score = 0.4
    best_timestamp = None

    total_duration = duration * len(chunks)  # Total duration of the video in seconds

    for index, chunk in enumerate(chunks):
        score = SequenceMatcher(None, query.lower(), chunk.lower()).ratio()
        if score > best_score:
            chunk_start_time = start + (index * chunk_length / len(transcript)) * total_duration
            chunk_midpoint = chunk_start_time + (chunk_length / 2) * total_duration / len(transcript)
            best_timestamp = chunk_midpoint

    return (best_timestamp, score)

def search_videos(query):
    try:
        ydl_opts = {
            'format': 'best',  # Choose the best quality format
            'quiet': True,     # Suppress console output
            'extract_flat': True,  # Extract only the direct video URL
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                # Search for videos matching the query
                search_results = ydl.extract_info(f"ytsearch:{query}", download=False)
                if 'entries' in search_results:
                    if search_results['entries']:
                        first_video_link = search_results['entries'][0]['url']
                        return first_video_link
                    else:
                        return None
            except youtube_dl.utils.DownloadError as e:
                print("Error:", e)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        return None

def extract_timestamp(video_id, query):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        best_timestamp = None

        for transcript in transcript_list:
            translated_transcript = transcript.translate('en').fetch()
            
            for segment in translated_transcript:
                text = segment['text']
                start = segment['start']
                duration = segment['duration']
                end = start + duration
                
                if query:
                    best_timestamp, score = find_best_timestamp(text, query, start, duration)
                    return best_timestamp, score
        return None
    except:
        print("Subtitles are disabled...")
        return None
    
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

def get_frame(query):
    if "course" in query.lower() or "professor" in query.lower():
        print("Query contains sensitive words. Skipping...")
        return None, None, None
    
    query = query[:300]
    video = search_videos(query)

    if video:
        print(video)
        video_id = video.split("v=")[1]

        best_timestamp, score = extract_timestamp(video_id, query)
        if best_timestamp:
            extract_frame_from_youtube(f"https://www.youtube.com/watch?v={video_id}", best_timestamp, f"conversation_images/{query}.jpg")
            print("youtube score:", score)
            return best_timestamp, video_id, score
        else:
            print("No transcripts available for this video.")
            return None, None, None
    else:
        print("No videos found for the given query.")
        return None, None, None
