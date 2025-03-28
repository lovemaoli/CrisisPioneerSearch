# 急先锋搜索

## 设计理念

一个AI驱动的搜索引擎，以MoFA开发框架搭建，目标定位为在官方渠道和社交媒体上搜寻某个热点话题（可以是气象灾害、应急警报等），由agent整合各渠道信息并反馈给用户。

## 技术架构图

MoFA 框架图

<img src="https://github.com/RelevantStudy/mofasearch/blob/main/hackathons/docs/images/image-20250310010710778.png" alt="image-20250310010710778" style="zoom:67%;" />

## 运行指南

### 1 Python 环境

```bash
# 安装 UV 包管理器 加快mofa安装
pip install uv
```

### **注意**: 
- 本地python环境要纯净，不要多个python版本，否则容易导致Dora-rs运行环境和Mofa安装环境的冲突。
- 如果你的环境使用的是Anaconda / Miniconda，务必将Mofa安装到`Base`环境下，以保证Dora运行环境和Mofa环境的一致。
- 要求python环境 >= 3.10。

### 2 Rust 环境
```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Dora 运行时
cargo install dora-cli

# 验证安装
rustc --version
cargo --version
dora --version
```

### 3 安装 MoFa

```bash
# 克隆仓库
git clone https://github.com/moxin-org/mofa.git
cd mofa/python

# 安装依赖
uv pip install -e .
pip install -e . 
```

### 4 导入agent

将本仓库的 agent-hub 与 example 导入 MoFA 的对应文件夹

### 4.2 配置环境变量

创建 `.env.secret` 文件(crisis_pioneer_search.yml.yml目录同级进行创建)：
```plaintext
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://api.openai.com/v1  # 或其他API地址
LLM_MODEL=gpt-3.5-turbo  # 或其他模型名称
```
注：写者使用的是星火大模型

### 5 启动数据流
```bash
cd  /mofa/python/examples/crisis_pioneer_search

# 启动 Dora 服务
dora up

# 构建并运行数据流
dora build crisis_pioneer_search.yml
dora start crisis_pioneer_search.yml
```

### 6 测试交互
```bash
# 在另一个终端运行输入节点
terminal-input

# 输入测试数据
> hello
```

### 7 **运行效果**

```
root@root hello_world % terminal-input                                           
 Send You Task :  你好
-------------llm_result---------------    
……
```

## 架构设计
### 实现Agent逻辑

编辑 `xxx.py`：
```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import os
from dotenv import load_dotenv

@run_agent
def run(agent: MofaAgent):
    try:
        ……

def main():
    agent = MofaAgent(agent_name='my-agent')
    run(agent=agent)

if __name__ == "__main__":
    main()
```

### 数据流配置

创建 `dataflow.yml`：
```yaml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs: data
    inputs:
      agent_response: my-llm-agent/llm_result


```

### 关键代码说明

1. **使用装饰器**
   - 使用 `@run_agent` 装饰器简化代码结构
   - 自动处理循环和异常

2. **简单的输入输出**
   - 接收单个输入参数 `query`
   - 返回单个输出结果 `llm_result`

3. **错误处理**
   - 使用 try-except 捕获异常
   - 记录错误日志
   - 返回错误信息给用户

### 如何自定义

1. **修改系统提示词**
```python
messages=[
    {"role": "system", "content": "你的自定义系统提示词"},
    {"role": "user", "content": user_input}
]
```

2. **更换LLM提供商**
   - 修改 `.env.secret` 中的 API 配置
   - 根据需要调整模型参数

### 注意事项

1. 确保 `.env.secret` 已添加到 `.gitignore`
2. API密钥要妥善保管
3. 保持代码结构简单清晰

### agent处理流程详解
1. 用户通过 terminal-input 输入数据
2. terminal-input 将数据发送给 agent
3. agent 处理数据并返回结果
4. 结果返回给 terminal-input 显示
5. 由于 IS_DATAFLOW_END=true，流程结束并重新开始

### 日志文件位置
- `logs/xxx-agent.txt`: 智能体运行日志
- `logs/dora-coordinator.txt`: 协调器日志
- `logs/dora-daemon.txt`: 守护进程日志

### 项目结构
```
my-new-agent/
├── agent/
│   ├── configs/
│   │   └── agent.yml       # 配置文件
│   ├── main.py             # 主程序
│   └── __init__.py
├── tests/
│   └── test_main.py        # 测试代码
├── pyproject.toml          # 依赖配置
└── README.md               # 项目文档
```
