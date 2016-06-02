from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from sklearn.naive_bayes import MultinomialNB


def train_classifier():
    """
    """
    db = Database(MongoClient(), db_name)
    naive_bayes_collection = Collection(db, 'naive_bayes')
    feature_vectors_collection = Collection(db, 'feature_vectors')

    classes = naive_bayes_collection.find_one({'type': 'classes'})
    feature_vectors = feature_vectors_collection.find()


if __name__ == '__main__':
    parser = ArgumentParser(
        description="Trains a multinomial Naive Bayes classifier using feature vectors from the specified database.\n",
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        'db_name',
        help='Name of database to use'
    )
    args = parser.parse_args()
    db_name = args.db_name
    # Load list F of feature vectors
    # Load target classes C
    # Create list of length l, where the l[i] = C[F[i][num_comments]]
    pass
