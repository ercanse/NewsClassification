"""
Script to retrieve news articles from NU.nl and insert them into a MongoDB database.
"""

import lxml.html as html_parser
import urllib2
import re

from datetime import datetime

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'nu'
collection_name = 'articles'
base_url = 'http://www.nu.nl'


def get_articles():
    """
    Retrieves all articles not yet in the database and inserts them into the database.
    """
    print "Retrieving articles..."
    articles = []
    front_page = html_parser.parse(urllib2.urlopen(base_url))

    # Article URLs are contained in <a> elements inside <div class="column-content">
    url_elements = front_page.xpath('//div[@class="column-content"]//a')
    for url in url_elements:
        values = url.values()
        if len(values) == 2:
            url = values[0]
            if 'advertorial' not in url and re.match('/.+/\d+/.+', url):
                article = get_article_contents('%s%s' % (base_url, url))
                articles.append(article)
    print "Retrieved %d articles." % (len(articles))

    return articles


def get_article_contents(url):
    """
    :param url:
    :return:
    """
    print 'Retrieving article from %s...' % url

    # Retrieve article
    article = html_parser.parse(urllib2.urlopen(url))
    # Extract publication date
    published = article.xpath('//span[@class="published"]//span[@class="small"]')[0].text.strip()
    published_date = datetime.strptime(published, '%d-%m-%y %H:%M')
    # Extract title
    title = article.xpath('//div[@class="title"]//h1[@class="fluid"]')[0].text.strip()
    # Extract article text by combining the excerpt and the body
    text = ""
    text += article.xpath('//div[@class="item-excerpt"]')[0].text.strip()
    text_elements = article.xpath('//div[@class="zone"]//div[@class="block-content"]//p')
    for text_element in text_elements:
        element_text = text_element.text
        if element_text:
            text += element_text.strip()
    # Extract the NUjij link used for commenting
    comments_url = article.xpath(
        '//ul[@class="social-buttons"]//li[@class="nujij"]//a[@class="tracksocial"]'
    )[0].attrib['href']

    return dict(
        published=published_date,
        news_url=url,
        comments_url=comments_url,
        title=title,
        text=text,
        num_comments=None
    )


def get_number_of_comments():
    """
    Retrieves the number of comments for each article published at least 24 hours ago.
    Updates the corresponding article document with the retrieved number of documents.
    """
    pass


def save_articles(articles):
    """
    Inserts articles into the database.
    :param articles: dict containing articles
    """
    db = Database(MongoClient(), db_name)
    collection = Collection(db, collection_name)
    collection.insert_many(articles)
    print "Inserted %d articles into '%s.%s'." % (len(articles), db_name, collection_name)


if __name__ == '__main__':
    articles_dict = get_articles()
    save_articles(articles_dict)
