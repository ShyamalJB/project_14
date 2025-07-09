import scrapy
from urllib.parse import urljoin, urlparse
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError
import tldextract


class GoiSpider(scrapy.Spider):
    name = "goi_spider"
    allowed_domains = ['gov.in']
    start_urls = [
        'https://india.gov.in',
        'https://meity.gov.in',
        'https://mha.gov.in',
        'https://pmindia.gov.in',
    ]

    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [404],
        'LOG_LEVEL': 'INFO'
    }

    visited_links = set()
    rotten_links = set()
    non_https_sites = set()

    def parse(self, response):
        self.log(f"Visited: {response.url}")

        # Check HTTPS
        parsed_url = urlparse(response.url)
        if parsed_url.scheme != 'https' and self.is_gov_in(parsed_url.netloc):
            self.non_https_sites.add(f"{parsed_url}")

        for href in response.css('a::attr(href)').getall():
            link = urljoin(response.url, href)
            if self.should_visit(link):
                yield scrapy.Request(
                    link,
                    callback=self.parse,
                    errback=self.handle_error,
                    dont_filter=True
                )

    def should_visit(self, link):
        if link in self.visited_links:
            return False
        parsed = urlparse(link)
        domain = parsed.netloc
        if self.is_gov_in(domain):
            self.visited_links.add(link)
            return True
        return False

    def is_gov_in(self, domain):
        ext = tldextract.extract(domain)
        return ext.suffix == 'gov.in'

    def handle_error(self, failure):
        request = failure.request
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                self.rotten_links.add(response.url)
                self.log(f"Broken link: {response.url}")
        elif failure.check(DNSLookupError, TimeoutError):
            self.rotten_links.add(request.url)
            self.log(f"DNS/Timeout error: {request.url}")

    def closed(self, reason):
        print("\n======== Broken (404) Links ========")
        for link in sorted(self.rotten_links):
            print(link)

        print("\n======== Non-HTTPS Govt Sites ========")
        for site in sorted(self.non_https_sites):
            print(site)