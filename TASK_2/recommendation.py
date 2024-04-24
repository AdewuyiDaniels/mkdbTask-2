from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import seasonal_decompose

# Load data (replace with your actual loading logic)
data = pd.read_csv("data/sales_data_sample.csv", encoding='latin1')

# Preprocess data (assuming 'OrderDate' has date format)
data['Month'] = pd.to_datetime(data['MONTH_ID']).dt.month_name()
data['Year'] = pd.to_datetime(data['YEAR_ID']).dt.year

# Pre-calculate monthly sales
monthly_sales = data.groupby(['MONTH_ID', 'Year'])['SALES'].sum().reset_index()

# Anomaly detection model (trained beforehand)
isolation_forest = IsolationForest(contamination=0.01)  # Adjust contamination for anomaly ratio
isolation_forest.fit(monthly_sales[['SALES']])

# Trend analysis function
def get_monthly_trend(month, year):
    data_subset = monthly_sales[(monthly_sales['MONTH_ID'] == month) & (monthly_sales['Year'] == year)]
    if data_subset.empty:
        return None
    decomposition = seasonal_decompose(data_subset['SALES'], model='additive')
    trend = decomposition.trend.iloc[-1]
    previous_trend = decomposition.trend.iloc[-2] if len(decomposition.trend) > 1 else None
    if previous_trend is not None and trend > previous_trend:
        # Calculate percentage increase
        increase = (trend - previous_trend) / previous_trend * 100
        return f"Sales trend shows an increase of {increase:.2f}% compared to the previous month."
    return None

app = Flask(__name__)

@app.route("/recommendation/<month>")
def get_recommendation(month):
    try:
        month_data = monthly_sales.loc[(monthly_sales['MONTH_ID'] == month)]
        if month_data.empty:
            return jsonify({'message': 'No data for this month'}), 404
        # Anomaly detection
        prediction = isolation_forest.predict(month_data[['SALES']])
        is_anomaly = prediction[0] == -1
        # Trend analysis
        trend = get_monthly_trend(month, month_data['Year'].values[0])
        response = ""
        if is_anomaly:
            response = "This month seems to have an unusual sales pattern compared to usual trends."
        elif trend:
            response = trend
        else:
            response = "Sales seem to be within the expected range for this month."
        return jsonify({'recommendation': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
