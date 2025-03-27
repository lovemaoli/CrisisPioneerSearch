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

        agent.send_output(
            agent_output_name='llm_result',
            agent_result="我正在搜寻中，请稍等..."
        )

        # LLM 回答判断用户是需要帮助还是单纯的提问，如果是提问则回答是，如果是需要帮助则回答否
        response = client.chat.completions.create(
            model=os.getenv('LLM_MODEL', 'generalv3.5'),
            messages=[
                {"role": "system", "content": "你是一个判断高手，能够判断用户是需要困难的帮助还是单纯的提问。请注意，请你以纯文本形式回答问题，不要使用markdown、html等格式。"},
                {"role": "user", "content": "请你根据我给你的问题判断我是需要帮助还是单纯的提问，如果是提问请回答是，如果是需要帮助请回答否，请注意你只需要回答一个字，是或否，我的问题是：{}".format(user_input)}
            ],
            stream=False
        )

        # 判断 LLM 的回答是否有否字
        if '否' not in response.choices[0].message.content:
            # 调用 LLM 回答问题
            print('LLM search')
            response = client.chat.completions.create(
                model=os.getenv('LLM_MODEL', 'generalv3.5'),
                messages=[
                    {"role": "system", "content": "你是一个实时紧急搜索引擎，能够整合多源数据，目标定位为在官方渠道和社交媒体上搜寻某个热点话题（可以是气象灾害、应急警报等），由agent整合各渠道信息并反馈给用户，最后输出给用户。请注意，请你以纯文本形式回答问题，不要使用markdown、html等格式。"},
                    {"role": "user", "content": user_input+"，以纯文本形式回答问题，不要输出*号"}
                ],
                stream=False
            )
            
            # 发送输出
            agent.send_output(
                agent_output_name='llm_result',
                agent_result=response.choices[0].message.content
            )
        else:
            print('LLM solve')
            response = client.chat.completions.create(
                model=os.getenv('LLM_MODEL', 'generalv3.5'),
                messages=[
                    {"role": "system", "content": "你是一个实时紧急搜索引擎，你能够了解用户需要的帮助，目标定位为利用已有的知识，分析用户的困难，并给出合理的解决方案，最后输出给用户。请注意，请你以纯文本形式回答问题，不要使用markdown、html等格式，给予用户解决方案时按步骤给出。"},
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
        print(f"Error: {str(e)}")
        agent.send_output(
            agent_output_name='llm_result',
            agent_result=f"Error: {str(e)}"
        )

def main():
    agent = MofaAgent(agent_name='crisis-help-agent')
    run(agent=agent)

if __name__ == "__main__":
    main()