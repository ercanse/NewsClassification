from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from sklearn.naive_bayes import MultinomialNB


def load_feature_vectors_and_classes(db_name):
    """
    :return:
    """
    db = Database(MongoClient(), db_name)
    collection_names = db.collection_names()
    if not ('naive_bayes' in collection_names and 'feature_vectors' in collection_names):
        print 'Database missing collections needed to train classifier on.'
        exit()

    classes = Collection(db, 'naive_bayes').find_one({'type': 'classes'})
    feature_vector_documents = Collection(db, 'feature_vectors').find()

    return feature_vector_documents, classes['classes']


def get_training_vectors_and_target_values(feature_vector_documents, classes):
    """
    """
    feature_vectors = []
    target_values = []

    def get_class_for_number_of_comments(num_comments):
        """
        :param num_comments:
        :return:
        """
        for class_name, comments_range in classes.iteritems():
            if comments_range['start'] <= num_comments <= comments_range['end']:
                return class_name

    for feature_vector_document in feature_vector_documents:
        feature_vectors.append(feature_vector_document['feature_vector'])
        target_values.append(get_class_for_number_of_comments(feature_vector_document['num_comments']))

    return feature_vectors, target_values


def train_classifier(feature_vectors, target_values):
    """
    :return:
    """
    if not isinstance(feature_vectors, list):
        raise TypeError("'feature_vectors' must be a list.")
    if not isinstance(target_values, list):
        raise TypeError("'target_values' must be a list.")
    classifier = MultinomialNB()
    classifier.fit(feature_vectors, target_values)
    print classifier


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

    feature_vectors, classes = load_feature_vectors_and_classes(args.db_name)
    training_vectors, target_values = get_training_vectors_and_target_values(feature_vectors, classes)
    train_classifier(training_vectors, target_values)
