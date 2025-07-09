import scrapy
from urllib.parse import urljoin, urlparse
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError
import tldextract
from goi_scraper.items import LinkItem


class GoiSpider(scrapy.Spider):
    name = "goi_spider"
    allowed_domains = ['gov.in', 'nic.in']
    start_urls = ['https://igod.gov.in/sectors']

    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [404],
        'LOG_LEVEL': 'INFO'
    }
    visited_links = set()

    def parse(self, response):
        self.log(f"Visited: {response.url}")

        # Check HTTPS
        parsed_url = urlparse(response.url)
        if parsed_url.scheme != 'https' and self.is_gov_site(parsed_url.netloc):
            https_issue = LinkItem(url=response.url, type='non_https')
            yield https_issue            

        # Crawling though each link present in the website
        for href in response.css('a::attr(href)').getall():
            link = urljoin(response.url, href)
            if self.should_visit(link):
                yield scrapy.Request(
                    link,
                    callback=self.parse,
                    errback=self.handle_error,
                    dont_filter=True
                )
    def is_gov_site(self, domain):
        ext = tldextract.extract(domain)
        return ext.suffix == 'gov.in' or ext.suffix =='nic.in'
    
    def should_visit(self, link):
        if link in self.visited_links:
            return False
        parsed = urlparse(link)
        domain = parsed.netloc
        if self.is_gov_in(domain):
            self.visited_links.add(link)
            return True
        return False

    def handle_error(self, failure):
        request = failure.request
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                yield LinkItem(url=response.url, type='rotten')
        elif failure.check(DNSLookupError, TimeoutError):
            yield LinkItem(url=request.url, type='rotten')