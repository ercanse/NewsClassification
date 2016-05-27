"""
Script to load article URLs from the database, retrieve the articles, and extract and store their details
(author, title, introductory paragraph, number of views, number of comments).
"""

import lxml.html as html_parser
import traceback
import urllib2

from bson.dbref import DBRef
from optparse import OptionParser
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'ml'
urls_collection_name = 'urls'
failed_urls_collection_name = 'urls_failed'
articles_collection_name = 'articles_raw'

db = Database(MongoClient(), db_name)
urls_collection = Collection(db, urls_collection_name)
articles_collection = Collection(db, articles_collection_name)
failed_urls_collection = Collection(db, failed_urls_collection_name)


def load_urls(only_failed=False):
    """
    :param only_failed: if True, only process URLs from 'failed_urls_collection'
    :return: list of dicts with URLs
    """
    urls = []

    if not only_failed:
        for url_to_process in urls_collection.find():
            urls.append(url_to_process)
    for url_failed in failed_urls_collection.find():
        url_failed['failed'] = True
        urls.append(url_failed)
    return urls


def process_urls(urls):
    """
    Retrieves articles indicated by the URLs in urls and extracts information from them.
    :param urls: list of dicts of article URLs to process
    :return:
        list of articles retrieved from URLs and list of URLs that couldn't be retrieved or processed properly
    """
    failed_urls = []
    articles = []
    num_articles = len(urls)
    count = 1

    for url in urls:
        if 'photoplasty' in url['url']:
            print 'Skipping photoplasty...'
            count += 1
            continue
        try:
            print 'Retrieving article %d of %d at URL \'%s\'...' % (count, num_articles, url['url'])
            article_details = retrieve_article_page(url)
        except (urllib2.HTTPError, IndexError, UnicodeDecodeError) as e:
            if isinstance(e, urllib2.HTTPError):
                print e
                print traceback.print_exc()
                print 'Couldn\'t retrieve article at URL \'%s\'.' % url['url']
            else:
                print e
                print traceback.print_exc()
                print 'Couldn\'t process article at URL \'%s\'.' % url['url']
            if 'failed' not in url:
                failed_urls.append(url)
                failed_urls_collection.insert_one(url)
        else:
            articles.append(article_details)
            articles_collection.insert_one(article_details)
            # Remove entry from collection of failed urls
            if 'failed' in url:
                failed_urls_collection.delete_one({'_id': url['_id']})
        count += 1
    return articles, failed_urls


def download_article_page(url):
    """
    :return:
    """
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0')
    return html_parser.parse(urllib2.urlopen(request))


def retrieve_article_page(url):
    """
    Retrieves the article at URL url and calls the data extraction function.
    :param url: URL of article to retrieve
    :return: retrieved article
    """
    article = download_article_page(url['url'])
    article_details = process_article(url, article)
    return article_details


def retrieve_subsequent_article_page(url):
    """
    Retrieves the second or later page of the article at URL url.
    :param url: URL of article to retrieve
    :return: retrieved article
    """
    article = download_article_page(url)
    headings, text = process_article_text(article)
    return headings, text


def process_article(url, article):
    """
    Parses article and stores its details in the database.
    :param url: article URL
    :param article: article to process
    :return: dict with data extracted from article
    """
    title = article.xpath('//section[@class="body"]//h1')[0].text
    author = article.xpath('//a[@class="byline"]')[0].text

    num_views = article.xpath('//span[@id="viewCounts"]')[0].text
    num_views = num_views.split(' ')[0].replace(',', '')

    num_comments = article.xpath('//section[@class="header subheader"]//span[@id="commentCounts"]')[0].text

    headings, text = process_article_text(article)

    # Check whether article has multiple pages
    pagination_elements = article.xpath('//span[@class="paginationNumber"]')
    if pagination_elements:
        # Get total number of pages
        pages = int(pagination_elements[1].text)
        # Retrieve headings and text on subsequent pages
        for page_number in range(2, pages + 1):
            if 'html' in url['url']:
                next_page_url = url['url'].replace('.html', '') + '_p%d.html' % page_number
            else:
                next_page_url = url['url'] + '%d' % page_number

            headings_next, text_next = retrieve_subsequent_article_page(next_page_url)
            headings.extend(headings_next)
            text.extend(text_next)

    return {
        'url': DBRef(urls_collection_name, url['_id']),
        'author': author,
        'title': title,
        'headings': headings,
        'text': text,
        'num_views': num_views,
        'num_comments': num_comments
    }


def process_article_text(article):
    """
    :param article: article to extract text from
    :return: tuple containing a list of headings and a list of text elements found in article
    """
    headings = []
    heading_elements = article.xpath('//section[@class="body"]//section//h2')
    for sub_heading in heading_elements:
        try:
            headings.append(sub_heading.text)
        except UnicodeDecodeError:
            print 'Skipping heading...'

    text = []
    paragraphs = article.xpath('//section[@class="body"]//section//p')
    for text_element in paragraphs:
        try:
            text.append(text_element.text)
        except UnicodeDecodeError:
            print 'Skipping paragraph...'

    return headings, text


if __name__ == '__main__':
    # Create 'only_failed' option
    parser = OptionParser()
    parser.add_option(
        "--only_failed", action="store_true", dest="only_failed", default=False, help="Process only failed urls."
    )
    (options, args) = parser.parse_args()

    # Load URLs and retrieve and process the articles at those URLs
    urls_list = load_urls(only_failed=options.only_failed)
    articles_list, failed_urls_list = process_urls(urls_list)
