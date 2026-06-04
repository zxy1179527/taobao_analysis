import pandas as pd
import numpy as np
import os

np.random.seed(17)

# ---------- 获取脚本所在目录并构建绝对路径 ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DATA_PATH = os.path.join(DATA_DIR, 'UserBehavior.csv')
OUTPUT_SAMPLE = os.path.join(DATA_DIR, 'taobao_sample_50k.parquet')
OUTPUT_DAILY = os.path.join(DATA_DIR, 'user_daily.parquet')

# ---------- 1. 分块读取并即时过滤时间范围 ----------
chunks = []
chunk_size = 500000
# 计算起止时间戳（秒）
start_ts = int(pd.Timestamp('2017-11-25 00:00:00').timestamp())
end_ts = int(pd.Timestamp('2017-12-04 00:00:00').timestamp())

print("开始分块读取并过滤数据...")
for i, chunk in enumerate(pd.read_csv(DATA_PATH, chunksize=chunk_size, header=None,
                                      names=['user_id', 'item_id', 'category_id', 'behavior_type', 'timestamp'])):
    # 过滤时间范围
    chunk = chunk[(chunk['timestamp'] >= start_ts) & (chunk['timestamp'] < end_ts)]
    if not chunk.empty:
        chunks.append(chunk)
    if i % 10 == 0 and i != 0:
        total_kept = sum(len(c) for c in chunks)
        print(f"已处理 {(i+1) * chunk_size} 行，当前保留行数: {total_kept}")

# 合并
df_raw = pd.concat(chunks, ignore_index=True)
print(f"过滤后原始数据量: {df_raw.shape}")

# 转换时间戳
df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'], unit='s')
print(f"时间戳转换完成，实际日期范围: {df_raw['timestamp'].min()} 至 {df_raw['timestamp'].max()}")

# ---------- 2. 探查与清洗----------
print(df_raw.info())
print(df_raw.head())
print("缺失值统计:\n", df_raw.isnull().sum())
print(f"完全重复行数: {df_raw.duplicated().sum()}")
df_raw.drop_duplicates(inplace=True)
print(f"去重后数据量: {df_raw.shape}")

# ---------- 3. 采样 5万用户 ----------
all_users = df_raw['user_id'].unique()
sampled_users = np.random.choice(all_users, size=50000, replace=False)
df_sample = df_raw[df_raw['user_id'].isin(sampled_users)].copy()
print(f"采样后数据量: {df_sample.shape}")
df_sample.reset_index(drop=True, inplace=True)


# ---------- 4. 内存优化 ----------
def memory_usage_mb(df):
    return df.memory_usage(deep=True).sum() / 1024 ** 2


before_mem = memory_usage_mb(df_sample)
print(f"优化前内存: {before_mem:.2f} MB")

for col in ['user_id', 'item_id', 'category_id', 'behavior_type']:
    df_sample[col] = df_sample[col].astype('category')

after_mem = memory_usage_mb(df_sample)
print(f"优化后内存: {after_mem:.2f} MB, 节省 {(1 - after_mem / before_mem) * 100:.1f}%")

# ---------- 5. 生成分析底表 ----------
df_sample.to_parquet(OUTPUT_SAMPLE, index=False)

df_sample['date'] = df_sample['timestamp'].dt.date
daily_agg = df_sample.groupby(['user_id', 'date', 'behavior_type'],observed=True).size().unstack(fill_value=0).reset_index()
for bt in ['pv', 'fav', 'cart', 'buy']:
    if bt not in daily_agg.columns:
        daily_agg[bt] = 0
daily_agg['total_actions'] = daily_agg[['pv', 'fav', 'cart', 'buy']].sum(axis=1)
daily_agg.to_parquet(OUTPUT_DAILY, index=False)

print("预处理完成，底表已保存。")
