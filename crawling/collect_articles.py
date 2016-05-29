"""
Script to retrieve news articles from NU.nl, insert them into a MongoDB database,
and update them with the number of comments they have received.
"""

import lxml.html as html_parser
import urllib2
import re

from datetime import datetime, timedelta

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'nu'
collection_name = 'articles'
db = Database(MongoClient(), db_name)
collection = Collection(db, collection_name)

base_url = 'http://www.nu.nl'


def collect_articles():
    """ Retrieves articles that aren't yet in the database and saves them to the database.
    """
    retrieved_urls = get_retrieved_urls()
    front_page = get_front_page()
    articles = get_articles(front_page, retrieved_urls)
    save_articles(articles)


def get_retrieved_urls():
    """
    :return: list of URLs of all articles in the database
    """
    retrieved_articles = collection.find({}, {'news_url': 1})
    retrieved_urls = [article['news_url'] for article in retrieved_articles]
    print 'Found %d URLs already retrieved...\n' % len(retrieved_urls)
    return retrieved_urls


def get_front_page():
    """
    :return: page at URL 'base_url'
    """
    print "Checking for articles on %s..." % base_url
    return download_page(base_url)


def get_articles(page, retrieved_urls):
    """
    :param page: page containing URLs of news articles
    :param retrieved_urls: URLs of articles already in the database
    :return: Retrieves all articles on 'page', the URLs of which are not in 'retrieved_urls'.
    """
    num_links_processed = 0
    articles = []
    # Article URLs are contained in <a> elements inside <div class="column-content">
    url_elements = page.xpath('//div[@class="column-content"]//a')

    for url in url_elements:
        values = url.values()
        if len(values) == 2:
            url = values[0]
            # Check whether URL belongs to a news item
            if 'advertorial' not in url and re.match('/.+/\d+/.+', url):
                num_links_processed += 1
                article_url = '%s%s' % (base_url, url)
                # Skip if already processed
                if article_url not in retrieved_urls:
                    article = process_article('%s%s' % (base_url, url))
                    if article is not None:
                        articles.append(article)

    print "Retrieved %d new articles, skipped %d existing ones.\n" \
          % (len(articles), num_links_processed - len(articles))
    return articles


def process_article(url):
    """
    :param url: URL of article to process
    :return: dict containing article contents
    """
    print 'Retrieving article from %s...' % url
    # Retrieve article
    article = download_page(url)
    if article is None:
        return article
    # Extract contents
    article_contents = extract_article_contents(article)
    if article_contents is not None:
        article_contents['news_url'] = url
    return article_contents


def extract_article_contents(article):
    """
    :param article: article to extract contents of
    :return: dict containing article contents
    """
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
    # Skip article if the comments URL couldn't be extracted properly
    if not comments_url_is_valid(comments_url):
        print 'Could not find comments URL for article.'
        return None

    return dict(
        published=published_date,
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
    date = datetime.now() - timedelta(days=1)
    # Get articles older than 24 hours which haven't yet had their number of comments updated
    articles = collection.find({'published': {'$lt': date}, 'num_comments': None})
    print 'Updating number of comments for %d articles...' % articles.count()

    num_comments_updated = 0

    for article in articles:
        comments_url = article['comments_url']
        # Delete article if the comments URL is invalid
        if not comments_url_is_valid(comments_url):
            print 'Deleting article with invalid comments URL...'
            collection.delete_one({'_id': article['_id']})
        else:
            # Retrieve comments page
            print 'Retrieving comments from %s...' % comments_url
            comments_page = download_page(comments_url)
            if comments_page is None:
                continue
            # Search for element containing number of comments
            comments_element = comments_page.find('//span[@class="bericht-reacties"]')
            if comments_element is None:
                print 'Could not find comments, deleting article...'
                collection.delete_one({'_id': article['_id']})
                continue

            # Update article with the number of comments it has received
            comments_text = comments_element.text.strip()
            num_comments = int(comments_text.split(' ')[0])
            collection.update_one({'_id': article['_id']}, {'$set': {'num_comments': num_comments}})
            num_comments_updated += 1

    if num_comments_updated > 0:
        print 'Updated comments for %d articles.' % num_comments_updated


def comments_url_is_valid(comments_url):
    """
    :param comments_url: URL of page for commenting to validate
    :return: True only if comments_url belongs to a valid discussion page
    """
    return not(comments_url.startswith('http://www.nujij.nl/jij.lynkx/?u=http') or 'slideshow' in comments_url)


def download_page(url):
    """
    :param url: URL of page to retrieve
    :return: web page at URL url
    """
    page = None
    try:
        page = html_parser.parse(urllib2.urlopen(url))
    except urllib2.URLError:
        print 'Could not access page at URL %s.' % url
    return page


def save_articles(articles):
    """
    Inserts articles into the database.
    :param articles: list of articles
    """
    if isinstance(articles, list) and len(articles) > 0:
        collection.insert_many(articles)
        print "Inserted %d articles into '%s.%s'.\n" % (len(articles), db_name, collection_name)


if __name__ == '__main__':
    # Retrieve articles and insert them into the database
    collect_articles()
    # For articles that are old enough, update the number of comments they have received
    get_number_of_comments()
