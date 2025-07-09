# articles.py
from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "articles.json")

# Load articles once
with open(ARTICLES_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)

@router.get("/articles")
def list_articles():
    return [{"id": a["id"], "title": a["title"]} for a in articles]

@router.get("/articles/{article_id}")
def get_article(article_id: int):
    for article in articles:
        if article["id"] == article_id:
            return article
    raise HTTPException(status_code=404, detail="Article not found")
