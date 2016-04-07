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
        retrieve_main_article_page(url['url'])


def retrieve_main_article_page(url):
    """
    :param url: URL of article to retrieve
    :return: retrieved article
    """
    print(url)
    article = html_parser.parse(urllib2.urlopen(url))
    process_article(url, article)


def retrieve_subsequent_article_page(url):
    """
    :param url: URL of article to retrieve
    :return: retrieved article
    """
    print(url)
    article = html_parser.parse(urllib2.urlopen(url))
    headings, text = process_article_text(article)
    return headings, text


def process_article(url, article):
    """
    Parses article and stores its details in the database.
    :param url: article URL
    :param article: article to process
    """
    title = article.xpath('//section[@class="body"]//h1')[0].text
    author = article.xpath('//a[@class="byline"]')[0].text

    num_views = article.xpath('//span[@id="viewCounts"]')[0].text
    num_views = num_views.split(' ')[0].replace(',', '')

    num_comments = article.xpath('//section[@class="header subheader"]//span[@id="commentCounts"]')[0].text

    headings, text = process_article_text(article)

    pagination_elements = article.xpath('//span[@class="paginationNumber"]')
    if pagination_elements:
        pages = int(pagination_elements[1].text)
        for page_number in range(2, pages + 1):
            next_page_url = url.replace('.html', '') + '_p%d.html' % page_number
            headings_next, text_next = retrieve_subsequent_article_page(next_page_url)
            headings.extend(headings_next)
            text.extend(text_next)

    return author, title, headings, text, num_views, num_comments


def process_article_text(article):
    headings = []
    heading_elements = article.xpath('//section[@class="body"]//section//h2')
    for sub_heading in heading_elements:
        headings.append(sub_heading.text)

    text = []
    paragraphs = article.xpath('//section[@class="body"]//section//p')
    for text_element in paragraphs:
        text.append(text_element.text)

    return headings, text

if __name__ == '__main__':
    urls = load_urls()
    process_urls(urls[500:501])
