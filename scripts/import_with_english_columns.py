import pandas as pd
from sqlalchemy import create_engine
import os

# --- 配置 ---
base_dir = "/root/telecom_project"
data_file = os.path.join(base_dir, "data/合并后的大表.csv")
MYSQL_PASSWORD = "123456"  # 请替换为你的真实密码

# --- 定义列名映射 (中文 -> 英文) ---
column_mapping = {
    '云池': 'yunchi',
    '设备名称': 'device_name',
    'cpu分配量（核）': 'cpu_alloc',
    '内存分配量(GB)': 'mem_alloc',
    '存储分配量(GB)': 'storage_alloc',
    'power off': 'power_status',
    'tools': 'tools',
    'cpu利用率日峰值(%)': 'cpu_peak',
    '内存利用率日峰值(%)': 'mem_peak',
    '存储利用率日峰值(%)': 'storage_peak',
    'CPU>30': 'cpu_over_30',
    'MEM>60': 'mem_over_60',
    '采集源': 'source',
    '节点': 'node',
    '项目': 'project',
    '集群': 'cluster',
    '存在状态': 'exist_status',
    '日期': 'date',
    'CPU>30每小时': 'cpu_over_30_hourly',
    'MEM>60每小时': 'mem_over_60_hourly'
}

# --- 执行导入 ---
print("📖 正在读取CSV文件...")
df = pd.read_csv(data_file, encoding='utf-8-sig', low_memory=False)

# 重命名列
print("🏷️  正在将列名转换为英文...")
df.rename(columns=column_mapping, inplace=True)

# 连接MySQL
engine = create_engine(f"mysql+pymysql://root:{MYSQL_PASSWORD}@localhost:3306/vanna_db?charset=utf8mb4")
# 导入到新表 (如果表存在则替换)
print(f"💾 正在导入数据到表 'utilization_en' ...")
df.to_sql('utilization_en', con=engine, if_exists='replace', index=False, chunksize=1000)

print(f"✅ 导入完成！共导入 {len(df)} 行数据。")
print("📋 新表 'utilization_en' 已创建，所有列名均为英文。")
