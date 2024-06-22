from flask import Flask, render_template, url_for
import requests
import csv
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Define your services and their API endpoints
SERVICES = [
    {
        "name": "Pricenet",
        "endpoint": "https://api.vishok.me/pricenet",
        "status": None,
        "description": "A price comparison engine written in node.js"
    }
]

CSV_FILE = "services_status.csv"

# Function to read last check time and status for all services from CSV
def read_services_status():
    services_status = {}
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                services_status[row['name']] = {
                    'last_checked': datetime.strptime(row['last_checked'], '%Y-%m-%d %H:%M:%S'),
                    'status': row['status']
                }
    return services_status

# Function to write current time and status for all services to CSV
def write_services_status(services):
    with open(CSV_FILE, 'w', newline='') as file:
        fieldnames = ['name', 'last_checked', 'status']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for service in services:
            writer.writerow({
                'name': service['name'],
                'last_checked': service['last_checked'].strftime('%Y-%m-%d %H:%M:%S'),
                'status': service['status']
            })

# Function to check status of a service
def check_service_status(service):
    try:
        start_time = datetime.now()
        response = requests.get(service["endpoint"])
        end_time = datetime.now()
        response_time_ms = (end_time - start_time).total_seconds() * 1000

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                if response_time_ms < 100:
                    service["status"] = 'Active'
                else:
                    service["status"] = 'Busy'
            else:
                service["status"] = 'Inactive'
        else:
            service["status"] = 'Inactive'
    except requests.exceptions.RequestException as e:
        print(e)
        service["status"] = 'Inactive'

# Route for the index page
@app.route('/')
def index():
    services_status = read_services_status()

    for service in SERVICES:
        last_checked = services_status.get(service["name"], {}).get('last_checked')

        # Check if last check time exists and if it's more than 5 minutes ago
        if last_checked is None or datetime.now() - last_checked > timedelta(minutes=5):
            check_service_status(service)
            service['last_checked'] = datetime.now()
            services_status[service["name"]] = {
                'last_checked': service['last_checked'],
                'status': service['status']
            }

    write_services_status(SERVICES)

    return render_template('index.html', services=SERVICES)

if __name__ == '__main__':
    app.run(debug=True)
