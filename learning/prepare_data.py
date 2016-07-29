"""
Prepares the dataset containing feature vectors and class labels for use by classifiers.
1)
Two inputs are loaded using 'load_feature_vectors_and_classes':
- List of dictionaries of the form:
    [{feature_vector: [0, 3, 1, ...], num_comments: [10]},
     {feature_vector: [1, 0, 0, ...], num_comments: [20]]
- Dict of target classes of the form:
    {'very_low': {'start': 0, 'end': 10), 'low': {'start': 11, 'end': 20), 'medium': {'start': 21, 'end': 30),
    'high': {'start': 31, 'end': 40), 'very_high': {'start': 41, 'end': 50),}
2)
Based on these, it creates a list of feature vectors and target values using 'get_feature_vectors_and_target_values'.
With the examples given above, this would look like:
- [[0, 3, 1, ...], [1, 0, 0, ...]]
- ['very_low', 'low']
"""
import numpy

from numpy.linalg import norm
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


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
    if not len(feature_vector_dicts) == 0:
        raise TypeError("'feature_vector_dicts' is empty.")
    if not len(target_classes) == 0:
        raise TypeError("'target_classes' is empty.")

    num_vectors = len(feature_vector_dicts)
    vector_size = len(feature_vector_dicts[0]['feature_vector'])
    print 'Preparing %d feature vectors of size %d each...' % (num_vectors, vector_size)
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

    total_vector_length = 0
    term_frequencies = [0] * vector_size
    for feature_vector_document in feature_vector_dicts:
        feature_vector = feature_vector_document['feature_vector']
        # Add length of vector to total vector length
        total_vector_length += norm(feature_vector)
        # Keep track of the frequency of each term in dataset
        for index, frequency in enumerate(feature_vector):
            term_frequencies[index] += frequency

        feature_vectors.append(feature_vector)
        # Add the class label corresponding to 'feature_vector' to 'target_values'
        target_values.append(get_class_for_number_of_comments(feature_vector_document['num_comments']))

    # Apply document frequency thresholding (tp = (sqrt(1 + 8 * I1) - 1) / 2)

    for feature_vector in feature_vectors:
        # Normalize vector lengths
        avg_vector_length = total_vector_length / num_vectors

    target_values_arr = numpy.array(target_values)
    return numpy.array(feature_vectors), target_values_arr
