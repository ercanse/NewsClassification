import numpy

from unittest import TestCase

from ml.naive_bayes.train_multinomial_nb import get_feature_vectors_and_target_values
from ml.naive_bayes.train_multinomial_nb import evaluate_classifier_using_repeated_fixed_split
from ml.naive_bayes.train_multinomial_nb import evaluate_classifier_using_repeated_cross_validation


class TestTrainMultinomialNB(TestCase):
    def setUp(self):
        self.feature_vectors_dicts = [{'feature_vector': [0, 1], 'num_comments': 10},
                                      {'feature_vector': [1, 0], 'num_comments': 20}]
        self.target_classes = {'very_low': {'start': 0, 'end': 10}, 'low': {'start': 11, 'end': 20}}
        self.feature_vectors = numpy.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        self.target_values = numpy.array(['very_low', 'low', 'medium', 'high'])

    def test_get_feature_vectors_and_target_values_returns_ndarray_of_vectors(self):
        vectors, _ = get_feature_vectors_and_target_values(self.feature_vectors_dicts, self.target_classes)
        self.assertIsInstance(vectors, numpy.ndarray)

    def test_get_feature_vectors_and_target_values_returns_ndarray_of_values(self):
        _, values = get_feature_vectors_and_target_values(self.feature_vectors_dicts, self.target_classes)
        self.assertIsInstance(values, numpy.ndarray)

    def test_get_feature_vectors_and_target_values_returns_values_array_of_correct_shape(self):
        _, values = get_feature_vectors_and_target_values(self.feature_vectors_dicts, self.target_classes)
        self.assertTupleEqual((len(self.target_classes),), values.shape)

    def test_get_feature_vectors_and_target_values_returns_correct_values(self):
        _, values = get_feature_vectors_and_target_values(self.feature_vectors_dicts, self.target_classes)
        self.assertListEqual(['very_low', 'low'], values.tolist())

    def test_evaluate_classifier_using_repeated_fixed_split_returns_float(self):
        score = evaluate_classifier_using_repeated_fixed_split(self.feature_vectors, self.target_values, iterations=1)
        self.assertIsInstance(score, float)

    def test_evaluate_classifier_using_repeated_cross_validation_returns_float(self):
        score = evaluate_classifier_using_repeated_cross_validation(self.feature_vectors, self.target_values, n_folds=2,
                                                                    iterations=1)
        self.assertIsInstance(score, float)
