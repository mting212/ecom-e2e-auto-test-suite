## 项目结构

```
test_intern/
├── register.py            ← 被测代码：注册校验逻辑
├── api_server.py          ← 被测代码：Flask 注册 API
├── test_register.py       ← 单元测试：parametrize + fixture + 异常测试
├── test_api.py            ← 接口基础：requests 打 httpbin 靶场
├── test_api_register.py   ← 接口测试：对 api_server 发真实请求
├── conftest.py            ← 共享 fixture（base_url, api_client, 数据清理）
└── test_ui.py             ← Selenium UI 自动化（Day 12+）
```

## 快速开始

```bash
# 安装依赖
pip install pytest requests flask selenium webdriver-manager pytest-cov

# 单元测试
pytest test_register.py -v

# 接口测试（需两个终端）
python api_server.py                  # 终端1：启动 Flask
pytest test_api_register.py -v        # 终端2：跑测试

# 覆盖率
pytest test_register.py --cov=register --cov-report=term
```

