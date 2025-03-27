from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
from playwright.sync_api import sync_playwright # pip install playwright + playwright install
from bs4 import BeautifulSoup
import json

# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36 EdgA/123.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.bing.com/",
}

sites = ['', 'toutiao.com', 'weibo.com', 'm.weibo.cn', 'news.qq.com']

@run_agent
def run(agent: MofaAgent):
    try:
        # 加载环境变量
        load_dotenv('.env.secret')
        client = OpenAI(
            api_key=os.getenv('LLM_API_KEY'),
            base_url=os.getenv('LLM_API_BASE')
        )
        
        # 接收用户输入
        user_input = agent.receive_parameter('query')

        # LLM 优化搜索关键词
        response = client.chat.completions.create(
            model=os.getenv('LLM_MODEL', 'generalv3.5'),
            messages=[
                {"role": "user", "content": "请你根据我给你的问题编辑一个搜索内容(30字以内)，使得搜索结果内容更详实，你只需要以纯文本的形式回答对应的搜索内容，我的问题是：{}".format(user_input)}
            ],
            stream=False
        )

        agent.send_output(
            agent_output_name='site_result',
            agent_result=f"正在搜索关键词：{response.choices[0].message.content}"
        )
        user_input = response.choices[0].message.content
        
        result_list = []

        # 使用 Playwright
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)  # headless=True 表示无头模式
            context = browser.new_context()
            page = context.new_page()

            for site in sites:
                # 构造 URL
                if site == '':
                    url = f"https://cn.bing.com/search?q={user_input}&FORM=BESBTB"
                else:
                    url = f"https://cn.bing.com/search?q={user_input}%20site:{site}"
                print(f"Fetching: {url}")

                # 打开页面
                page.goto(url)
                page.wait_for_timeout(3000)  # 等待 3 秒，确保页面加载完成

                # 获取页面内容
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # 提取搜索结果主内容
                for item in soup.find_all('li', class_='b_algo'):
                    try:
                        title = item.find('h2').text
                        description_tag = item.find('p')
                        description = description_tag.text if description_tag else "No description available"
                        link = item.find('a')['href']
                        result_list.append({'title': title, 'description': description, 'link': link})
                        agent.send_output(
                            agent_output_name='site_result',
                            agent_result=f"Title: {title}\nDescription: {description}\nLink: {link}"
                        )
                    except Exception as e:
                        print(f"An error occurred while extracting search results: {str(e)}")

            # 关闭浏览器
            browser.close()

        # 发送输出
        agent.send_output(
            agent_output_name='bing_result',
            agent_result=json.dumps(result_list, ensure_ascii=False, indent=4)  # 格式化
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        agent.send_output(
            agent_output_name='bing_result',
            agent_result=f"Error: {str(e)}"
        )

def main():
    agent = MofaAgent(agent_name='crisis-search-agent')
    run(agent=agent)

if __name__ == "__main__":
    main()