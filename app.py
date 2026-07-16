"""
Vanna 2.0 Web 界面 - 极简版
功能：网页输入自然语言问题，展示 SQL 和查询结果
"""

from flask import Flask, request, render_template_string, jsonify
import sys
sys.path.append('/root/telecom_project')
from scripts.vanna_agent import ask, run_sql

app = Flask(__name__)

# ============================================================
# HTML 页面（内嵌在代码中，无需额外文件）
# ============================================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Vanna 数据查询助手</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f0f4f8;
            padding: 40px 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 28px;
            color: #1a202c;
            font-weight: 700;
        }
        .header p {
            color: #718096;
            margin-top: 8px;
            font-size: 16px;
        }
        .card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            padding: 30px;
            margin-bottom: 24px;
        }
        .input-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .input-group input {
            flex: 1;
            min-width: 200px;
            padding: 14px 18px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.2s;
            outline: none;
        }
        .input-group input:focus {
            border-color: #4299e1;
        }
        .input-group button {
            padding: 14px 32px;
            background: #4299e1;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .input-group button:hover {
            background: #3182ce;
        }
        .input-group button:disabled {
            background: #a0aec0;
            cursor: not-allowed;
        }
        .quick-questions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 16px;
        }
        .quick-questions button {
            padding: 8px 16px;
            background: #edf2f7;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            color: #2d3748;
        }
        .quick-questions button:hover {
            background: #e2e8f0;
            border-color: #4299e1;
        }
        .result-section {
            margin-top: 20px;
        }
        .result-section .label {
            font-size: 14px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 8px;
        }
        .sql-box {
            background: #1a202c;
            color: #68d391;
            padding: 16px 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
            margin-bottom: 16px;
        }
        .sql-box .label-sql {
            color: #a0aec0;
            font-size: 12px;
            margin-bottom: 8px;
        }
        .table-wrapper {
            overflow-x: auto;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        table th {
            background: #f7fafc;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            color: #2d3748;
            border-bottom: 2px solid #e2e8f0;
        }
        table td {
            padding: 10px 16px;
            border-bottom: 1px solid #edf2f7;
            color: #4a5568;
        }
        table tr:hover td {
            background: #f7fafc;
        }
        .status {
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 16px;
            font-size: 14px;
        }
        .status.loading {
            background: #ebf8ff;
            color: #2b6cb0;
        }
        .status.success {
            background: #f0fff4;
            color: #276749;
        }
        .status.error {
            background: #fff5f5;
            color: #9b2c2c;
        }
        .footer {
            text-align: center;
            color: #a0aec0;
            font-size: 14px;
            margin-top: 20px;
        }
        .loading-spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 3px solid #e2e8f0;
            border-top-color: #4299e1;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            vertical-align: middle;
            margin-right: 10px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🤖 Vanna 数据查询助手</h1>
        <p>用自然语言提问，AI 自动生成 SQL 并返回结果</p>
    </div>

    <div class="card">
        <div class="input-group">
            <input type="text" id="questionInput" placeholder="输入你的问题，例如：统计开机状态的虚拟机数量" />
            <button id="askBtn" onclick="askQuestion()">🔍 查询</button>
        </div>
        <div class="quick-questions">
            <button onclick="quickAsk('统计开机状态的虚拟机数量')">开机数量</button>
            <button onclick="quickAsk('CPU利用率最高的5台虚拟机')">CPU Top 5</button>
            <button onclick="quickAsk('七宝节点有多少台虚拟机')">七宝数量</button>
            <button onclick="quickAsk('内存利用率超过90%的虚拟机')">内存超90%</button>
        </div>
    </div>

    <div id="resultArea">
        <!-- 结果会动态显示在这里 -->
    </div>

    <div class="footer">
        Vanna 2.0 · 自然语言转 SQL
    </div>
</div>

<script>
    async function askQuestion() {
        const input = document.getElementById('questionInput');
        const question = input.value.trim();
        if (!question) return;
        await doAsk(question);
    }

    async function quickAsk(question) {
        document.getElementById('questionInput').value = question;
        await doAsk(question);
    }

    async function doAsk(question) {
        const btn = document.getElementById('askBtn');
        const resultArea = document.getElementById('resultArea');

        btn.disabled = true;
        btn.textContent = '⏳ 处理中...';

        resultArea.innerHTML = `
            <div class="card">
                <div class="status loading">
                    <span class="loading-spinner"></span> 正在处理: "${question}"
                </div>
            </div>
        `;

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });

            const data = await response.json();

            if (data.error) {
                resultArea.innerHTML = `
                    <div class="card">
                        <div class="status error">❌ ${data.error}</div>
                    </div>
                `;
                return;
            }

            let tableHtml = '';
            if (data.data && data.data.length > 0) {
                const headers = Object.keys(data.data[0]);
                let rows = '';
                data.data.forEach(row => {
                    rows += '<tr>';
                    headers.forEach(h => {
                        rows += `<td>${row[h] !== null ? row[h] : ''}</td>`;
                    });
                    rows += '</tr>';
                });
                tableHtml = `
                    <div class="label">📊 查询结果 (共 ${data.rowCount} 行)</div>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
                            <tbody>${rows}</tbody>
                        </table>
                    </div>
                `;
            } else {
                tableHtml = `<div class="status success">✅ 查询成功，没有匹配的数据</div>`;
            }

            resultArea.innerHTML = `
                <div class="card">
                    <div class="status success">✅ 查询完成</div>
                    <div class="label">📝 生成的 SQL</div>
                    <div class="sql-box"><div class="label-sql">-- 自动生成</div>${data.sql}</div>
                    ${tableHtml}
                </div>
            `;

        } catch (err) {
            resultArea.innerHTML = `
                <div class="card">
                    <div class="status error">❌ 请求失败: ${err.message}</div>
                </div>
            `;
        }

        btn.disabled = false;
        btn.textContent = '🔍 查询';
    }

    // 回车键触发查询
    document.getElementById('questionInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') askQuestion();
    });
