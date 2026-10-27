项目描述：针对自研 Flask 电商系统迭代快、人工回归低效、易漏测等问题，独立搭建单元 + 接口 + UI E2E 三层自动化测试体系，覆盖用户、商品、购物车、订单核心业务，落地 93 条自动化用例，实现版本迭代常态化自动化回归。
· 负责模块：
1. 测试框架：基于 pytest 封装全局固件，统一环境配置、请求调用、数据清理与通用断言逻辑，代码复用率提升 70%、脚本开发效率提升 60%，统一项目测试规范。
2. 单元测试：参数化覆盖各类边界与异常场景，依托 pytest-cov 校验代码质量，核心业务代码覆盖率超 95%，从源头拦截底层逻辑缺陷。
3. 接口自动化：独立开发 72 条核心接口用例，支持业务接口关联串联与多层断言、并行执行，把 2 小时人工回归压缩至 5 分钟，测试迭代效率提升 95%。
4. UI 自动化：采用 Selenium + POM 封装浏览器兼容、元素等待、弹窗处理等通用能力，落地 21 条全链路 E2E 用例，完整覆盖用户下单全流程，实现无人值守测试。
5. 工程化与闭环：规范项目依赖、Git 迭代流程与全套测试文档，建立分层回归测试闭环，精准定位并跟进修复缺陷，使版本漏测率降低 80%。
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

