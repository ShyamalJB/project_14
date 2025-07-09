import scrapy
from urllib.parse import urljoin, urlparse
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError
import tldextract
from goi_scraper.items import LinkItem

# main spider class
class GoiSpider(scrapy.Spider):
    name = "goi_spider"
    allowed_domains = ['gov.in', 'nic.in']
    start_urls = ['https://igod.gov.in/sectors']

    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [404],
        'LOG_LEVEL': 'INFO'
    }
    
    visited_links = set()  # all domains crawled by spider stored in a set 'visited_links'
    
    def parse(self, response):

        # Check if URL is HTTPS or not
        parsed_url = urlparse(response.url)
        if parsed_url.scheme != 'https' and self.is_gov_site(parsed_url.netloc):
            https_issue = LinkItem(url=response.url, type='non_https')
            yield https_issue            

        # Attempting to crawl though each link present in the website
        try:
            for href in response.css('a::attr(href)').getall():
                link = urljoin(response.url, href)
                if self.should_visit(link):
                    yield response.follow(
                        link,
                        callback=self.parse,
                        errback=self.handle_error,
                        dont_filter=True
                    )
        except:
            print("Error while attempting to crawl !!!")

    # Function that checks if domain ends in 'gov.in' or 'nic.in' 
    def is_gov_site(self, domain):
        ext = tldextract.extract(domain)
        return ext.suffix == 'gov.in' or ext.suffix =='nic.in'
    
    # Function that checks if link's domain has been visited or not 
    # and adds unique domains to the set 'visited_links'
    def should_visit(self, link):
        parsed = urlparse(link)
        domain = parsed.netloc
        if self.is_gov_site(domain) and (domain not in self.visited_links):  
            url_add = urljoin(parsed.scheme + '://', domain)          
            self.visited_links.add(url_add)
            return True
        else:
            return False
    #Function that yields rotten links to output
    def handle_error(self, failure):
        request = failure.request
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                yield LinkItem(url=response.url, type='rotten')
        elif failure.check(DNSLookupError, TimeoutError):
            yield LinkItem(url=request.url, type='rotten')

    # Function that writes 'domains_visited.csv'
    def closed(self, reason):
        with open("domains_visited.csv", "w") as file:
            for item in self.visited_links:
                file.write(item + "\n")      
        self.logger.info(f"Visited links saved to 'domains_visited.csv'")
        self.logger.info(f"Spider ended due to {reason}")