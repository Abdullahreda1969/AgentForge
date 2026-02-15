import yfinance as yf
import pandas as pd

def calculate_bmi(height, weight):
    """
    Calculates Body Mass Index (BMI) from height and weight.

    Args:
        height (float): Height in meters.
        weight (float): Weight in kilograms.

    Returns:
        float: BMI value.  Returns None if input is invalid.
    """
    if height <= 0 or weight <= 0:
        print("Error: Height and weight must be positive values.")
        return None
    try:
        data = yf.download("BMI", start="2020-01-01", end="2023-12-31")
        if data.empty:
            print("Error: No data available for BMI calculation.")
            return None
        bmi = data["BMI"].mean()
        return bmi
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    try:
        height = float(input("Enter your height in meters: "))
        weight = float(input("Enter your weight in kilograms: "))

        bmi = calculate_bmi(height, weight)

        if bmi is not None:
            print(f"Your BMI is: {bmi:.2f}")
            print("BMI is a measure of body fat based on height and weight.")
    except ValueError:
        print("Error: Invalid input. Please enter numeric values for height and weight.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")