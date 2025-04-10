Creating a "Smart Energy Tracker" web application involves several components, such as a web framework, a database for storing energy data, a front-end for displaying information, and some analytics for processing data. For simplicity, I'll outline a basic version using Flask, a lightweight Python web framework. This application will simulate data collection and provide a basic visualization using matplotlib for analytics. 

To keep the focus on Python, this example will not include the complexities of deploying a real-time dashboard or collecting live data from IoT devices, but will instead simulate the data collection process.

We'll use the following Python libraries:
- Flask: For creating the web application.
- matplotlib: For data visualization.
- SQLite: For storing energy data.
- NumPy: For data manipulation.
- Pandas: For data handling and analysis.

You can install Flask, matplotlib, NumPy, and Pandas via pip:

```bash
pip install flask matplotlib numpy pandas
```

Here’s a simplified version of the application:

```python
from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime

app = Flask(__name__)

# Create a database and table if it doesn't exist
def init_db():
    with sqlite3.connect('energy.db') as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS energy_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        usage FLOAT NOT NULL)''')
    print("Database initialized.")

# Insert a new energy usage entry
def insert_data(usage):
    try:
        with sqlite3.connect('energy.db') as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO energy_usage (usage) VALUES (?)", (usage,))
            conn.commit()
            print(f"Inserted usage: {usage}")
    except sqlite3.Error as e:
        print(f"An error occurred while inserting data: {e}")

# Retrieve data from the last 'n' days
def get_data(days=7):
    try:
        query = "SELECT timestamp, usage FROM energy_usage WHERE timestamp >= datetime('now', ?)"
        with sqlite3.connect('energy.db') as conn:
            df = pd.read_sql_query(query, conn, params=(f'-{days} days',))
        return df
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving data: {e}")
        return pd.DataFrame()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    try:
        usage = float(request.form['usage'])
        insert_data(usage)
        return jsonify({'status': 'success', 'message': 'Data added successfully!'})
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid input! Please enter a numeric value.'}), 400


@app.route('/visualize')
def visualize():
    try:
        df = get_data()
        if df.empty:
            return jsonify({'status': 'error', 'message': 'No data available for visualization.'}), 400

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['usage'], marker='o')
        plt.title('Energy Usage Over Time')
        plt.xlabel('Timestamp')
        plt.ylabel('Energy Usage (kWh)')
        plt.xticks(rotation=45)
        plt.tight_layout()

        image_path = 'static/usage_plot.png'
        plt.savefig(image_path)
        plt.close()

        return jsonify({'status': 'success', 'image_path': image_path})
    except Exception as e:
        print(f"An error occurred during visualization: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to generate visualization.'}), 500


if __name__ == '__main__':
    # Initialize the database
    init_db()
    # Run the application
    app.run(debug=True)
```

### HTML Template (index.html)
Create a simple HTML file `index.html` in a `templates` directory to interact with the application:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Energy Tracker</title>
</head>
<body>
    <h1>Smart Energy Tracker</h1>
    <form id="usageForm">
        <label for="usage">Enter energy usage (kWh):</label>
        <input type="text" id="usage" name="usage" required>
        <button type="submit">Submit</button>
    </form>
    <div id="message"></div>
    <h2>Energy Usage Visualization</h2>
    <button id="visualizeBtn">Show Visualization</button>
    <div id="visualization"></div>

    <script>
        document.getElementById('usageForm').onsubmit = function (event) {
            event.preventDefault();
            let usage = document.getElementById('usage').value;
            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `usage=${usage}`
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('message').innerText = data.message;
            });
        };

        document.getElementById('visualizeBtn').onclick = function () {
            fetch('/visualize')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('visualization').innerHTML = `<img src="${data.image_path}" alt="Energy Usage Plot">`;
                } else {
                    document.getElementById('visualization').innerText = data.message;
                }
            });
        };
    </script>
</body>
</html>
```

### Explanation and Error Handling
1. **Database Initialization:** The `init_db()` function creates a table if it doesn't exist.
2. **Data Insertion:** The `insert_data()` function adds energy usage data to the database. It handles exceptions related to database errors.
3. **Data Retrieval:** The `get_data()` function fetches data for the last `n` days. It handles exceptions if the query fails.
4. **Visualization:** The `/visualize` route generates a plot of the energy usage data. It handles exceptions for any errors during the plotting process.
5. **Web Interaction:** The HTML form and JavaScript handle submissions and interaction with the Flask routes.

This application provides a starting point for a smart energy tracker. In a real-world application, you would likely integrate user authentication, more detailed analytics, and real-time data collection from IoT sensors.