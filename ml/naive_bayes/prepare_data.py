from bson import DBRef
from collections import Counter
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'nu'
articles_processed_collection_name = 'articles_processed'

db = Database(MongoClient(), db_name)
processed_collection = Collection(db, articles_processed_collection_name)
naive_bayes_collection = Collection(db, 'vocabulary')
feature_vectors_collection = Collection(db, 'feature_vectors')


def create_vocabulary(articles):
    """
    Creates a set of all words occurring in all articles.
    """
    vocabulary = []
    for article in articles:
        vocabulary.extend(article.get('title', '').split(' '))
        vocabulary.extend(article.get('text', '').split(' '))
    return sorted(list(set(vocabulary)))


def create_feature_vectors(vocabulary, articles):
    """
    Creates a vector v of size 'len(vocabulary)' for each article.
    The value of the i-th element in v is the frequency with which the i-th term in vocabulary occurs in the article.
    """
    feature_vectors = []
    for article in articles:
        # Determine the frequency of each term in article
        text = article.get('title').split(' ') + article.get('text').split(' ')
        term_counts = Counter(text)
        # Represent article as vector of term occurrences
        feature_vector = [0] * len(vocabulary)
        for index, term in enumerate(vocabulary):
            feature_vector[index] = term_counts.get(term, 0)
        feature_vectors.append({
            'article_processed_id': DBRef(articles_processed_collection_name, article['_id']),
            'feature_vector': feature_vector,
            'num_comments': article.get('num_comments', 0)
        })
    return feature_vectors


if __name__ == '__main__':
    articles = processed_collection.find()
    vocabulary = create_vocabulary(articles)
    create_feature_vectors(vocabulary, articles)
