"""
Prepares the collected news articles for use by a Naive Bayes classifier.
First creates a vocabulary, which is the set of all words occurring in all articles.
It then expresses each news article as a term vector, where the i-th entry indicates
how many times word i from the vocabulary occurs in the article.
"""
from bson import DBRef
from collections import Counter
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'nu'
articles_processed_collection_name = 'articles_processed'

db = Database(MongoClient(), db_name)
processed_collection = Collection(db, articles_processed_collection_name)
naive_bayes_collection = Collection(db, 'naive_bayes')
feature_vectors_collection = Collection(db, 'feature_vectors')


def create_vocabulary(articles):
    """
    Creates a set of all words occurring in all articles.
    """
    print('Creating vocabulary from %d articles...' % len(articles))
    vocabulary = []
    for article in articles:
        vocabulary.extend(article.get('title', '').split(' '))
        vocabulary.extend(article.get('text', '').split(' '))
    vocabulary = sorted(list(set(vocabulary)))
    print('Created vocabulary consisting of %d terms.' % len(vocabulary))
    return vocabulary


def create_feature_vectors(vocabulary, articles):
    """
    Creates a vector v of size 'len(vocabulary)' for each article.
    The value of the i-th element in v is the frequency with which the i-th term in vocabulary occurs in the article.
    """
    print('Creating feature vectors for %d articles...' % len(articles))
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
    print('Created %d feature vectors.' % len(feature_vectors))
    return feature_vectors


if __name__ == '__main__':
    articles = [article for article in processed_collection.find()]
    # Create and save vocabulary
    vocabulary = create_vocabulary(articles)
    print('Inserting vocabulary into database...')
    naive_bayes_collection.insert_one({'type': 'vocabulary', 'vocabulary': vocabulary})
    # Create and save feature vectors
    feature_vectors = create_feature_vectors(vocabulary, articles)
    print('Inserting feature vectors into database...')
    feature_vectors_collection.insert_many(feature_vectors)
