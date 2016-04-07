import lxml.html as html_parser
import urllib2

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'ml'
collection_name = 'links'


def get_links_for_year_range(start_year, end_year):
    """
    :param start_year:
    :param end_year:
    :return:
    """
    links = []
    for year in range(start_year, end_year + 1):
        links.extend(get_links_for_year(year))
    return links


def get_links_for_year(year):
    """
    :param year:
    :return:
    """
    links = []
    for month in range(1, 13):
        links.extend(get_links_for_month(year, month))
    return links


def get_links_for_month(year, month):
    """
    :param year:
    :param month:
    :return:
    """
    links = []
    url = 'http://www.cracked.com/funny-articles.html?date_year=%d&date_month=%d' % (year, month)
    document = html_parser.parse(urllib2.urlopen(url))

    # Article URLs are contained in <a> elements inside <div id="safePlace">
    url_elements = document.xpath('//div[@id="safePlace"]//a')
    for url in url_elements:
        values = url.values()
        if 'linkImage' in values:
            links.append({
                'url': url.attrib['href'],
                'year': year,
                'month': month
            })

    return links


def save_links(links):
    """
    :param links:
    :return:
    """
    db = Database(MongoClient(), db_name)
    collection = Collection(db, collection_name)
    collection.insert_many(links)


if __name__ == '__main__':
    links_dict = get_links_for_year_range(2005, 2015)
    save_links(links_dict)
