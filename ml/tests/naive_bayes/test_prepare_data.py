from bson import ObjectId
from unittest import TestCase

from ml.naive_bayes.prepare_data import create_vocabulary, create_feature_vectors


class TestPrepareData(TestCase):
    def setUp(self):
        self.articles = [
            {'_id': ObjectId(), 'title': 'a news article', 'text': 'very interesting content'},
            {'_id': ObjectId(), 'title': 'viral piece of news', 'text': 'jaw-dropping developments'}
        ]

    def test_create_vocabulary_returns_list(self):
        self.assertTrue(isinstance(create_vocabulary(self.articles), list))

    def test_create_vocabulary_includes_all_unique_terms(self):
        vocabulary = create_vocabulary(self.articles)
        self.assertListEqual(
            vocabulary, [
                'a', 'article', 'content', 'developments', 'interesting', 'jaw-dropping', 'news', 'of', 'piece', 'very',
                'viral'
            ]
        )

    def test_create_feature_vector_counts_term_occurrences_correctly(self):
        vocabulary = [
            'a', 'article', 'content', 'developments', 'interesting', 'jaw-dropping', 'news', 'of', 'piece', 'very',
            'viral'
        ]
        feature_vectors = create_feature_vectors(
            vocabulary,
            [{'_id': ObjectId(), 'title': 'article news', 'text': 'article very interesting'}]
        )
        self.assertEqual([0, 2, 0, 0, 1, 0, 1, 0, 0, 1, 0], feature_vectors[0].get('feature_vector', []))
