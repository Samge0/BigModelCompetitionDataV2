#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-30 15:30
# describe：使用dify构建的关系提取应用（底座为llama3.1:8b）对文本进行关系提取

import json
import requests
import configs


class ChatMessageAPI:
    def __init__(self, base_url, api_key):
        """
        Initialize the API client with the base URL and API key.

        :param base_url: The base URL of the API endpoint.
        :param api_key: The API key for authorization.
        """
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def send_chat_message(self, query, user, files=None, response_mode='blocking', conversation_id=""):
        """
        Send a chat message to the API.

        :param query: The query to be sent.
        :param user: The user identifier.
        :param files: A list of files to be included in the request (default: None).
        :param response_mode: The mode of the response (default: 'blocking'). blocking or streaming
        :param conversation_id: The conversation ID (default: empty string).
        :return: The response from the API.
        """
        data = {
            "inputs": {},
            "query": query,
            "response_mode": response_mode,
            "conversation_id": conversation_id,
            "user": user
        }

        try:
            # Make the POST request
            response = requests.post(self.base_url, headers=self.headers, json=data, proxies={"http": None, "https": None})
            # Handle the response
            if response.status_code == 200:
                answer = response.json().get('answer')
                if "```" in answer:
                    answer = answer.replace("\n", " ").replace("```json", "").replace("```", "")
                return json.loads(answer)
            else:
                print(f"Request failed with status code: {response.status_code}")
                return None
        except:
            return None


api_client = None


def get_api_client(api_key=None):
    global api_client
    if not api_client:
        api_client = ChatMessageAPI(
            base_url=f'{configs.API_URL}/chat-messages',
            api_key=api_key or configs.AUTHORIZATION
        )
    return api_client


if __name__ == "__main__":

    # Send a chat message
    result = get_api_client().send_chat_message(
        query="""{
"question": "速率限制指南-用量级别等级",
"answer": "当前我们基于用户的月度 API 调用消耗金额情况将速率控制分为6种等级。\n消耗金额选取逻辑：我们会选取用户当前月份1号～t-1日的调用 API 推理消耗总金额和用户上个月的 API 调用消耗总金额做比较，取更高金额作为用户当前的 API 消耗金额。\n特别的，若您从未曾付费充值/购买过资源包，则会归为免费级别。\n用量级别|资质\n免费|api调用消耗0元-50元/每月（不含）\n用量级别1|api调用消耗50元-500元/每月（不含）\n用量级别2|api调用消耗500元-5000元/每月（不含）\n用量级别3|api调用消耗5000元-10000元/每月（不含）\n用量级别4|api调用消耗10000元-30000元/每月（不含）\n用量级别5|api调用消耗30000元以上/每月\n选择级别，查看各模型在对应级别下的限制"
}""",
        user=configs.USER_NAME
    )
    print(result)
    