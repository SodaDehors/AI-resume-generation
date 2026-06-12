---
title: 从零搭建 AI 简历生成系统——Prompt Engineering × LLM 实战
date: 2026-06-12
categories:
  - 项目
  - AI
  - 全栈
tags:
  - Flask
  - LLM
  - Prompt Engineering
  - DeepSeek
  - 部署
description: 机器学习课程项目：基于大语言模型的智能简历生成系统。支持 3 套模板、多 AI 引擎切换、规则引擎 Fallback，已部署至阿里云轻量服务器。
slug: cong-ling-da-jian-ai-jian-li-sheng-cheng-xi-tong----prompt-engineering-x-llm-shi-zhan
cover: ""
halo:
  site: http://47.99.135.194:8090
  name: afde574a-1c1d-4979-9215-280f79b69b83
  publish: false
---

## 为什么做这个项目

写简历大概是每个求职者都逃不掉的事。你有没有这种感觉——明明做了很多事，落到纸上就是"负责 XX 工作"八个字，干巴巴的。HR 看 5 秒就扔一边了。

恰逢机器学习课程要求交一个大作业😀，我就想：**能不能让 LLM 来帮我写简历？** 不是简单地把文字丢给 ChatGPT 那种，而是做一个真正能**引导用户填写信息 → AI 分模块优化 → 多模板渲染输出**的完整系统。

## 最终效果

