from flask import Flask, request, render_template, jsonify, send_from_directory
from scrapper3 import MagicpinSpider
from scrapy.http import TextResponse
from helper_func import find_combinations
from urllib.parse import urlparse
import traceback
import requests
import logging

# Configure logging
logging.basicConfig( level=logging.INFO)

app = Flask(__name__)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get form data
            url = request.form['url']
            target_sum = request.form['target_sum']
            percentage = request.form['percentage']
            upto = request.form['upto']
            upto_val=0
            if(len(upto)!=0):
                upto_val=int(upto)
            # Server-side validation
            if not url.strip():
                logging.error("Please enter a URL.")
                return render_template('index.html', error="Please enter a URL.")
            if 'magicpin.in' not in urlparse(url).netloc:
                logging.error("The URL must be from magicpin.in domain.")
                return render_template('index.html', error="The URL must be from magicpin.in domain.")
            if not target_sum.strip() and (not percentage.strip() or not upto.strip()):
                logging.error("Please enter either Total Amount or Percentage off with Upto value.")
                return render_template('index.html', error="Please enter either Total Amount or Percentage off with Upto value.")
            if target_sum.strip() and (percentage.strip() or upto.strip()):
                logging.error("Please enter only Total Amount or Percentage off with Upto value, not both.")
                return render_template('index.html', error="Please enter only Total Amount or Percentage off with Upto value, not both.")

            # Calculate target_sum_f based on user input
            if target_sum.strip():
                target_sum_f = int(target_sum)
            else:
                target_sum_f = int(upto) * 100 / int(percentage)

            # Instantiate the spider with the URL
            spider = MagicpinSpider()

            # Fetch the HTML content
            response = TextResponse(url=url, body=requests.get(url).text, encoding='utf-8')

            # Scrape data from the provided URL
            scraped_data = spider.parse(response)

            # Find combinations for the scraped data and target sum
            combinations = find_combinations(scraped_data['item_data'], target_sum_f)

            return render_template('result.html', combinations=combinations, hotel_name=scraped_data['hotel_name'], scraped_data=scraped_data['item_data'],upto_val=int(upto_val))
        except Exception as e:
            # Log the error or handle it as required
            logging.error("An error occurred: %s", str(e))  # Log the error to the file 'app.log'
            traceback.print_exc()  # Print the traceback to console for debugging
            error_msg = "An error occurred: " + str(e)
            logging.error(error_msg)
            return render_template('index.html', error=error_msg)

    return render_template('index.html')

if __name__ == '__main__':
    logging.info("Starting the app.")
    app.run(port=80)
