# backend/services/piazza_service.py
from piazza_api import Piazza
from bs4 import BeautifulSoup
import re
import os
import time
from dotenv import load_dotenv

load_dotenv()

class PiazzaService:
    def __init__(self):
        self.email = os.getenv("PIAZZA_USERNAME")
        self.password = os.getenv("PIAZZA_PASSWORD")
        self.class_id = os.getenv("PIAZZA_CLASS_ID")
        self.network = self._login()

    def _login(self):
        """Login to Piazza and return the network object."""
        p = Piazza()
        p.user_login(email=self.email, password=self.password)
        return p.network(self.class_id)

    def fetch_posts(self, num_posts=100):
        """Fetch posts from the Piazza class."""
        posts_data = []
        posts = self.network.iter_all_posts(limit=num_posts)
        for k, post in enumerate(posts):
            time.sleep(1)
            post_text = self._clean_text(post['history'][0]['content'])
            post_data = {
                "post": f"post{k + 1}: {post_text}",
                "comments": []
            }
            for i, comment in enumerate(post['children']):
                comment_text = self._clean_text(comment['subject'])
                comment_data = {
                    "comment": f"post{k + 1}-comment{i + 1}: {comment_text}",
                    "replies": []
                }
                if comment['children']:
                    for j, reply in enumerate(comment['children']):
                        reply_text = self._clean_text(reply['subject'])
                        comment_data['replies'].append(
                            f"post{k + 1}-comment{i + 1}-reply{j + 1}: {reply_text}"
                        )
                post_data["comments"].append(comment_data)
            posts_data.append(post_data)
        return posts_data

    def _clean_text(self, text):
        """Clean and sanitize the text content."""
        text = BeautifulSoup(text, 'html.parser').get_text()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\n\r\u2028\u2029]', '', text)
        return text
