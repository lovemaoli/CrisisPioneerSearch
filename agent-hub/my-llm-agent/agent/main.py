from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import os
from dotenv import load_dotenv

@run_agent
def run(agent: MofaAgent):
    try:
        # 加载环境变量
        load_dotenv('.env.secret')
        
        # 初始化 OpenAI 客户端
        client = OpenAI(
            api_key=os.getenv('LLM_API_KEY'),
            base_url=os.getenv('LLM_API_BASE')
        )
        
        # 接收用户输入
        user_input = agent.receive_parameter('query')
        
        # 调用 LLM
        response = client.chat.completions.create(
            model=os.getenv('LLM_MODEL', 'generalv3.5'),
            messages=[
                {"role": "system", "content": "你是一个实时应急搜索引擎，能够整合多源数据，包括政府官方灾害预警、实时社交媒体信息、新闻、气象大模型的内容，最后输出给用户。请注意，请你以纯文本形式回答问题，不要使用markdown、html等格式。"},
                {"role": "user", "content": user_input}
            ],
            stream=False
        )
        
        # 发送输出
        agent.send_output(
            agent_output_name='llm_result',
            agent_result=response.choices[0].message.content
        )
        
    except Exception as e:
        agent.logger.error(f"Error: {str(e)}")
        agent.send_output(
            agent_output_name='llm_result',
            agent_result=f"Error: {str(e)}"
        )

def main():
    agent = MofaAgent(agent_name='my-llm-agent')
    run(agent=agent)

if __name__ == "__main__":
    main()