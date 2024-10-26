import os
from lxml import html
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

html_file = "output_file.html"

with open(html_file, 'r', encoding='utf-8') as file:
    page_content = file.read()

tree = html.fromstring(page_content)

rows = tree.xpath('//table//tr')

times = []
temps = []
rhum_values = []  

for row in rows:
    columns = row.xpath('.//td/text()')
    if len(columns) > 3:  
        time = columns[0].strip()  
        temp = columns[1].strip()  
        rhum = columns[3].strip()  
        if temp != 'NaN' and rhum != 'NaN':  
            time_dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            times.append(time_dt)
            temps.append(float(temp))
            rhum_values.append(float(rhum))

if times and temps and rhum_values:
    fig, ax1 = plt.subplots(figsize=(12, 8))

    color = '#FFB6C1' 
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (°C)', color=color)
    ax1.plot(times, temps, color=color, linestyle='-', linewidth=4, label='Temperature (°C)', alpha=0.7)
    ax1.scatter(times, temps, color=color, s=100, edgecolor='#FF69B4', linewidth=0.1, alpha=0.8)  
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = '#90EE90' 
    ax2.set_ylabel('Relative Humidity (%)', color=color)
    ax2.plot(times, rhum_values, color=color, linestyle='--', linewidth=4, label='Relative Humidity (%)', alpha=0.7)
    ax2.scatter(times, rhum_values, color=color, s=100, edgecolor='#32CD32', linewidth=0.1, alpha=0.8) 
    ax2.tick_params(axis='y', labelcolor=color)
    
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=16))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    fig.autofmt_xdate()

    plt.title('Temperature and Relative Humidity Over Time')

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    ax1.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show() 
else:
    print("NONE")
