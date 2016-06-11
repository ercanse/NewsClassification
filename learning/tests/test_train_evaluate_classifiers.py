import numpy

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC, SVC
from unittest import TestCase

from learning.train_evaluate_classifiers import evaluate_classifier_using_repeated_cross_validation


class TestTrainEvaluateClassifiers(TestCase):
    def setUp(self):
        self.feature_vectors = numpy.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        self.target_values = numpy.array(['very_low', 'very_low', 'medium', 'medium'])

    def test_evaluate_multinomial_nb_using_repeated_cross_validation_returns_float(self):
        score = evaluate_classifier_using_repeated_cross_validation(
            MultinomialNB(), self.feature_vectors, self.target_values, n_folds=2, iterations=1)
        self.assertIsInstance(score, float)

    def test_evaluate_linear_svm_using_repeated_cross_validation_returns_float(self):
        score = evaluate_classifier_using_repeated_cross_validation(
            LinearSVC(), self.feature_vectors, self.target_values, n_folds=2, iterations=1)
        self.assertIsInstance(score, float)

    def test_unsupported_classifier_raises_error(self):
        self.assertRaises(TypeError, lambda l: evaluate_classifier_using_repeated_cross_validation(
            SVC(), self.feature_vectors, self.target_values, n_folds=2, iterations=1))
