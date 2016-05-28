"""
Script to retrieve news articles from NU.nl and insert them into a MongoDB database.
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


def get_articles():
    """
    Retrieves all articles not yet in the database and inserts them into the database.
    """
    print "Retrieving articles..."
    # Determine URLs already processed
    retrieved_articles = collection.find({}, {'news_url': 1})
    retrieved_urls = [article['news_url'] for article in retrieved_articles]

    num_links_processed = 0
    articles = []
    front_page = html_parser.parse(urllib2.urlopen(base_url))

    # Article URLs are contained in <a> elements inside <div class="column-content">
    url_elements = front_page.xpath('//div[@class="column-content"]//a')
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
                    article = get_article_contents('%s%s' % (base_url, url))
                    if article is not None:
                        articles.append(article)
    print "Retrieved %d new articles, skipped %d existing ones." \
          % (len(articles), num_links_processed - len(articles))

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
    # Skip article if the comments URL couldn't be extracted properly
    if comments_url.startswith('http://www.nujij.nl/jij.lynkx/?u=http') and 'slideshow' in comments_url:
        return None

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
    date = datetime.now() - timedelta(days=1)
    articles = collection.find({'published': {'$lt': date}, 'num_comments': None})
    print 'Retrieving number of comments for %d articles...' % articles.count()

    for article in articles:
        comments_url = article['comments_url']
        # Delete article if the comments URL
        if comments_url.startswith('http://www.nujij.nl/jij.lynkx/?u=http') and 'slideshow' in comments_url:
            collection.delete_one({'_id': article['_id']})
        else:
            # Retrieve comments page
            comments_page = html_parser.parse(urllib2.urlopen(comments_url))
            comments_text = comments_page.find('//span[@class="bericht-reacties"]').text.strip()
            # Update article with the number of comments it has received
            num_comments = int(comments_text.split(' ')[0])
            collection.update_one({'_id': article['_id']}, {'$set': {'num_comments': num_comments}})


def save_articles(articles):
    """
    Inserts articles into the database.
    :param articles: list of articles
    """
    if isinstance(articles, list) and len(articles) > 0:
        collection.insert_many(articles)
        print "Inserted %d articles into '%s.%s'." % (len(articles), db_name, collection_name)


def run():
    """
    Retrieves articles and saves them to the database.
    """
    articles = get_articles()
    save_articles(articles)
    get_number_of_comments()


if __name__ == '__main__':
    run()
