# 🤖 AI 简历生成系统

机器学习课程项目 —— 基于大语言模型的智能简历生成系统。

## 功能特点

- **AI 智能生成**：利用大语言模型（Claude / GPT）自动优化简历内容，包括：
  - 专业摘要生成
  - 工作经历量化改写（STAR 法则）
  - 技能分类整理
  - 项目描述优化
  - 自我评价润色
- **3 套精美模板**：经典双栏 / 现代卡片 / 极简 ATS 优化
- **PDF 导出**：一键生成 A4 排版 PDF，支持浏览器直接打印
- **多步骤表单**：6 步向导式填写，数据实时保存
- **无 API Key 也能用**：内置规则引擎 Fallback，不依赖外部 API 也能生成简历

## 技术栈

- **后端**：Python Flask + Session 管理
- **前端**：原生 HTML/CSS/JS，Jinja2 模板渲染
- **AI 引擎**：Anthropic Claude API / OpenAI GPT API / 规则引擎
- **PDF 生成**：WeasyPrint（可选）+ 浏览器打印

## 项目结构

```
简历/
├── app.py                    # Flask 入口，路由注册
├── config.py                 # 应用配置
├── requirements.txt          # Python 依赖
├── README.md                 # 本文档
│
├── ai_service/               # AI 服务层
│   ├── base.py               # LLM 客户端抽象基类
│   ├── claude_client.py      # Anthropic Claude API 实现
│   ├── openai_client.py      # OpenAI GPT API 实现
│   ├── fallback_client.py    # 规则引擎（无需 API Key）
│   └── prompts.py            # Prompt 模板库（5 组专项 Prompt）
│
├── resume/                   # 简历生成核心
│   ├── generator.py          # 生成编排器（逐 section 调用 AI）
│   ├── formatter.py          # LLM 输出解析与格式化
│   └── templates/            # 3 套简历 Jinja2 模板
│       ├── classic.html
│       ├── modern.html
│       └── compact.html
│
├── pdf_generator/
│   └── engine.py             # WeasyPrint PDF 渲染引擎
│
├── static/
│   ├── css/
│   │   ├── base.css          # 全局样式
│   │   ├── wizard.css        # 表单向导样式
│   │   ├── preview.css       # 预览页样式
│   │   └── templates/        # 简历模板 CSS
│   │       ├── classic.css
│   │       ├── modern.css
│   │       └── compact.css
│   └── js/
│       ├── api.js            # AJAX 通信
│       ├── wizard.js         # 表单向导逻辑
│       └── preview.js        # 预览页逻辑
│
├── templates/                # Flask 页面模板
│   ├── base.html             # 基础骨架
│   ├── index.html            # 首页
│   ├── form.html             # 表单向导
│   ├── preview.html          # 简历预览
│   ├── error.html            # 错误页
│   └── resume/               # 简历模板（运行时） ← resume/templates/*.html
│
├── utils/
│   ├── validators.py         # 输入验证
│   └── session_manager.py    # Session 管理
│
└── flask_session/            # Session 文件存储（运行时生成）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

核心依赖：
- `flask` — Web 框架
- `flask-session` — 服务器端 Session
- `cachelib` — Session 文件存储后端
- `python-dotenv` — 环境变量管理

可选依赖：
- `anthropic` — Claude API（推荐）
- `openai` — GPT API
- `weasyprint` — PDF 生成（需要额外安装 GTK3 运行时）

### 2. 配置 API Key（可选）

创建 `.env` 文件：
```env
# 可选：设置 API Key（也可以在表单第 6 步输入）
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
```

不配置 API Key 也可以使用，系统会自动启用规则引擎模式。

### 3. 启动应用

```bash
python app.py
```

打开浏览器访问：**http://127.0.0.1:5000**

### 4. 使用流程

1. 点击「开始创建简历」
2. 按 6 个步骤填写个人信息
3. 在第 6 步选择模板和 AI 引擎
4. 点击「生成简历」
5. 预览效果，切换模板
6. 下载 PDF 或直接打印

## ML 课程亮点

本项目展示了以下机器学习 / NLP 相关技术：

| 技术点 | 说明 |
|--------|------|
| **Prompt Engineering** | 5 组精心设计的 Prompt 模板，针对不同简历 section 进行了温度调优和输出格式控制 |
| **LLM 应用开发** | 使用大语言模型进行文本生成、润色、摘要、分类等多种 NLP 任务 |
| **模型抽象** | Provider 无关的接口设计，支持无缝切换 Claude / GPT / 规则引擎 |
| **Baseline 对比** | 规则引擎 Fallback 作为非 ML 基准，直观展示 LLM 的价值提升 |
| **结构化输出** | JSON 格式控制 + 鲁棒解析，处理 LLM 输出不稳定的问题 |
| **错误处理** | API 调用失败自动降级，保证系统在任何情况下都能正常工作 |

## 三套模板对比

| 模板 | 布局风格 | 适用场景 |
|------|---------|---------|
| **Modern 现代** | 单栏全宽，青色主题，卡片式设计 | 科技互联网、设计创意、创业公司 |
| **Classic 经典** | 双栏深蓝侧边栏，传统专业风格 | 金融银行、政府机关、教育培训 |
| **Compact 极简** | 单栏纯文字，最大信息密度 | 大厂海投、ATS 自动筛选系统 |

## API 路由说明

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/form` | GET | 简历表单 |
| `/api/save-step` | POST | 保存表单步骤数据 |
| `/api/generate` | POST | 生成完整简历 |
| `/api/generate-section/<section>` | POST | 生成单个栏目 |
| `/api/validate-key` | POST | 验证 API Key |
| `/api/status` | GET | 获取生成状态 |
| `/preview/<template>` | GET | 预览指定模板 |
| `/download/<template>/pdf` | GET | 下载 PDF |

## 注意事项

1. **API Key 安全**：API Key 仅保存在当前会话中，服务器重启后丢失
2. **PDF 生成**：推荐使用浏览器打印功能（Ctrl+P）作为首选方案
3. **数据隐私**：所有数据仅存储在本地 Session 文件中，不会外传
4. **WeasyPrint**：如需服务端 PDF 生成，Windows 用户需安装 GTK3 运行时

## 许可

本项目为机器学习课程作业，仅供学习参考。
