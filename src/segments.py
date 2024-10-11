import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 读取Excel文件
# 假设Excel文件名为'weici.xlsx'，并且分数在名为'分数'的列中
file_name = 'C:\\Users\\wonder\\Documents\\college-major4hs\\2024高考\\weici.xlsx'
column_name = '分数'  # 根据实际的列名进行调整
df = pd.read_excel(file_name)

# 获取分数列的数据
scores = df[column_name].values

# 计算均值和标准差
mean = np.mean(scores)
std = np.std(scores)

# 定义分段的边界
bins = [
    mean - 3*std, mean - 2*std, mean - std, mean,
    mean + std, mean + 2*std, mean + 3*std
]

# 计算每个分段的人数
counts, bin_edges = np.histogram(scores, bins=bins)

# 绘制分数的直方图
plt.hist(scores, bins=bins, alpha=0.7, color='blue', edgecolor='black')

# 添加标题和标签
plt.title('Score Distribution Based on Standard Deviation')
plt.xlabel('Score')
plt.ylabel('Number of Students')
#plt.xticks(bins, ['<{}'].format(round(mean - 3*std, 2)) + ', '.join(['{:.2f}'.format(round(x, 2)) for x in (mean - 2*std, mean - std, mean, mean + std, mean + 2*std, mean + 3*std)]) + '>')
#plt.xticks(bins, ['<{}'.format(round(mean - 3*std, 2))] + ', '.join(['{:.2f}'.format(round(x, 2)) for x in (mean - 2*std, mean - std, mean, mean + std, mean + 2*std, mean + 3*std)]) + '>')
#plt.xticks(bins, ['<{0}'.format(round(mean - 3*std, 2))] + ', '.join(['{:.2f}'.format(round(x, 2)) for x in (mean - 2*std, mean - std, mean, mean + std, mean + 2*std, mean + 3*std)]) + '>')
# 显示图表
plt.show()