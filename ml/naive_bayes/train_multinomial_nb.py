from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from sklearn.cross_validation import train_test_split
from sklearn.naive_bayes import MultinomialNB


def load_feature_vectors_and_classes(db_name):
    """
    :param db_name: name of database to use
    :return:
        - list of feature vectors
        - dictionary where the keys are the class labels and the values are dictionaries of the form
        {start: <integer>, end: <integer>}
    """
    db = Database(MongoClient(), db_name)
    collection_names = db.collection_names()
    if not ('naive_bayes' in collection_names and 'feature_vectors' in collection_names):
        print 'Database missing collections needed to train classifier on.'
        exit()

    classes = Collection(db, 'naive_bayes').find_one({'type': 'classes'})
    feature_vectors = [feature_vector for feature_vector in Collection(db, 'feature_vectors').find()]

    return feature_vectors, classes['classes']


def get_target_values(feature_vector_documents, classes):
    """
    :param feature_vector_documents: list of documents containing feature vectors and number of comments
    :param classes: dictionary containing a 'class label -> comment interval' mapping
    :return:
        - list of feature vectors
        - list of target values, with the i-th element corresponding to the target value of the i-th feature vector
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
    Trains a multinomial Naive Bayes classifier on the given feature vectors and target values.
    :return: trained MultinomialNB instance
    """
    if not isinstance(feature_vectors, list):
        raise TypeError("'feature_vectors' must be a list.")
    if not isinstance(target_values, list):
        raise TypeError("'target_values' must be a list.")

    # Split data into a training set (80%) and a test set (20%)
    feature_vectors_train, feature_vectors_test, target_values_train, target_values_test = train_test_split(
        feature_vectors, target_values, test_size=0.2)
    # Train classifier on training set
    classifier = MultinomialNB().fit(feature_vectors_train, target_values_train)
    # Evaluate classifier on test set
    print 'Classifier score on test set: ', classifier.score(feature_vectors_test, target_values_test)

    print 'Empirical log probability for each class:\n', classifier.class_log_prior_
    print 'Number of samples encountered for each class:\n', classifier.class_count_
    print 'Number of samples encountered for each (class, feature):\n', classifier.feature_count_

    return classifier


if __name__ == '__main__':
    parser = ArgumentParser(
        description="Trains a multinomial Naive Bayes classifier using feature vectors from a given database.\n",
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        'db_name',
        help='Name of database to use'
    )
    args = parser.parse_args()

    feature_vectors, classes = load_feature_vectors_and_classes(args.db_name)
    training_vectors, target_values = get_target_values(feature_vectors, classes)
    classifier = train_classifier(training_vectors, target_values)
