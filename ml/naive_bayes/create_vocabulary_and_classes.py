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
    return set(sorted(vocabulary))


def create_classes(articles):
    """
    Divides the number of comments found in articles across five target classes.
    :param articles:
    :return:
    """
    comment_amounts = []


if __name__ == '__main__':
    processed_articles = processed_collection.find()
    create_vocabulary(processed_articles)
    create_classes(processed_articles)
