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


def get_articles_to_preprocess():
    """
    :return:
        articles in collection that 1) aren't yet referenced by a preprocessed version in processed_collection
        and 2) have had their number of comments updated
    """
    processed_articles = processed_collection.find({'article_id': {'$exists': 1}}, {'article_id': 1})
    processed_ids = [processed_article['article_id'].id for processed_article in processed_articles]
    print 'Skipping %d preprocessed articles...' % len(processed_ids)
    return collection.find({'_id': {'$nin': processed_ids}, 'num_comments': {'$ne': None}})


def preprocess(articles):
    """
    Applies preprocessing on articles using Dutch stopwords.
    Saves the preprocessed documents to processed_collection.
    :param articles: articles to preprocess
    """
    try:
        stop_words = stopwords.words('dutch')
    except LookupError as e:
        print e
        exit()

    print 'Preprocessing %d articles...' % articles.count()
    processed_articles = []
    for article in articles:
        processed_article = dict(
            article_id=bson.DBRef(collection_name, article['_id']),
            title=preprocess_text(article.get('title', ''), stop_words),
            text=preprocess_text(article.get('text', ''), stop_words),
            num_comments=article.get('num_comments', 0)
        )
        processed_articles.append(processed_article)
    if processed_articles:
        processed_collection.insert_many(processed_articles)
        print 'Saved preprocessed articles.'


def preprocess_text(text, stop_words):
    """
    :param text: text to preprocess
    :param stop_words: list of stopwords to filter text by
    :return: a lowercase version of text, split on punctuation marks and filtered by stop_words
    """
    text = text.lower()
    text = re.split('\W+', text)
    return ' '.join(word for word in text if word not in stop_words)


if __name__ == '__main__':
    preprocess(get_articles_to_preprocess())
