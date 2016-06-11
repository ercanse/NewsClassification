import numpy

from unittest import TestCase

from learning.prepare_data import get_feature_vectors_and_target_values


class TestPrepareData(TestCase):
    def setUp(self):
        self.feature_vectors_dicts = [{'feature_vector': [0, 1], 'num_comments': 10},
                                      {'feature_vector': [1, 0], 'num_comments': 20}]
        self.target_classes = {'very_low': {'start': 0, 'end': 10}, 'low': {'start': 11, 'end': 20}}

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
