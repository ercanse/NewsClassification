from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'nu'
articles_collection_name = 'articles_processed'
naive_bayes_collection_name = 'naive_bayes'

db = Database(MongoClient(), db_name)
processed_collection = Collection(db, articles_collection_name)
naive_bayes_collection = Collection(db, naive_bayes_collection_name)


def create_vocabulary_and_classes(articles):
    """
    Creates a set of all words occurring in all articles.
    Divides the number of comments found in articles across five target classes.
    Saves both results to the database.
    """
    vocabulary = []
    comment_amounts = []
    for article in articles:
        # Add words to vocabulary
        # Add number of comments to comment_amounts
        pass


if __name__ == '__main__':
    processed_articles = processed_collection.find()
    create_vocabulary_and_classes(processed_articles)
