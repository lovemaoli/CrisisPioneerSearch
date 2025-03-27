from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import json

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
        result_list = json.loads(agent.receive_parameter('result_list'))

        agent.send_output(
            agent_output_name='llm_result',
            agent_result="我正在进一步整理数据，请稍等..."
        )

        # link 对 llm 没有意义
        for i in range(len(result_list)):
            result_list[i].pop('link')
        
        # llm 结合用户提问和搜索到的网页结果，回答用户的问题
        response = client.chat.completions.create(
            model=os.getenv('LLM_MODEL', 'generalv3.5'),
            messages=[
                {"role": "system", "content": "你是一个实时紧急搜索引擎，能够整合多源数据，目标定位为在官方渠道和社交媒体上搜寻某个热点话题"
                                                "(可以是气象灾害、应急警报等), 由agent整合各渠道信息并反馈给用户, 最后输出给用户。"
                                                "请注意, 请你以纯文本形式回答问题, 不要使用markdown、html等格式。"},
                # {"role": "user", "content": user_input},
                # {"role": "assistant", "content": first_answer},
                {"role": "user", "content": "我的问题是{},请你根据搜索引擎得到的内容{}，进一步补充回答我的问题；请你在回答问题以'根据急先锋搜索引擎搜索的结果，'开头,以纯文本形式输出, 不要输出*号".format(user_input, json.dumps(result_list, ensure_ascii=False))},
            ],
            stream=False
        )

        # 发送输出
        agent.send_output(
            agent_output_name='final_result',
            agent_result=response.choices[0].message.content
        )
                
    except Exception as e:
        print(f"Error: {str(e)}")
        agent.send_output(
            agent_output_name='final_result',
            agent_result=f"Error: {str(e)}"
        )

def main():
    agent = MofaAgent(agent_name='crisis-think-agent')
    run(agent=agent)

if __name__ == "__main__":
    main()