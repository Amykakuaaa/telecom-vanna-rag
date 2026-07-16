"""
Vanna Agent - 适配 openai 2.x 版本 + 英文表结构
"""

import pandas as pd
from sqlalchemy import create_engine
from openai import OpenAI

print("=" * 60)
print("Vanna Agent 初始化 (英文表结构)")
print("=" * 60)

# ============================================================
# 1. 配置 LLM API
# ============================================================
client = OpenAI(
    base_url="http://8.145.39.17:8080/v1",
    api_key="sk-LRkt3NnxpxrvJndgGdo042rc5977VfFjLjiPEkXHbYRdzJWt"
)
print("✅ LLM API 配置完成")

# ============================================================
# 2. 配置 MySQL 连接
# ============================================================
MYSQL_PASSWORD = "123456"  

engine = create_engine(
    f"mysql+pymysql://root:{MYSQL_PASSWORD}@localhost:3306/vanna_db?charset=utf8mb4"
)
print("✅ MySQL 连接配置完成")

# ============================================================
# 3. 表结构描述（英文列名）
# ============================================================
TABLE_SCHEMA = """
数据库表 utilization_en 结构如下：
- device_name: 设备名称 (VARCHAR)
- power_status: 电源状态 (VARCHAR)，取值: 'Powered On'（开机）, 'Powered Off'（关机）, 'Suspended'（挂起）
- node: 节点/机房位置 (VARCHAR)，如: '七宝', '周家渡', '信息园'
- cpu_peak: CPU日峰值利用率 (DECIMAL)，范围 0-100
- mem_peak: 内存日峰值利用率 (DECIMAL)，范围 0-100
- storage_peak: 存储日峰值利用率 (DECIMAL)，范围 0-100
"""

# ============================================================
# 4. 核心查询函数
# ============================================================
def ask(question):
    """自然语言查询：问题 → SQL → 结果"""
    print(f"\n🤔 问题: {question}")
    print("-" * 50)
    
    prompt = f"""
你是一个 MySQL 专家。{TABLE_SCHEMA}

请根据用户问题生成标准的 MySQL SELECT 查询语句。
要求：
- 只返回 SQL 语句，不要包含任何解释、注释或额外文字
- SQL 语句以分号结尾
- 如果问题涉及"开机"，使用 power_status = 'Powered On'
- 如果问题涉及"关机"，使用 power_status = 'Powered Off'

用户问题: {question}
SQL:
"""
    try:
        response = client.chat.completions.create(
            model="minimax-m2.1-w8a8",
            messages=[
                {"role": "system", "content": "你是一个专业的 MySQL 查询生成器，只输出 SQL 语句。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql = response.choices[0].message.content.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()
        print(f"📝 生成的 SQL: {sql}")
        
        result = pd.read_sql(sql, engine)
        result._sql = sql
        print(f"✅ 查询成功，返回 {len(result)} 行")
        return result
        
    except Exception as e:
        error_msg = f"❌ 查询失败: {e}"
        print(error_msg)
        return error_msg


def run_sql(sql):
    """直接执行 SQL"""
    try:
        return pd.read_sql(sql, engine)
    except Exception as e:
        return f"执行失败: {e}"


print("\n✅ Vanna Agent 已就绪！")
print("使用: from scripts.vanna_agent import ask, run_sql")