> 🔗 在线体验：[airesume.sodadengsl.cn](http://airesume.sodadengsl.cn)
> 📦 GitHub：[github.com/SodaDehors/AI-resume-generation](https://github.com/SodaDehors/AI-resume-generation)

### 核心功能

- 🤖 **AI 智能生成**：利用 LLM 对简历的 5 个模块分别优化——专业摘要、工作经历（STAR 法则量化改写）、技能分类整理、项目描述优化、自我评价润色
- 🎨 **3 套精美模板**：经典双栏 / 现代卡片 / 极简 ATS 优化，支持 AJAX 即时切换
- 📄 **PDF 导出**：WeasyPrint + 浏览器打印双方案
- 🔌 **多 AI 引擎**：支持 Claude / OpenAI / DeepSeek，Provider 无关接口设计
- 🚫 **无 API Key 也能用**：内置规则引擎 Fallback，中文关键词检测 + 模板生成
- 📝 **6 步向导式表单**：分步填写，数据实时保存，支持取消生成

---

## 技术架构

```
┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│  用户浏览器    │────▶│  Nginx :80   │────▶│  Gunicorn   │
│              │◀────│              │◀────│  :8000      │
└──────────────┘     └──────────────┘     └──────┬──────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                     Flask App                            │
                    │  ┌───────────┐  ┌───────────┐  ┌───────────────────┐    │
                    │  │ AI Service │  │  Resume    │  │  PDF Generator   │    │
                    │  │  Layer     │  │  Generator │  │  (WeasyPrint)    │    │
                    │  └─────┬─────┘  └───────────┘  └───────────────────┘    │
                    │        │                                                  │
                    │  ┌─────┴──────────────────────────┐                      │
                    │  │ Claude │ OpenAI │ DeepSeek │ FB │  ← Provider 抽象    │
                    │  └─────────────────────────────────┘                      │
                    └──────────────────────────────────────────────────────────┘
```

**后端**：Python Flask + Flask-Session（服务端 Session） + Gunicorn
**前端**：原生 HTML/CSS/JS + Jinja2 模板，零框架依赖
**AI 引擎**：Anthropic Claude / OpenAI GPT / DeepSeek（OpenAI 兼容协议）
**部署**：阿里云轻量 2C2G + Nginx 反向代理

---

## 有意思的技术点

### 5 组专项 Prompt

AI 写得好的前提是 Prompt 设计到位。我把系统提示词拆成了 5 个专项 Sub-Prompt，每个针对不同简历模块做了温度调优：

| 模块 | 温度 | 设计思路 |
|------|------|---------|
| 个人摘要 | 0.7 | 需要一定创造性，突出职业亮点 |
| 工作经历 | 0.3 | 低温度保证 STAR 法则格式严格，量化数据准确 |
| 技能分类 | 0.2 | 纯粹的归类任务，不需要发散 |
| 项目描述 | 0.5 | 平衡技术深度与可读性 |
| 自我评价 | 0.6 | 在专业性和真诚感之间取中间值 |

关键是在 System Prompt 里植入了**角色设定**：

```
你是一位资深职业简历撰写专家，拥有10年以上HR和猎头经验。
你精通ATS优化，擅长将普通工作描述转化为量化的成就有力陈述。
所有输出必须是有效的JSON格式。
```

这比简单说"帮我写简历"效果好太多了——LLM 会自己代入 HR 的视角来写。

### 鲁棒的 JSON 解析

LLM 输出 JSON 有时候不老实——换行、加注释、套 markdown 代码块、尾随逗号……各种幺蛾子。写了一个 `extract_json()` 函数多层兜底：

```python
def extract_json(text: str) -> dict:
    # 1. 直接解析
    # 2. 提取 ```json ... ``` 中的内容
    # 3. 提取第一个 { 到最后一个 } 之间的子串
    # 4. 修复常见问题：尾随逗号、数组尾随逗号
    # 5. 全失败返回 {}
```

### Provider 抽象

接口设计层面，所有 LLM 客户端实现同一个抽象基类：

```python
class BaseLLMClient(ABC):
    def generate(self, system_prompt, user_prompt,
                 temperature=0.4, max_tokens=2000) -> str: ...
    def is_available(self) -> bool: ...
```

DeepSeek 用 OpenAI 兼容协议，所以 `DeepSeekClient` 直接复用 OpenAI SDK，只改 `base_url`：

```python
class DeepSeekClient(BaseLLMClient):
    BASE_URL = 'https://api.deepseek.com'
    def _get_client(self):
        return OpenAI(api_key=self.api_key, base_url=self.BASE_URL)
```

这种设计让切换 AI 引擎只需改一行配置，不需要动业务代码。

### 规则引擎 Fallback 作为 Baseline

为了体现 ML 方法的价值，系统内置了一个不依赖 LLM 的纯规则引擎。比如技能分类：

```python
# 用关键词匹配做分类
if any(kw in skill_name for kw in ['Python', 'React', 'Docker']):
    tech_skills.append(skill)
elif any(kw in skill_name for kw in ['英语', '日语']):
    lang_skills.append(skill)
```

这个 Fallback 的效果虽然远不如 LLM，但有两个意义：一是保证了「无 API Key 也能用」的体验底线，二是作为非 ML 基准，直观展示 LLM 提升的价值。

---

## 部署踩坑记录

部署到阿里云轻量服务器 2 核 2G 时遇到不少问题。

### 怎么塞进已经跑着 2 个项目的小机器

服务器上本来有 Halo 博客（Java, ~430MB）和 weekend-planner 后台（Java, ~280MB），加上宝塔面板，1.6G 内存只剩 274MB 可用。

**解决方案**：
1. 把 weekend-planner 的 JVM 堆上限从 `-Xmx1024M` 降到 `-Xmx384M`，释放 ~150MB
2. Gunicorn 从 2 worker 降到 **1 worker + 2 threads**，省 60MB
3. 跳过 WeasyPrint 的 GTK3 依赖（300MB+ 磁盘），PDF 导出用浏览器打印兜底

最终 Flask 应用只占 ~80MB，整机可用内存维持在 400MB 左右。

### Flask-Session 不生效导致 Cookie 溢出

生成后跳转失败是一个隐蔽的 bug：Flask 默认用 Cookie 存 session，4KB 上限。AI 生成的大段简历文字直接把 cookie 撑爆了。配置里写了 `SESSION_TYPE = 'filesystem'` 但 `app.py` 忘了初始化 `Session(app)`。

```python
# 少写了这一行！
from flask_session import Session
Session(app)  # 这句话救了命
```

### `@property` 在 Flask Config 上是坑

`ProductionConfig.SESSION_FILE_DIR` 用了 `@property`，cachelib 拿到的是 property 对象而不是字符串，直接报 `TypeError`。改成 `os.getenv` 计算出的普通字符串就好了。

---

## 总结与后续计划

这个项目从 Prompt 设计、LLM 调用、前端交互到生产部署全栈独立完成。收获最大的是——

1. **Prompt Engineering 不是玄学**：角色设定 + 结构化约束 + 温度调优的组合拳行之有效
2. **生产部署要考虑的远比开发多**：内存优化、Session 存储、防火墙、反向代理超时……
3. **小机器也能跑多个服务**：1.6G 内存跑 3 个项目靠的是精细的资源配置

后续打算做的事：
- [ ] 生成改为异步 + 前端轮询进度（现在有进度条），支持取消
- [ ] 多条工作经历并行调用 LLM，生成速度翻倍
- [ ] 加 Token 消耗统计，让用户了解每次生成花了多少钱
- [ ] 单元测试覆盖核心模块

---

> 📦 项目开源在 [GitHub](https://github.com/SodaDehors/AI-resume-generation)，欢迎 Star ⭐
> 🖥 在线地址：[airesume.sodadengsl.cn](http://airesume.sodadengsl.cn)
>
> 如果你也想为期末作业做一个 LLM 应用，欢迎参考代码结构和 Prompt 设计。
