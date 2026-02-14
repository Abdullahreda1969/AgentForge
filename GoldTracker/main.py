import requests
import json
import logging
import unittest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GoldPriceSaver:
    def __init__(self, mock_api_url):
        self.mock_api_url = mock_api_url
        self.mock_api_key = "YOUR_API_KEY"  # Replace with a real API key

    def get_gold_price(self):
        """
        Fetches gold price from the mock API.
        """
        try:
            response = requests.get(self.mock_api_url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            return data['gold_price']
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return None
        except (KeyError, TypeError) as e:
            logging.error(f"Invalid JSON response: {e}")
            return None

    def save_gold_price(self, gold_price):
        """
        Saves the gold price to a file.
        """
        try:
            with open("gold_price.json", "w") as f:
                json.dump(gold_price, f)
            logging.info(f"Gold price saved to gold_price.json")
        except IOError as e:
            logging.error(f"Error writing to file: {e}")

    def update_gold_price(self, gold_price):
        """
        Updates the gold price in the file.
        """
        try:
            with open("gold_price.json", "w") as f:
                json.dump(gold_price, f)
            logging.info(f"Gold price updated in gold_price.json")
        except IOError as e:
            logging.error(f"Error writing to file: {e}")


# Example Usage (for unit testing)
class TestGoldPriceSaver(unittest.TestCase):

    def test_get_gold_price(self):
        mock_api_url = "https://mock-gold-api.com/gold"
        saver = GoldPriceSaver(mock_api_url)
        gold_price = saver.get_gold_price()
        self.assertEqual(gold_price, 1900.50)

    def test_save_gold_price(self):
        mock_api_url = "https://mock-gold-api.com/gold"
        saver = GoldPriceSaver(mock_api_url)
        saver.save_gold_price(1900.50)
        self.assertEqual(saver.mock_api_url, "https://mock-gold-api.com/gold")

    def test_update_gold_price(self):
        mock_api_url = "https://mock-gold-api.com/gold"
        saver = GoldPriceSaver(mock_api_url)
        saver.update_gold_price(1900.50)
        self.assertEqual(saver.mock_api_url, "https://mock-gold-api.com/gold")

    def test_invalid_api_response(self):
        mock_api_url = "https://mock-gold-api.com/gold"
        saver = GoldPriceSaver(mock_api_url)
        invalid_price = saver.get_gold_price()
        self.assertIsNone(invalid_price)

    def test_file_write_error(self):
        mock_api_url = "https://mock-gold-api.com/gold"
        saver = GoldPriceSaver(mock_api_url)
        try:
            saver.save_gold_price("invalid_price")
        except IOError as e:
            self.fail(f"File write error: {e}")

if __name__ == '__main__':
    unittest.main()