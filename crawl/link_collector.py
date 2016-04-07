import lxml.html as html_parser
import urllib2

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db_name = 'ml'
collection_name = 'urls'


def get_urls_for_year_range(start_year, end_year):
    """
    Retrieves a list of URL details for all articles published between and including start_year and end_year.
    :param start_year: year from which to start collecting article URLs
    :param end_year: last year to collect article URLs for
    :return: list of dicts containing article URL details
    """
    print "Retrieving urls between years %d and %d...\n" % (start_year, end_year)
    urls = []
    for year in range(start_year, end_year + 1):
        urls.extend(get_urls_for_year(year))
    print "Retrieved %d urls between years %d and %d." % (len(urls), start_year, end_year)

    return urls


def get_urls_for_year(year):
    """
    Retrieves a list of URL details for all articles published in year.
    :param year: year for which to retrieve article URLs
    :return: list of dicts containing article URL details
    """
    print "Retrieving urls for year %d..." % year
    urls = []
    for month in range(1, 13):
        urls.extend(get_urls_for_month(year, month))
    print "Retrieved %d urls for year %d." % (len(urls), year)

    return urls


def get_urls_for_month(year, month):
    """
    Retrieves a list of URL details for all articles published in the given month of the given year.
    :param year: year for which to retrieve article URLs
    :param month: month for which to retrieve article URLs
    :return: list of dicts containing the URL and date and year of publication for each article
    """
    print "Retrieving urls for %d-%d..." % (month, year)
    urls = []
    url = 'http://www.cracked.com/funny-articles.html?date_year=%d&date_month=%d' % (year, month)
    document = html_parser.parse(urllib2.urlopen(url))

    # Article URLs are contained in <a> elements inside <div id="safePlace">
    url_elements = document.xpath('//div[@id="safePlace"]//a')
    for url in url_elements:
        values = url.values()
        if 'linkImage' in values:
            urls.append({
                'url': url.attrib['href'],
                'year': year,
                'month': month
            })
    print "Retrieved %d urls for %d-%d." % (len(urls), month, year)

    return urls


def save_urls(urls):
    """
    Inserts urls into the database.
    :param urls: dicts containing article URL details
    """
    db = Database(MongoClient(), db_name)
    collection = Collection(db, collection_name)
    collection.insert_many(urls)
    print "Inserted %d urls into '%s.%s'." % (len(urls), db_name, collection_name)


if __name__ == '__main__':
    # Retrieve urls and insert them into the database
    urls_dict = get_urls_for_year_range(2005, 2015)
    save_urls(urls_dict)
