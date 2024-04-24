from flask import Flask, request, jsonify
import pandas as pd
import requests

app = Flask(__name__)

# Load data
orders_data = pd.read_csv("data/orders.csv.csv", encoding='latin1')
sales_data = pd.read_csv("data/sales_data_sample.csv", encoding='latin1')

# Gender API URL
GENDER_API_URL = "https://gender-api.com/get"

# Gender API Key 
GENDER_API_KEY = "23d5b1a2d73059c3b8c01daadfa4ad81f39dbc53c572295e463c56e81a5670e4"

def get_gender(first_name):
    try:
        # Prepare request parameters
        params = {
            "name": first_name,
            "key": GENDER_API_KEY
        }
        # Make request to Gender API
        response = requests.get(GENDER_API_URL, params=params)
        # Parse response JSON
        data = response.json()
        # Extract gender from response
        gender = data.get('gender', 'Unknown')
        return gender
    except Exception as e:
        print(f"Error fetching gender: {e}")
        return 'Unknown'

@app.route("/gender/<order_id>")
def get_customer_gender(order_id):
    try:
        # Find customer information for the specified order ID
        order_info = orders_data.loc[orders_data['OrderID'] == int(order_id)]
        if order_info.empty:
            return jsonify({'message': 'Order not found'}), 404
        # Extract customer number from order data
        customer_number = order_info['CustomerNumber'].iloc[0]
        # Find customer information in sales data
        customer_info = sales_data.loc[sales_data['CUSTOMERNUMBER'] == customer_number]
        if customer_info.empty:
            return jsonify({'message': 'Customer data not found'}), 404
        # Extract customer first name
        first_name = customer_info['CONTACTFIRSTNAME'].iloc[0]
        # Get gender from Gender API
        gender = get_gender(first_name)
        return jsonify({'gender': gender})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
