"""
Script to load article URLs from the database, retrieve the articles, and extract and store their details
(author, title, introductory paragraph, number of views, number of comments).
"""

import lxml.html as html_parser
import pymongo
import urllib2

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'ml'
collection_name = 'urls'


def load_urls():
    """
    :return: all URL documents in collection db_db_name.collection_name.
    """
    db = Database(MongoClient(), db_name)
    collection = Collection(db, collection_name)
    return collection.find().sort([('year', pymongo.ASCENDING), ('month', pymongo.ASCENDING)])


def process_urls(urls):
    """
    :param urls: article URLs to process
    :return: list of article retrieved from URLs
    """
    for url in urls:
        retrieve_article(url)


def retrieve_article(url):
    """
    :param url: URL of article to retrieve
    :return: retrieved article
    """
    print(url['url'])
    article = html_parser.parse(urllib2.urlopen(url['url']))
    process_article(article)


def process_article(article):
    """
    Parses article and stores its details in the database.
    :param article: article to process
    """
    title = article.xpath('//section[@class="body"]//h1')[0].text
    author = article.xpath('//a[@class="byline"]')[0].text

    num_views = article.xpath('//span[@id="viewCounts"]')[0].text
    num_views = num_views.split(' ')[0].replace(',', '')

    num_comments = article.xpath('//section[@class="header subheader"]//span[@id="commentCounts"]')[0].text

    print title, author, num_views, num_comments, '\n'


if __name__ == '__main__':
    urls = load_urls()
    process_urls(urls[:5])
