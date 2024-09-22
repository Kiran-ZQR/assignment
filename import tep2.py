import os
from lxml import html
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 指定 HTML 文件路径
html_file = "D:/系统默认/output_file.html"

# 读取 HTML 文件
with open(html_file, 'r', encoding='utf-8') as file:
    page_content = file.read()

# 使用 lxml 解析 HTML
tree = html.fromstring(page_content)

# 提取表格行
rows = tree.xpath('//table//tr')

# 准备数据存储
times = []
temps = []
rhum_values = []  # 新增存储相对湿度

# 遍历表格行，提取时间、温度和相对湿度
for row in rows:
    columns = row.xpath('.//td/text()')
    if len(columns) > 3:  # 确保有足够数据（假设rhum在第三列）
        time = columns[0].strip()  # 获取时间
        temp = columns[1].strip()  # 获取温度
        rhum = columns[3].strip()  # 获取相对湿度（假设在第三列）
        if temp != 'NaN' and rhum != 'NaN':  # 过滤掉 NaN 数据
            # 将时间格式转换为 datetime 格式
            time_dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            times.append(time_dt)
            temps.append(float(temp))
            rhum_values.append(float(rhum))

# 确保有数据可视化
if times and temps and rhum_values:
    fig, ax1 = plt.subplots(figsize=(12, 8))

    # 绘制温度随时间的变化，使用淡粉色实线并加粗
    color = '#FFB6C1'  # 淡粉色
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (°C)', color=color)
    ax1.plot(times, temps, color=color, linestyle='-', linewidth=4, label='Temperature (°C)', alpha=0.7)
    ax1.scatter(times, temps, color=color, s=100, edgecolor='#FF69B4', linewidth=0.1, alpha=0.8)  # 更深的粉色 '#FF69B4'
    ax1.tick_params(axis='y', labelcolor=color)

    # 创建第二个 Y 轴
    ax2 = ax1.twinx()
    color = '#90EE90'  # 淡绿色
    ax2.set_ylabel('Relative Humidity (%)', color=color)
    ax2.plot(times, rhum_values, color=color, linestyle='--', linewidth=4, label='Relative Humidity (%)', alpha=0.7)
    ax2.scatter(times, rhum_values, color=color, s=100, edgecolor='#32CD32', linewidth=0.1, alpha=0.8)  # 更深的绿色 '#32CD32'
    ax2.tick_params(axis='y', labelcolor=color)
    
    # 时间格式化，显示每6小时的数据点
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=16))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    # 自动调整布局
    fig.autofmt_xdate()

    # 设置图表标题
    plt.title('Temperature and Relative Humidity Over Time')

    # 显示图例
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # 增加网格线和图表美观度
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 显示图表
    plt.tight_layout()  # 自动调整布局以避免标签重叠
    plt.show()
else:
    print("NONE")