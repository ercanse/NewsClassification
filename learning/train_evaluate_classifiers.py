"""
Trains a multinomial Naive Bayes classifier and a linear SVM.
Evaluates the trained classifiers using cross-validation.
"""
import numpy

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from learning.prepare_data import load_feature_vectors_and_classes, get_feature_vectors_and_target_values


def evaluate_classifier_using_repeated_cross_validation(classifier, feature_vectors, target_values, n_folds=10,
                                                        iterations=10):
    """
    Evaluates the given classifier using n-fold stratified cross-validation.
    Repeats this 'iterations' times and returns the average score.
    :param classifier: classifier to evaluate
    :param feature_vectors: feature vectors to use for evaluation
    :param target_values: labels representing values for each feature vector
    :param n_folds: number of folds to use for cross-validation
    :param iterations: number of evaluations to run
    :return: mean cross-validation score of all runs
    """
    if not (isinstance(classifier, MultinomialNB) or isinstance(classifier, LinearSVC)):
        raise TypeError("'classifier' must be MultinomialNB or LinearSVC.")
    check_vectors_and_values(feature_vectors, target_values)
    if not isinstance(n_folds, int):
        raise TypeError("'n_folds' must be an integer.")

    print('\nEvaluating %s classifier with %d runs of %d-fold stratified cross-validation...' % \
          (classifier, iterations, n_folds))
    scores = []
    for _ in range(iterations):
        k_fold = StratifiedKFold(target_values, n_folds=n_folds, shuffle=True)
        scores.append(cross_val_score(classifier, feature_vectors, target_values, cv=k_fold).mean())

    score = sum(scores) / float(len(scores))
    print('Mean cross-validation score: %f' % score)
    return score


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
        description="Trains a multinomial Naive Bayes classifier and a linear SVM "
                    "using feature vectors and target values from a given database.\n",
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
    # Evaluate performance of multinomial NB and linear SVM
    evaluate_classifier_using_repeated_cross_validation(MultinomialNB(), vectors, values)
    evaluate_classifier_using_repeated_cross_validation(LinearSVC(), vectors, values)
