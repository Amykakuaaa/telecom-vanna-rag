# 智能问数 RAG 项目

> 基于 Vanna + Flask + MySQL 的自然语言查询系统，支持通过中文提问自动生成 SQL 并返回虚拟机资源利用率数据。

---

## 项目简介

本项目面向云平台虚拟机资源运维场景，依靠大模型结合知识库自动解析虚拟机数据表、生成查询 SQL，自动统计虚拟机开机数量、资源利用率等指标，并智能解答运维人员、业务客户关于资源采集、计费数据的各类疑问。

项目整体采用 RAG 知识库架构，内置数据表结构、字段释义、运维查询逻辑等知识库内容，搭配 Agent 执行 SQL 查询并解析结果生成自然语言答复。

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Flask |
| 数据库 | MySQL 5.7（Docker 容器） |
| AI 引擎 | Vanna + OpenAI 兼容 API |
| LLM 模型 | minimax-m2.1-w8a8 |
| 环境管理 | Conda（Python 3.11） |
| 部署 | Docker + Docker Compose |

---

## 项目结构
/root/telecom_project/
├── app.py  # Flask Web 服务入口
├── scripts/
│ ├── vanna_agent.py # Vanna 核心逻辑（LLM 调用 + SQL 生成）
│ └── import_with_english_columns.py # 数据导入脚本（中文列名→英文）
├── data/ # 数据目录（CSV 文件不上传）
├── logs/ # 日志目录
├── requirements.txt # Python 依赖
├── .gitignore # Git 忽略文件配置
└── README.md # 项目说明文档

text

---

## 核心功能

1. **自然语言 → SQL 自动生成**：输入中文问题，自动生成 SQL 并执行查询
2. **虚拟机开机数量统计**：一键统计开机/关机/挂起状态虚拟机数量
3. **资源利用率 Top N 查询**：CPU、内存、存储利用率排行
4. **按节点、集群、日期多维度筛选**：支持七宝、周家渡、信息园等节点查询
5. **Web 可视化界面**：提供友好交互界面，支持快捷按钮

---

## 数据入库（已完成）

| 指标 | 数据 |
|------|------|
| 总行数 | 841,577 行 |
| 列数 | 20 列 |
| 日期范围 | 2026-05-14 ~ 2026-05-31 |
| 数据来源 | 18 个每日 CSV 文件合并 |


### 数据预处理（在 Windows 上执行）

```python
import pandas as pd
import glob
import os

folder_path = r"C:\Users\18117\Desktop\电信实习\利用率\利用率"
file_pattern = os.path.join(folder_path, "日峰值利用率*.csv")
all_files = glob.glob(file_pattern)

df_list = []
for file in all_files:
    filename = os.path.basename(file)
    date_str = filename.replace("日峰值利用率", "").replace(".csv", "")
    date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    df = pd.read_csv(file, encoding="utf-8-sig")
    df["日期"] = date_formatted
    df_list.append(df)

df_final = pd.concat(df_list, ignore_index=True)
df_final.to_csv("合并后的大表.csv", index=False, encoding="utf-8-sig")
```

### 列名映射（中文 → 英文）
import_with_english_columns.py   
导入时自动将中文列名映射为英文，避免 SQL 特殊字符问题：
中文列名	          英文列名
设备名称	        device_name
power off	       power_status
节点	                  node
cpu利用率日峰值(%)	cpu_peak
内存利用率日峰值(%)	mem_peak
存储利用率日峰值(%)	storage_peak
CPU>30	               cpu_over_30
MEM>60	               mem_over_60
日期	                   date


### 快速启动（CentOS 7）
1. 环境准备
1.1 安装 Miniconda
bash
#### 下载兼容 CentOS 7 的旧版 Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh -O /tmp/miniconda_old.sh
bash /tmp/miniconda_old.sh -b -p /root/miniconda3
/root/miniconda3/bin/conda init bash
source ~/.bashrc
conda --version   # 应显示 conda 4.12.0
1.2 创建 Python 3.11 环境
bash
conda create -n vanna_env python=3.11 -y
conda activate vanna_env
1.3 安装依赖
bash
#### conda 安装需要编译的包
conda install -c conda-forge numpy pandas greenlet

#### pip 安装纯 Python 包
pip install vanna openai sqlalchemy pymysql flask 


2. 启动 MySQL 容器
bash
docker run -d \
  --name mysql-vanna \
  --restart unless-stopped \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=vanna_db \
  -v vanna-mysql-data:/var/lib/mysql \
  mysql:5.7 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci


### 验证容器：

bash
docker ps | grep mysql-vanna
docker exec -it mysql-vanna mysql -uroot -p123456 -e "SHOW DATABASES;"   #vanna_db 数据库已经创建

3. 导入数据
bash
cd /root/telecom_project
python scripts/import_with_english_columns.py
4. 启动 Web 服务
bash
cd /root/telecom_project
python app.py
访问地址：http://<虚拟机IP>:5100

### 查询流程
text
用户输入问题（中文）
        ↓
Flask 后端接收（app.py）
        ↓
Vanna Agent（vanna_agent.py）
        ↓
拼接 Prompt（表结构 + 问题）
        ↓
LLM API（minimax-m2.1-w8a8）
        ↓
生成 SQL 语句
        ↓
执行 SQL 查询 MySQL
        ↓
     返回结果 
        ↓
     前端展示


### 测试查询
问题	预期结果
统计开机状态的虚拟机数量	返回 331512
CPU利用率最高的5台虚拟机	返回 Top 5 列表
七宝节点有多少台虚拟机	        返回具体数字
内存利用率超过90%的虚拟机	返回列表
