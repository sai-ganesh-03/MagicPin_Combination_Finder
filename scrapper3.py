from playwright.sync_api import sync_playwright
import scrapy
from scrapy import Selector
import logging
import time
class MagicpinSpider(scrapy.Spider):
    name = 'magicpin'

    def start_requests(self):
        # Here, we'll accept the URL from the function argument
        url = getattr(self, 'url', None)
        if url:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        start_parse = time.time()
        self.logger.info("Parsing Started")
        delivery_url, hotel_name = self.delivery_url_extractor(response.text)
        self.logger.info("Delivery URL Extracted")
        
        html_content = self.get_html_content(delivery_url)
        self.logger.info("HTML Content Extracted")
        selector = scrapy.Selector(text=html_content)
        
        # Extract item data using Scrapy selectors
        item_data = self.extract_item_data(selector)
        
        # Logging and time calculation
        self.logger.info("Scraping Completed")
        stop_parse = time.time()
        self.logger.info(f"Scraper took {stop_parse - start_parse} seconds")
        
        return {'item_data': item_data, 'hotel_name': hotel_name}
        
        
    def delivery_url_extractor(self, html_text):
        selector = Selector(text=html_text)
        delivery_tab = selector.css('a.delivery-tab')
        hotel_tab = selector.css('h1.v2 a::text')
        hotel_name = hotel_tab.get()
        if delivery_tab:
            delivery_href = delivery_tab.attrib['href']
            return [delivery_href, hotel_name]

    def get_html_content(self, delivery_url):
        with sync_playwright() as p:
        
            browser = p.webkit.launch()
            page = browser.new_page()
            page.route('**/*.{css*,woff,woff2,png,jpg,jpeg,gif,svg}', lambda route: route.abort())
            page.goto(delivery_url)
            selector = '.catalogItemsHolder .categoryListing:not(:first-child) .itemDetails'
            # Specify the maximum time to wait (in seconds)
            timeout = 30000
            
            # Wait for the expected number of elements to appear
            page.wait_for_selector(selector, state='attached', timeout=timeout)
            self.logger.info("Selector Found")
            time.sleep(1)
            # Get the HTML content after JavaScript execution
            html_content = page.content()
            browser.close()
        return html_content
    
    def extract_item_data(self, selector):
        # Extract item data using Scrapy selectors
        item_details_selector='.catalogItemsHolder .categoryListing:not(:first-child) .itemDetails'
        item_details = selector.css(item_details_selector)
        item_data = []
        for detail in item_details:
            try:
                item_name = detail.css('.itemName a.rel-handled::text').get()
                item_price = detail.css('.itemPrice.nonDiscountedPrice::text').get() or detail.css('.itemPrice::text').get()
                mrp = int(item_price.replace('₹', '').strip())
                item_data.append({"item_name": item_name, "mrp": mrp})
            except Exception as e:
                self.logger.error(f"An exception occurred while extracting item data: {str(e)}")
                continue
        return item_data

# Configure logging
logging.basicConfig(level=logging.INFO)