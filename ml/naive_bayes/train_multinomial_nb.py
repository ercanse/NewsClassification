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

    target_classes = Collection(db, 'naive_bayes').find_one({'type': 'classes'})
    if 'classes' not in target_classes:
        raise KeyError("'target_classes' must contain a 'classes' key.")

    feature_vectors = list(Collection(db, 'feature_vectors').find())
    return feature_vectors, target_classes['classes']


def get_feature_vectors_and_target_values(feature_vector_dicts, target_classes):
    """
    :param feature_vector_dicts: list of dicts containing feature vectors and number of comments
    :param target_classes: dictionary containing a 'target class label -> comment interval' mapping
    :return:
        - NumPy ndarray containing feature vectors
        - NumPy ndarray containing target values, with the i-th element corresponding to
          the target value of the i-th feature vector
    """
    if not isinstance(feature_vector_dicts, list):
        raise TypeError("'feature_vector_dicts' must be a list.")
    if not isinstance(target_classes, dict):
        raise TypeError("'target_classes' must be a dict.")

    print 'Preparing %d feature vectors of size %d each...'\
          % (len(feature_vector_dicts), len(feature_vector_dicts[0]['feature_vector']))
    feature_vectors = []
    target_values = []

    def get_class_for_number_of_comments(num_comments):
        """
        :param num_comments: number of comments to determine class for
        :return: class within which the specified number of comments belongs to ('very low', 'high', etc.)
        """
        for class_name, comments_range in target_classes.iteritems():
            if comments_range['start'] <= num_comments <= comments_range['end']:
                return class_name

    for feature_vector_document in feature_vector_dicts:
        feature_vectors.append(feature_vector_document['feature_vector'])
        # Add the class label corresponding to 'feature_vector' to 'target_values'
        target_values.append(get_class_for_number_of_comments(feature_vector_document['num_comments']))

    target_values_arr = numpy.array(target_values)
    return numpy.array(feature_vectors), target_values_arr


def evaluate_classifier_using_repeated_fixed_split(feature_vectors, target_values, iterations=25):
    """
    Evaluates the multinomial Naive Bayes classifier using a fixed 80-20 training-test split of the dataset.
    Repeats this 'iterations' times and returns the average score.
    :param feature_vectors: feature vectors to use for evaluation
    :param target_values: labels representing values for each feature vector
    :param iterations: number of evaluations to run
    """
    check_vectors_and_values(feature_vectors, target_values)

    print '\nEvaluating classifier with %d runs using a fixed training-test split...' % iterations
    # Split data into a training set (80%) and a test set (20%)
    feature_vectors_train, feature_vectors_test, target_values_train, target_values_test = train_test_split(
        feature_vectors, target_values, test_size=0.2)
    # Evaluate classifier on test set
    scores = [
        MultinomialNB().fit(feature_vectors_train, target_values_train).score(feature_vectors_test, target_values_test)
        for _ in xrange(iterations)]

    score = sum(scores) / float(len(scores))
    print 'Mean score: %f' % score
    return score


def evaluate_classifier_using_repeated_cross_validation(feature_vectors, target_values, n_folds=10, iterations=25):
    """
    Evaluates the multinomial Naive Bayes classifier using n-fold stratified cross-validation.
    Repeats this 'iterations' times and returns the average score.
    :param feature_vectors: feature vectors to use for evaluation
    :param target_values: labels representing values for each feature vector
    :param n_folds: number of folds to use for cross-validation
    :param iterations: number of evaluations to run
    """
    check_vectors_and_values(feature_vectors, target_values)
    if not isinstance(n_folds, int):
        raise TypeError("'n_folds' must be an integer.")

    print '\nEvaluating classifier with %d runs of %d-fold stratified cross-validation...' % (iterations, n_folds)
    k_fold = StratifiedKFold(target_values, n_folds=n_folds, shuffle=True)
    scores = [cross_val_score(MultinomialNB(), feature_vectors, target_values, cv=k_fold).mean()
              for _ in xrange(iterations)]

    score = sum(scores) / float(len(scores))
    print 'Mean cross-validation score: %f' % score
    return score


def train_classifier(feature_vectors, target_values):
    """
    :param feature_vectors: feature vectors to train on
    :param target_values: labels representing values for each feature vector
    :return: MultinomialNB instance trained on the full dataset
    """
    return MultinomialNB().fit(feature_vectors, target_values)


def check_vectors_and_values(feature_vectors, target_values):
    """
    Checks whether feature_vectors and target_values are NumPy nd-arrays.
    :param feature_vectors: array of feature vectors
    :param target_values: array of target values
    """
    if not isinstance(feature_vectors, numpy.ndarray):
        raise TypeError("'feature_vectors' must be a NumPy ndarray.")
    if not isinstance(target_values, numpy.ndarray):
        raise TypeError("'target_values' must be a NumPy ndarray.")


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
    vectors, classes = load_feature_vectors_and_classes(args.db_name)
    vectors, values = get_feature_vectors_and_target_values(vectors, classes)
    # Evaluate classifier performance
    evaluate_classifier_using_repeated_fixed_split(vectors, values)
    evaluate_classifier_using_repeated_cross_validation(vectors, values)
    # Train classifier on whole dataset
    classifier = train_classifier(vectors, values)
