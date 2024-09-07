# RAYDIANT
An AI Teaching Assistant chatbot pwoered by a RAG system that is trained and live updated on your course. Works on RAG system and uses openAI API.

### Instructions
- TO run the app, run the following code in your terminal
```
streamlit run src/app.py
```

- To pretrain and fetch certain data files, run the foolowing code before running the main app
```
python3 src/scripts/scrape.py
python3 src/scripts/train.py
```