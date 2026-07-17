# shift-scheduler

57车间排班表 - 一个简单的排班管理Web应用

## 本地运行
```bash
pip install -r requirements.txt
python app.py
```

## 部署到 Render
1. 连接 GitHub 仓库
2. 新建 Web Service
3. 选 Python 环境
4. Start Command: `gunicorn app:app`
