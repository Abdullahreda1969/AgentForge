import yfinance as yf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_gold_price():
    """
    Retrieves the current price of Gold (GC=F) from Yahoo Finance.
    """
    try:
        # Download the data
        data = yf.download(tickers=["GC=F"], period="1d")

        # Check if data is valid
        if data.empty:
            logging.warning("No data found for GC=F.")
            return None

        # Extract the price
        gold_price = data['Close'].iloc[-1]  # Get the last closing price
        return gold_price

    except Exception as e:
        logging.error(f"Error retrieving gold price: {e}")
        return None

if __name__ == "__main__":
    gold_price = get_gold_price()

    if gold_price is not None:
        print(f"The current price of Gold (GC=F) is: {gold_price}")
    else:
        print("Could not retrieve the gold price.")