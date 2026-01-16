# ====== 网页代码 ======
@app.route("/", methods=["GET"])
def index():
    return """
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>智能文档生成</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    }
    
    body {
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }
    
    .container {
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      width: 100%;
      max-width: 600px;
      padding: 40px;
      transition: transform 0.3s ease;
    }
    
    .container:hover {
      transform: translateY(-5px);
    }
    
    h2 {
      color: #2c3e50;
      text-align: center;
      margin-bottom: 30px;
      font-weight: 600;
      font-size: 28px;
    }
    
    .form-group {
      margin-bottom: 25px;
    }
    
    label {
      display: block;
      margin-bottom: 8px;
      color: #34495e;
      font-weight: 500;
      font-size: 16px;
    }
    
    input, textarea {
      width: 100%;
      padding: 12px 15px;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 16px;
      transition: all 0.3s;
      background-color: #f8f9fa;
    }
    
    input:focus, textarea:focus {
      outline: none;
      border-color: #3498db;
      box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
      background-color: white;
    }
    
    textarea {
      min-height: 150px;
      resize: vertical;
    }
    
    .button-container {
      text-align: center;
      margin-top: 30px;
    }
    
    button {
      background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 14px 30px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    button:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
    }
    
    button:active {
      transform: translateY(0);
    }
    
    button:disabled {
      background: #95a5a6;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
    
    .loading {
      display: none;
      text-align: center;
      margin-top: 20px;
    }
    
    .spinner {
      border: 4px solid rgba(52, 152, 219, 0.2);
      border-radius: 50%;
      border-top: 4px solid #3498db;
      width: 30px;
      height: 30px;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .footer {
      text-align: center;
      margin-top: 30px;
      color: #7f8c8d;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>智能文档生成</h2>
    
    <div class="form-group">
      <label for="title">文档标题</label>
      <input type="text" id="title" placeholder="请输入文档标题">
    </div>
    
    <div class="form-group">
      <label for="summary">内容概要</label>
      <textarea id="summary" placeholder="请输入文档概要内容"></textarea>
    </div>
    
    <div class="button-container">
      <button onclick="generate()">生成文档</button>
    </div>
    
    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>正在生成文档，请稍候...</p>
    </div>
    
    <div class="footer">
      <p>基于 Dify 大模型平台生成专业文档</p>
    </div>
  </div>

  <script>
    function generate() {
      const title = document.getElementById("title").value.trim();
      const summary = document.getElementById("summary").value.trim();
      const button = document.querySelector("button");
      const loading = document.getElementById("loading");

      // 验证输入
      if (!title || !summary) {
        alert("请输入标题和概要内容！");
        return;
      }

      // 显示加载状态
      button.disabled = true;
      button.textContent = "生成中...";
      loading.style.display = "block";

      // 发送请求
      fetch("/generate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({title: title, summary: summary})
      })
      .then(res => {
        if (!res.ok) {
          throw new Error("生成失败，请重试");
        }
        return res.blob();
      })
      .then(blob => {
        // 创建下载链接
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "智能文档.docx";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      })
      .catch(error => {
        console.error("错误：", error);
        alert("生成文档失败，请检查网络连接或稍后重试。");
      })
      .finally(() => {
        // 恢复按钮状态
        button.disabled = false;
        button.textContent = "生成文档";
        loading.style.display = "none";
      });
    }
    
    // 添加键盘快捷键支持
    document.addEventListener('keydown', function(event) {
      // Ctrl+Enter 或 Cmd+Enter 触发生成
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        generate();
      }
    });
  </script>
</body>
</html>
"""