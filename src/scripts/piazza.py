from piazza_api import Piazza
from bs4 import BeautifulSoup
import json
import re
import os
import time
from dotenv import load_dotenv

load_dotenv()

p = Piazza()
email = os.getenv('USERNAME')
password = os.getenv("PASSWORD")
p.user_login(email=email, password=password)

class_id = 'lll6cacyxjfg3'
network = p.network(class_id)

num_posts = 100

data = []

with open('piazza_data.txt', 'w', encoding='utf-8') as file:
    posts = network.iter_all_posts(limit=num_posts)
    for k, post in enumerate(posts):
        time.sleep(1)
        post_text = BeautifulSoup(post['history'][0]['content'], 'html.parser').get_text()
        post_text = re.sub(r'\s+', ' ', post_text)
        post_text = re.sub(r'[\n\r\u2028\u2029]', '', post_text)
        file.write(f"post{k+1}: {post_text}\n")

        for i, comment in enumerate(post['children']):
            try:
                comment_text = BeautifulSoup(comment['subject'], 'html.parser').get_text()
                comment_text = re.sub(r'\s+', ' ', comment_text)
                comment_text = re.sub(r'[\n\r\u2028\u2029]', '', comment_text)
                file.write(f"post{k+1}-comment{i + 1}: {comment_text}\n")

                if comment['children']:
                    for j, reply in enumerate(comment['children']):
                        reply_text = BeautifulSoup(reply['subject'], 'html.parser').get_text()
                        reply_text = re.sub(r'\s+', ' ', reply_text)
                        reply_text = re.sub(r'[\n\r\u2028\u2029]', '', reply_text)
                        file.write(f"post{k+1}-comment{i + 1}-reply{j + 1}: {reply_text}\n")
            except:
                for reply in comment['history']:
                    reply_content = reply['content']
                    reply_content = re.sub(r'\s+', ' ', reply_content)
                    reply_content = re.sub(r'[\n\r\u2028\u2029]', '', reply_content)
                    file.write(f"post{k+1}-comment{i + 1}-reply{j+1}: {reply_content}\n")

        file.write("\n")