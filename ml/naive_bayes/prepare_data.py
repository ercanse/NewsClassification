from collections import Counter
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'nu'
articles_collection_name = 'articles_processed'
naive_bayes_collection_name = 'naive_bayes'

db = Database(MongoClient(), db_name)
processed_collection = Collection(db, articles_collection_name)
naive_bayes_collection = Collection(db, naive_bayes_collection_name)


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
        text = article.get('title').split(' ') + article.get('text').split(' ')
        term_counts = Counter(text)
        feature_vector = [0] * len(vocabulary)
        for term, count in term_counts.iteritems():
            feature_vector[vocabulary.index(term)] = count
        feature_vectors.append(feature_vector)
    return feature_vectors


if __name__ == '__main__':
    articles = processed_collection.find()
    vocabulary = create_vocabulary(articles)
    create_feature_vectors(vocabulary, articles)
