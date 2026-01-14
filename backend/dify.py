import json

import requests


def dify_request(question: str, stream: bool = False):
    """
    最基本的 Dify 请求封装
    传入一个问题，返回 Dify 的回答

    :param question: 用户的问题
    :param stream: 是否使用流式响应
    :return: Dify 的回答, 其中当为流式输出时会不停输出回答(待和前端配合使用)
    """
    API_KEY = "app-1IwfITLttFa7sNpXP26AN3YN"
    URL = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    if stream:
        print("使用流式无记忆模式响应输出中...")
        print(f"问题: {question}")
        payload = {
            "inputs": {
                "question": question
            },
            "response_mode": "streaming",
            "user": "human-user"
        }
        response = requests.post(URL, headers=headers, json=payload, stream=True)
        full_answer = ""

        for line in response.iter_lines():
            if not line:
                continue
            if not line.startswith(b"data: "):
                continue
            data = json.loads(line[6:].decode("utf-8"))
            event = data.get("event")

            # 输出流式内容
            if event == "text_chunk":
                chunk = data["data"]["text"]
                full_answer += chunk

                print(chunk, end="", flush=True)
            elif event == "error":
                raise RuntimeError(data)

        return full_answer

    else:
        print("使用非流式流式无记忆模式响应输出中...")
        print(f"问题: {question}")
        payload = {
            "inputs": {
                "question": question
            },
            "response_mode": "blocking",
            "user": "human-user"
        }
        response = requests.post(URL, json=payload, headers=headers)
        result = response.json()

        answer = result["data"]["outputs"].get("answer")
        return answer


def dify_chatflow_request(question: str, user: str, conversation_id: str = "", stream: bool = False):
    """
    Dify 的 Chatflow 请求封装, 使用 conversation_id 进行多轮对话并存储记忆
    传入一个问题，返回 Dify 的回答

    :param question: 用户的问题
    :param user: 用户唯一标识
    :param conversation_id: 对话 ID，可选
    :param stream: 是否使用流式响应
    :return: Dify 的回答和对话 ID的元组, 其中当为流式输出时会不停输出回答(待和前端配合使用)
    """
    API_KEY = "app-6nsFy8O8xGGivOFkT6kZJvzt"
    URL = "https://api.dify.ai/v1/chat-messages"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    if stream:
        print("使用流式响应输出中...")
        print(f"问题: {question}")
        print(f"用户: {user}")
        if conversation_id != "":
            print(f"对话 ID: {conversation_id}")
        else:
            print("无对话 ID (新对话)")

        payload = {
            "inputs": {},
            "query": question,
            "response_mode": "streaming",
            "user": user,
            "conversation_id": conversation_id
        }
        response = requests.post(URL, headers=headers, json=payload, stream=True)

        full_answer = ""
        last_conversation_id = conversation_id

        for line in response.iter_lines():
            if not line:
                continue
            if line.startswith(b'data: '):
                data = json.loads(line[6:])
                event = data.get("event")

                # 输出流式内容
                if event == "text_chunk":
                    chunk = data.get("data", "").get("text", "")
                    full_answer += chunk

                    print(chunk, end="", flush=True)
                    last_conversation_id = data.get("conversation_id", last_conversation_id)
                elif event == "workflow_finished":
                    break

        return full_answer, last_conversation_id
    else:
        if conversation_id != "":
            print("使用非流式响应输出中...")
            print(f"补充对话: {question}")
            print(f"用户: {user}")
            print(f"对话 ID: {conversation_id}")
        else:
            print("使用非流式响应输出中...")
            print(f"问题: {question}")
            print(f"用户: {user}")
            print("对话 ID: null (新对话)")

        payload = {
            "inputs": {},
            "query": question,
            "response_mode": "blocking",
            "user": user,
            "conversation_id": conversation_id
        }
        response = requests.post(URL, headers=headers, json=payload)
        result = response.json()

        answer = result["answer"]
        conversation_id = result["conversation_id"]

        return answer, conversation_id


# 测试用
if __name__ == '__main__':
    dify_request("番茄鸡蛋汤的做法", stream=True)