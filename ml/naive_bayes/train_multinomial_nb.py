import numpy

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from sklearn.cross_validation import cross_val_score, StratifiedKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB


def load_feature_vectors_and_classes(db_name):
    """
    :param db_name: name of database to use
    :return:
        - list of feature vectors
        - dictionary where the keys are the class labels and the values are dictionaries of the form
        {start: <integer>, end: <integer>}
    """
    print 'Loading feature vectors and target classes...'
    db = Database(MongoClient(), db_name)
    collection_names = db.collection_names()
    if not ('naive_bayes' in collection_names and 'feature_vectors' in collection_names):
        print 'Database missing collections needed to train classifier on.'
        exit()

    classes = Collection(db, 'naive_bayes').find_one({'type': 'classes'})
    feature_vectors = [feature_vector for feature_vector in Collection(db, 'feature_vectors').find()]

    return feature_vectors, classes['classes']


def get_feature_vectors_and_target_values(feature_vector_documents, classes):
    """
    :param feature_vector_documents: list of documents containing feature vectors and number of comments
    :param classes: dictionary containing a 'class label -> comment interval' mapping
    :return:
        - list of feature vectors
        - list of target values, with the i-th element corresponding to the target value of the i-th feature vector
    """
    print 'Preparing %d feature vectors...' % len(feature_vector_documents)
    feature_vectors = []
    target_values = []

    def get_class_for_number_of_comments(num_comments):
        """
        :param num_comments: number of comments to determine class for
        :return: class within which the specified number of comments belongs to ('very low', 'high', etc.)
        """
        for class_name, comments_range in classes.iteritems():
            if comments_range['start'] <= num_comments <= comments_range['end']:
                return class_name

    for feature_vector_document in feature_vector_documents:
        feature_vectors.append(feature_vector_document['feature_vector'])
        target_values.append(get_class_for_number_of_comments(feature_vector_document['num_comments']))

    target_values_arr = numpy.array(target_values)
    target_values_arr.reshape(-1, 1)
    return numpy.array(feature_vectors), target_values_arr


def evaluate_classifier_using_fixed_split(feature_vectors, target_values):
    """
    Evaluates the multinomial Naive Bayes classifier using a fixed 80-20 training-test split of the dataset.
    :param feature_vectors: feature vectors to use for evaluation
    :param target_values: labels representing values for each feature vector
    """
    if not isinstance(feature_vectors, numpy.ndarray):
        raise TypeError("'feature_vectors' must be a NumPy ndarray.")
    if not isinstance(target_values, numpy.ndarray):
        raise TypeError("'target_values' must be a NumPy ndarray.")

    print '\nEvaluating classifier using a fixed training-test split...'
    # Split data into a training set (80%) and a test set (20%)
    feature_vectors_train, feature_vectors_test, target_values_train, target_values_test = train_test_split(
        feature_vectors, target_values, test_size=0.2)
    # Train classifier on training set
    classifier = MultinomialNB().fit(feature_vectors_train, target_values_train)
    # Evaluate classifier on test set
    print 'Classifier score: ', classifier.score(feature_vectors_test, target_values_test)


def evaluate_classifier_using_cross_validation(feature_vectors, target_values):
    """
    Evaluates the multinomial Naive Bayes classifier using 10-fold stratified cross-validation.
    :param feature_vectors: feature vectors to use for evaluation
    :param target_values: labels representing values for each feature vector
    """
    print '\nEvaluating classifier using 10-fold stratified cross-validation...'
    k_fold = StratifiedKFold(target_values, n_folds=10, shuffle=True)
    score = cross_val_score(MultinomialNB(), feature_vectors, target_values, cv=k_fold)
    print 'Classifier score on 10 runs:\n', score
    print 'Mean classifier score during cross-validation:', score.mean()


def train_classifier(feature_vectors, target_values):
    """
    :param feature_vectors: feature vectors to train on
    :param target_values: labels representing values for each feature vector
    :return: MultinomialNB instance trained on the full dataset
    """
    return MultinomialNB().fit(feature_vectors, target_values)


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

    # Prepare data for learning
    feature_vectors, classes = load_feature_vectors_and_classes(args.db_name)
    training_vectors, target_values = get_feature_vectors_and_target_values(feature_vectors, classes)
    # Evaluate classifier performance
    evaluate_classifier_using_fixed_split(training_vectors, target_values)
    evaluate_classifier_using_cross_validation(training_vectors, target_values)
    # Train classifier on whole dataset
    classifier = train_classifier(training_vectors, target_values)
