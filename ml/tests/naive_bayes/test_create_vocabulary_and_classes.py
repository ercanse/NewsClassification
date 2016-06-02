from unittest import TestCase

from ml.naive_bayes.create_vocabulary_and_classes import create_vocabulary


class TestCreateVocabularyAndClasses(TestCase):

    def setUp(self):
        self.articles = [
            {'title': 'a news article', 'text': 'very interesting content'},
            {'title': 'viral piece of news', 'text': 'jaw-dropping developments'}
        ]

    def test_create_vocabulary(self):
        vocabulary = create_vocabulary(self.articles)
        self.assertSetEqual(
            vocabulary, {
                'a', 'news', 'article', 'very', 'interesting', 'content',
                'viral', 'piece', 'of', 'jaw-dropping', 'developments'
            }
        )
