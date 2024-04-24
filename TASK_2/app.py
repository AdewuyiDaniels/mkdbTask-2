from flask import Flask, request, jsonify
import pandas as pd

#QUESTION 1 AND 2

# Load the sales data
sales_data = pd.read_csv('data/sales_data_sample.csv', encoding='latin1')

#Create Flask App
app = Flask(__name__)

@app.route('/top_earning_sale_item', methods=['GET'])
def top_earning_sale_item():
    top_item = sales_data.groupby('PRODUCTLINE')['SALES'].sum().idxmax()
    return jsonify({'top_item': top_item})

@app.route('/best_sales_city', methods=['GET'])
def best_sales_city():
    best_city = sales_data.groupby('CITY')['SALES'].sum().idxmax()
    return jsonify({'best_city': best_city})

@app.route('/top_5_products', methods=['GET'])
def top_5_products():
    last_quarter_data = sales_data[(sales_data['YEAR_ID'] == 2003) & (sales_data['QTR_ID'] == 4)]
    filtered_data = last_quarter_data[(last_quarter_data['STATUS'] == 'Shipped') & (last_quarter_data['QUANTITYORDERED'] >= 40)]
    top_5_products = filtered_data.groupby('PRODUCTLINE')['SALES'].sum().nlargest(5).index.tolist()
    return jsonify({'top_5_products': top_5_products})

@app.route('/customer_segmentation', methods=['GET'])
def customer_segmentation():
    customers = sales_data.groupby('CUSTOMERNAME').filter(lambda x: (x['SALES'] > 5000).sum() > 3)
    customers_usa_france = customers[customers['COUNTRY'].isin(['USA', 'France'])]
    unique_customers = customers_usa_france['CUSTOMERNAME'].unique().tolist()
    return jsonify({'segmented_customers': unique_customers})

@app.route('/product_demand_fluctuation', methods=['GET'])
def product_demand_fluctuation():
    monthly_data = sales_data[sales_data['YEAR_ID'] == 2003]
    monthly_data = monthly_data[(monthly_data['SALES'] > 100000) & (monthly_data['PRICEEACH'] > 80)]
    highest_avg_order_qty_month = monthly_data.groupby('MONTH_ID')['QUANTITYORDERED'].mean().idxmax()
    return jsonify({'highest_avg_order_qty_month': highest_avg_order_qty_month})

@app.route('/regional_sales_comparison', methods=['GET'])
def regional_sales_comparison():
    state1 = request.args.get('state1')
    state2 = request.args.get('state2')
    filtered_data = sales_data[(sales_data['YEAR_ID'] == 2003) & (sales_data['STATUS'] == 'Shipped') & (sales_data['QUANTITYORDERED'] >= 20)]
    avg_order_value_state1 = filtered_data[filtered_data['STATE'] == state1]['SALES'].mean()
    avg_order_value_state2 = filtered_data[filtered_data['STATE'] == state2]['SALES'].mean()
    return jsonify({'avg_order_value_comparison': {state1: avg_order_value_state1, state2: avg_order_value_state2}})

@app.route('/order_fulfillment_efficiency', methods=['GET'])
def order_fulfillment_efficiency():
    # Filter data for orders placed in the first half of 2003
    first_half_data = sales_data[pd.to_datetime(sales_data['ORDERDATE']).dt.month <= 6]

    # Group by country and count orders
    country_orders = first_half_data['COUNTRY'].value_counts()

    # Filter countries with more than 50 total orders
    efficient_countries = country_orders[country_orders > 50]

    # Filter orders for efficient countries
    efficient_orders = first_half_data[first_half_data['COUNTRY'].isin(efficient_countries.index)]

    # Calculate order ship duration
    efficient_orders['ORDERDATE'] = pd.to_datetime(efficient_orders['ORDERDATE'])
    efficient_orders['SHIPPED_DATE'] = pd.to_datetime(efficient_orders['SHIPPED_DATE'])
    efficient_orders['ORDER_SHIP_DURATION'] = (efficient_orders['SHIPPED_DATE'] - efficient_orders['ORDERDATE']).dt.days

    # Filter orders shipped within 30 days
    orders_shipped_within_30_days = efficient_orders[efficient_orders['ORDER_SHIP_DURATION'] <= 30]

    # Calculate proportion of orders shipped within 30 days for each country
    proportion_orders_shipped = orders_shipped_within_30_days.groupby('COUNTRY').size() / efficient_countries

    # Find country with highest proportion
    highest_proportion_country = proportion_orders_shipped.idxmax()

    return jsonify({'highest_proportion_country': highest_proportion_country})


@app.route('/sales_trend_analysis', methods=['GET'])
def sales_trend_analysis():
    category = request.args.get('category')
    monthly_data = sales_data[sales_data['YEAR_ID'] == 2003]
    category_sales = monthly_data[monthly_data['PRODUCTLINE'] == category]
    category_sales['ORDERDATE'] = pd.to_datetime(category_sales['ORDERDATE'])
    category_sales = category_sales.sort_values('ORDERDATE')
    category_sales['SALES_CHANGE'] = category_sales['SALES'].pct_change()
    month_with_25_percent_increase = category_sales[(category_sales['SALES_CHANGE'] > 0.25) & (category_sales['PRICEEACH'] < 100)]['ORDERDATE'].iloc[0]
    return jsonify({'month_with_25_percent_increase': month_with_25_percent_increase})

if __name__ == '__main__':
    app.run(debug=True)