</script>

</body>
</html>
"""

# ============================================================
# Flask 路由
# ============================================================

@app.route('/')
def index():
    """主页：显示 HTML 界面"""
    return HTML_PAGE

@app.route('/api/ask', methods=['POST'])
def api_ask():
    """API：接收问题，返回 SQL 和结果"""
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': '请输入问题'})
    
    try:
        # 调用 Vanna 生成 SQL 并执行
        result = ask(question)
        
        # 检查是否返回了错误信息（字符串）
        if isinstance(result, str) and result.startswith('❌'):
            return jsonify({'error': result})
        
        # 如果是 DataFrame，转换为 JSON
        if hasattr(result, 'to_dict'):
            return jsonify({
                'sql': getattr(result, '_sql', ''),
                'data': result.to_dict('records'),
                'rowCount': len(result)
            })
        else:
            return jsonify({
                'sql': '',
                'data': [],
                'rowCount': 0,
                'result': str(result)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)})

# 在 ask 函数中保存生成的 SQL（用于展示）
_original_ask = ask
def ask_with_sql(question):
    import pandas as pd
    import openai
    
    # 构建提示词
    prompt = f"""
你是一个 MySQL 专家。数据库视图 v_utilization 结构如下：
- device_name: 设备名称 (VARCHAR)
- power_status: 电源状态 (VARCHAR)，取值: 'Powered On'（开机）, 'Powered Off'（关机）, 'Suspended'（挂起）
- node: 节点/机房位置 (VARCHAR)
- cpu_peak: CPU日峰值利用率 (DECIMAL)

请根据问题生成 SQL 查询语句，只返回 SQL，不要包含任何解释：
问题: {question}
SQL:
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        sql = response.choices[0].message.content.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        # 执行 SQL
        from scripts.vanna_agent import engine
        result = pd.read_sql(sql, engine)
        result._sql = sql  # 保存 SQL 到 DataFrame 的属性中
        return result
    except Exception as e:
        return f"❌ 查询失败: {e}"

# 替换原来的 ask 函数
import scripts.vanna_agent
scripts.vanna_agent.ask = ask_with_sql

# 重新导入 ask 以便使用新函数
from scripts.vanna_agent import ask as new_ask

@app.route('/api/ask', methods=['POST'])
def api_ask_new():
    """API：接收问题，返回 SQL 和结果"""
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': '请输入问题'})
    
    try:
        result = new_ask(question)
        
        if isinstance(result, str) and result.startswith('❌'):
            return jsonify({'error': result})
        
        if hasattr(result, 'to_dict'):
            sql = getattr(result, '_sql', '')
            return jsonify({
                'sql': sql,
                'data': result.to_dict('records'),
                'rowCount': len(result)
            })
        else:
            return jsonify({
                'sql': '',
                'data': [],
                'rowCount': 0,
                'result': str(result)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Vanna Web 服务启动")
    print("=" * 60)
    print("\n访问地址: http://localhost:5100")    
    print("或: http://你的虚拟机IP:5100")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5100, debug=True)
