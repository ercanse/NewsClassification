"""
Script to retrieve news articles from NU.nl and insert them into a MongoDB database.
"""

import lxml.html as html_parser
import urllib2

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'nu'
collection_name = 'articles'


def get_articles():
    """
    Retrieves all articles not yet in the database and inserts them into the database.
    """
    print "Retrieving articles..."
    urls = []
    url = 'http://www.nu.nl/'
    document = html_parser.parse(urllib2.urlopen(url))

    # Article URLs are contained in <a> elements inside <div id="safePlace">
    url_elements = document.xpath('//div[@id="safePlace"]//a')
    for url in url_elements:
        values = url.values()
        if 'linkImage' in values:
            urls.append({
                'url': url.attrib['href']
            })
    print "Retrieved %d articles." % (len(urls))

    return urls


def get_number_of_comments():
    """
    Retrieves the number of comments for each article published at least 24 hours ago.
    Updates the corresponding article document with the retrieved number of documents.
    """
    pass


def save_articles(urls):
    """
    Inserts articles into the database.
    :param articles: dicts containing articles details
    """
    db = Database(MongoClient(), db_name)
    collection = Collection(db, collection_name)
    collection.insert_many(urls)
    print "Inserted %d urls into '%s.%s'." % (len(urls), db_name, collection_name)


if __name__ == '__main__':
    # Retrieve articles and insert them into the database
    articles_dict = get_articles()
    save_articles(articles_dict)
