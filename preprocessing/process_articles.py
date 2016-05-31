"""
Script to preprocess NU.nl news articles.

Resources:
http://stackoverflow.com/questions/5486337/how-to-remove-stop-words-using-nltk-or-python?rq=1.
"""
import bson
import re

from nltk.corpus import stopwords
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'nu'
collection_name = 'articles'
processed_collection_name = 'articles_processed'

db = Database(MongoClient(), db_name)
collection = Collection(db, collection_name)
processed_collection = Collection(db, processed_collection_name)


def preprocess():
    try:
        stop_words = stopwords.words('dutch')
    except LookupError as e:
        print e
        exit()

    processed_articles = processed_collection.find({}, {'article_id': 1})
    processed_ids = [processed_article['article'].id for processed_article in processed_articles]
    print 'Skipping %d preprocessed articles...' % len(processed_ids)

    articles = collection.find({'_id': {'$nin': processed_ids}})
    print 'Preprocessing %d articles...' % articles.count()
    processed_articles = []
    for article in articles:
        title = preprocess_text(article.get('title', ''), stop_words)
        text = preprocess_text(article.get('text', ''), stop_words)

        article['title'] = title
        article['text'] = text
        article['article_id'] = bson.DBRef(processed_collection_name, article['_id'])

        processed_articles.append(article)
    processed_collection.insert_many(processed_articles)
    print 'Saved preprocessed articles.'


def preprocess_text(text, stop_words):
    """
    :param text:
    :param stop_words:
    :return:
    """
    text = text.lower()
    text = re.split('\W+', text)
    return ' '.join(word for word in text if word not in stop_words)

if __name__ == '__main__':
    preprocess()
