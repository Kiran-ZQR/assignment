import pandas as pd

# 加载CSV文件
csv_file = 'D:/系统默认/export.csv' 
data = pd.read_csv(csv_file)

# 将CSV数据保存为HTML文件
html_file = 'D:/系统默认/作业/assignment2/output_file.html' 
data.to_html(html_file, index=False)