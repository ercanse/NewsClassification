import lxml.html as html_parser
import urllib2

def get_links_for_year(year):
    """
    """
    for month in range(1, 13):
        get_links_for_month(year, month)


def get_links_for_month(year, month):
    """
    """
    url = 'http://www.cracked.com/funny-articles.html?date_year=%d&date_month=%d' % (year, month)
    document = html_parser.parse(urllib2.urlopen(url))
    articles_container = document.xpath('//div[@id="safePlace"]')[0]
    for element in articles_container.getchildren():
        print(element.get('class'))

if __name__ == '__main__':
    get_links_for_month(2015, 1)
