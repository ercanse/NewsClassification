"""
Trains a multinomial Naive Bayes classifier on the feature vectors and target values loaded from the database.
Evaluates the trained classifier using cross-validation.
"""
import numpy

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from sklearn.cross_validation import cross_val_score, StratifiedKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB

from learning.prepare_data import load_feature_vectors_and_classes, get_feature_vectors_and_target_values


def evaluate_classifier_using_fixed_split(feature_vectors, target_values):
    """
    Evaluates the multinomial Naive Bayes classifier using a fixed 80-20 training-test split of the dataset.
    :param feature_vectors: feature vectors to use for evaluation
    :param target_values: labels representing values for each feature vector
    """
    check_vectors_and_values(feature_vectors, target_values)

    print '\nEvaluating classifier using a fixed training-test split...'
    # Split data into a training set (80%) and a test set (20%)
    feature_vectors_train, feature_vectors_test, target_values_train, target_values_test = train_test_split(
        feature_vectors, target_values, test_size=0.2)
    # Evaluate classifier on test set
    mnb = MultinomialNB().fit(feature_vectors_train, target_values_train)
    score = mnb.score(feature_vectors_test, target_values_test)
    print 'Mean score: %f' % score
    return score


def evaluate_classifier_using_repeated_cross_validation(feature_vectors, target_values, n_folds=10, iterations=10):
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
    scores = []
    for _ in xrange(iterations):
        k_fold = StratifiedKFold(target_values, n_folds=n_folds, shuffle=True)
        scores.append(cross_val_score(MultinomialNB(), feature_vectors, target_values, cv=k_fold).mean())

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
    evaluate_classifier_using_fixed_split(vectors, values)
    evaluate_classifier_using_repeated_cross_validation(vectors, values)
    # Train classifier on whole dataset
    classifier = train_classifier(vectors, values)
