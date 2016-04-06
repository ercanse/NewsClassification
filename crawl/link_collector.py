import lxml.html as html_parser
import urllib2


def get_links_for_year(year):
    """
    """
    links = []
    for month in range(1, 13):
        links.extend(get_links_for_month(year, month))
    return links


def get_links_for_month(year, month):
    """
    """
    links = []
    url = 'http://www.cracked.com/funny-articles.html?date_year=%d&date_month=%d' % (year, month)
    document = html_parser.parse(urllib2.urlopen(url))

    urls = document.xpath('//div[@id="safePlace"]//a')
    for url in urls:
        values = url.values()
        if 'linkImage' in values:
            links.append(url.values()[1])

    print(links)
    return links

if __name__ == '__main__':
    get_links_for_month(2015, 1)
