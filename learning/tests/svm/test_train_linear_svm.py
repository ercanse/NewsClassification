import numpy

from unittest import TestCase

from learning.svm.train_linear_svm import evaluate_classifier_using_repeated_cross_validation


class TestTrainLinearMultinomialNB(TestCase):
    def setUp(self):
        self.feature_vectors = numpy.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        self.target_values = numpy.array(['very_low', 'very_low', 'medium', 'medium'])

    def test_evaluate_classifier_using_repeated_cross_validation_returns_float(self):
        score = evaluate_classifier_using_repeated_cross_validation(self.feature_vectors, self.target_values, n_folds=2,
                                                                    iterations=1)
        self.assertIsInstance(score, float)
