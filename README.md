# 淘宝用户行为分析

> 基于约 100 万用户 9 天行为数据的采样分析项目，覆盖流量监控、留存复购、RF 分层与品类交叉销售。

## 数据
- 来源：UserBehavior.csv（2017-11-25 至 2017-12-03）
- 采样：5 万随机用户
- 行为类型：点击、收藏、加购、购买

## 项目结构
├── data/ # 采样、中间数据及分析结果（.parquet, .csv）
├── outputs/ # 分析图表（.png）
├── notebooks/  ├── 笔记本/
│ ├── 01_traffic_funnel.ipynb
│ ├── 02_retention_repurchase.ipynb
│ └── 03_crm_cross_sell.ipynb
├── preprocessing.py # 数据清洗、采样与底表生成
└── README.md


## 分析模块
1. **流量、时序与转化漏斗**  
   - 每日 UV/PV 及人均 PV 趋势  
   - 24 小时行为分布  
   - 全站浏览→购买转化漏斗  

2. **用户留存与动态复购**  
   - 次日～7 日留存衰减曲线  
   - 购买行为路径分布  
   - 复购周期分布与流失预警线  

3. **精细化 CRM 与品类诊断**  
   - RF 客户分层（价值/忠诚/潜力/流失风险）  
   - 品类流量-转化波士顿矩阵  
   - 高频品类交叉销售共现矩阵  

## 技术栈
Python · Pandas · NumPy · Matplotlib · Seaborn
