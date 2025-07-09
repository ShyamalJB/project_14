# project_14
 Making a spider (web crawler) to extract all 404/rotten links and non-https sites in Government of India (GoI) sites
 
 
 ## version 1 (v1) : 
 - Made using scrapy
 - Listing the rotten links and non-https sites in 'links.csv' in spiders folder
 - Also listing the domains crawled by the spider in 'domains_visited.csv' in spiders folder
 - Starting url is an Integrated Govt Online Directory which contains links to all GoI sites (https://igod.gov.in/sectors)
 ## Instructions to run the spider
 Install scrapy by using pip: 
 ```bash
    pip install scrapy
 ```
 Go the spiders folder inside goi_scraper folder (Windows):
 ```bash
 cd .\goi_scraper\goi_scraper\spiders
 ```
 Go the spiders folder inside goi_scraper folder (macOS):
 ```bash
 cd ./goi_scraper/goi_scraper/spiders
 ```
 Start crawling spider and outputting 'links.csv' :
 ```bash
 scrapy crawl goi_spider -o links.csv
 ```
 
 P.S. I didn't get any rotten or non-https link 