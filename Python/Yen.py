import numpy as np  # for ndarray 
import pandas as pd  # For data manipulation and analysis
import requests  # To extract data from the web
from bs4 import BeautifulSoup  # converts incoming records to Unicode and outgoing forms to UTF-8
import matplotlib.pyplot as plt
from datetime import date
import os  # For directory creation

def menu():
    current_date = date.today().strftime('%Y-%m-%d')  # Format as YYYY-MM-DD
    print("Hello!\nLet's check the current JPY to HKD at the real exchange rate...\n")
    return current_date

def web_extract():
    try:
        web = requests.get("https://wise.com/gb/currency-converter/jpy-to-hkd-rate#rate-alerts")
        if web.status_code == 200:  # Successful request
            soup = BeautifulSoup(web.content, 'html.parser')
            return soup
        print("Extraction failed! Please try later...")
        return None
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def extract_yen(soup):    
    result = {
        'current_rate': None,
        'recent_data': []
    }
    # Extract current exchange rate
    rate_element = soup.find('span', class_="text-success")
    if rate_element:
        try:
            rate_text = rate_element.text.strip().replace(',', '')
            result['current_rate'] = float(rate_text)
        except (ValueError, AttributeError):
            print("Failed to extract current rate.")
    
    # Extract recent data from summary table
    table = soup.find('table', class_="_table_1m11l_1")
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                try:
                    # Extract high, low, average from 30-day or 90-day columns
                    label = row.find('td').text.strip().lower()
                    if 'high' in label:
                        result['recent_data'].append(float(cells[1].text.strip()))
                    elif 'low' in label:
                        result['recent_data'].append(float(cells[1].text.strip()))
                    elif 'average' in label:
                        result['recent_data'].append(float(cells[1].text.strip()))
                except (ValueError, AttributeError):
                    continue
    
    # If no table data, try chart data from script tags
    if not result['recent_data']:
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'data' in script.string:
                try:
                    lines = script.string.split('\n')
                    for line in lines:
                        numbers = [float(n) for n in line.split() if n.replace('.', '').replace('-', '').isdigit()]
                        if numbers:
                            result['recent_data'].extend(numbers)
                    result['recent_data'] = result['recent_data'][:10]  # Limit to 10 points
                    break
                except Exception:
                    continue
    
    return result

def visual_trend(recent_data, date_str):
    if not recent_data:
        print("No data available to plot.")
        return
    
    # Create x-axis (indices of data points)
    x = np.arange(len(recent_data))
    # Convert rates to HKD per 100 JPY
    y = np.array(recent_data) * 100
    
    # Create the plot
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'b-', marker='o', label='HKD per 100 JPY')
    plt.title('Recent JPY to HKD Exchange Trend (100 JPY)')
    plt.xlabel('Data Point Index')
    plt.ylabel('HKD per 100 JPY')
    plt.grid(True)
    plt.legend()
    
    # Ensure save directory exists
    save_dir = 'Photos/Yen'
    os.makedirs(save_dir, exist_ok=True)
    
    # Save the plot
    try:
        plt.savefig(f'{save_dir}/{date_str}.png')
        print(f"Plot saved as {save_dir}/{date_str}.png")
    except Exception as e:
        print(f"Failed to save plot: {e}")

def main():
    date_str = menu()
    soup = web_extract()
    if soup is None:
        print("Due to the anomaly, the program will be terminated. Please try later.")
        return 1
    
    data = extract_yen(soup)
    if data is None or data['current_rate'] is None:
        print("Failed to extract exchange rate data.")
        return 1
    
    print(f"Current JPY to HKD exchange rate: {data['current_rate']}")
    # Calculate HKD for 100 JPY
    jpy_amount = 100
    hkd_amount = jpy_amount * data['current_rate']
    print(f"With {jpy_amount} JPY, you can exchange for {hkd_amount:.2f} HKD")
    
    if data['recent_data']:
        print("Recent exchange rates:", data['recent_data'])
        # Convert recent data to numpy array and pandas Series for analysis
        rates_array = np.array(data['recent_data'])
        rates_series = pd.Series(data['recent_data'])
        print("Basic statistics:")
        print(f"Mean rate: {rates_series.mean():.6f}")
        print(f"Standard deviation: {rates_series.std():.6f}")
        # Plot the trend
        visual_trend(data['recent_data'], date_str)
    else:
        print("No recent data available.")
    
    return 0

if __name__ == "__main__":
    main()