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
            data = json.loads(line[6:])
            event = data.get("event")

            # 输出流式内容
            if event == "text_chunk":
                chunk = data["data"]["text"]
                full_answer += chunk

                print(chunk, end="", flush=True)
            elif event == "error":
                raise RuntimeError(data)

        # 去掉 <think> 推理部分
        after_think = full_answer.split("</think>")[-1].strip()

        # 去掉 ```json 包裹
        if after_think.startswith("```"):
            after_think = after_think.split("```", 1)[-1].strip()
        if after_think.endswith("```"):
            after_think = after_think.rsplit("```", 1)[0].strip()

        # 解析 JSON
        data = json.loads(after_think)
        return data

    else:
        print("使用非流式无记忆模式响应输出中...")
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

        answer = result["data"]["outputs"]["text"]

        # 去掉 <think> 推理部分
        after_think = answer.split("</think>")[-1].strip()

        # 去掉 ```json 包裹
        if after_think.startswith("```"):
            after_think = after_think.split("```", 1)[-1].strip()
        if after_think.endswith("```"):
            after_think = after_think.rsplit("```", 1)[0].strip()

        # 解析 JSON
        data = json.loads(after_think)
        return data


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
                if event == "message":
                    chunk = data.get("answer", "")
                    full_answer += chunk

                    print(chunk, end="", flush=True)
                    last_conversation_id = data.get("conversation_id", last_conversation_id)
                elif event == "workflow_finished":
                    break

        # 去掉 <think> 推理部分
        after_think = full_answer.split("</think>")[-1].strip()

        # 去掉 ```json 包裹
        if after_think.startswith("```"):
            after_think = after_think.split("```", 1)[-1].strip()
        if after_think.endswith("```"):
            after_think = after_think.rsplit("```", 1)[0].strip()

        # 解析 JSON
        data = json.loads(after_think)

        return data, last_conversation_id

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

        answer = result.get("answer", "")
        conversation_id = result["conversation_id"]

        # 去掉 <think> 推理部分
        after_think = answer.split("</think>")[-1].strip()

        # 去掉 ```json 包裹
        if after_think.startswith("```"):
            after_think = after_think.split("```", 1)[-1].strip()
        if after_think.endswith("```"):
            after_think = after_think.rsplit("```", 1)[0].strip()

        # 解析 JSON
        data = json.loads(after_think)

        return data, conversation_id


def dify_request_stream_generator(question: str):
    """
    与 dify_request(..., stream=True) 行为类似，但会将每个文本片段 yield 出来，
    最后输出一条以 __RESULT__ 开头的字符串，后面紧跟解析后的 JSON（字符串形式），
    便于前端在接收完流后拿到结构化数据用于生成文档或下载。
    """
    API_KEY = "app-1IwfITLttFa7sNpXP26AN3YN"
    URL = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {
            "question": question
        },
        "response_mode": "streaming",
        "user": "human-user"
    }

    response = requests.post(URL, headers=headers, json=payload, stream=True)

    full_answer = ""

    try:
        for line in response.iter_lines():
            if not line:
                continue
            if not line.startswith(b"data: "):
                continue
            data = json.loads(line[6:])
            event = data.get("event")

            if event == "text_chunk":
                chunk = data["data"].get("text", "")
                full_answer += chunk
                # 直接将文本片段 yield 给调用方（HTTP 响应流）
                yield chunk
            elif event == "error":
                # 将错误信息以 JSON 字符串形式 yield 出来并结束
                yield json.dumps({"error": data})
                return
    except Exception as e:
        yield json.dumps({"error": str(e)})
        return

    # 处理最终的完整回答，去掉 <think> 和 ```json 包裹并解析为 JSON
    after_think = full_answer.split("</think>")[-1].strip()

    if after_think.startswith("```"):
        after_think = after_think.split("```", 1)[-1].strip()
    if after_think.endswith("```"):
        after_think = after_think.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(after_think)
    except Exception:
        # 如果解析失败，把原始文本作为结果返回（不中断前端显示）
        parsed = {"text": after_think}

    # 最后将解析后的 JSON 作为一个单独的标记发送，前端可检测到这个前缀并处理为最终结构化结果
    yield "__RESULT__" + json.dumps(parsed, ensure_ascii=False)


def dify_chatflow_stream_generator(question: str,
                                   user: str,
                                   conversation_id: str = "",
                                   docx_create: bool = False,
                                   style: str = "不指定",
                                   file_num: int = None,
                                   menu: str = None,
                                   outline: str = None,
                                   example: str = None,
                                   relevant_documents: list = None,
                                   ):
    """
    适用于支持内存的 chatflow API（聊天消息）的流式生成器。
    随着文本块的到来，它会逐步生成（纯文本）。
    流结束后，它会生成一个以 '__RESULT__' 开头的标记字符串，后跟一个 JSON 字符串（ensure_ascii=False），其中包含解析后的 JSON 结果和最终的 conversation_id，
    例如：__RESULT__{"result": {...}, "conversation_id": "..."}

    如果发生错误，会生成类似 '{"error": ...}' 的 JSON 字符串。

    :param relevant_documents: 上传的文档
    :param question: 用户的问题
    :param user: 用户唯一标识
    :param conversation_id: 对话 ID，可选
    :param docx_create: 是否创建 docx 文档（必选）
    :param style: 文档风格（可选）
    :param file_num: 文件字数
    :param menu: 目录结构
    :param outline: 大纲
    :param example: 示例
    :return: 生成器，逐步 yield 文本块，最后 yield 结果
    """

    API_KEY = "app-6nsFy8O8xGGivOFkT6kZJvzt"
    URL = "https://api.dify.ai/v1/chat-messages"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    inputs = {
        "docx_create": docx_create,
        "style": style,
        "menu": menu or "",
        "outline": outline or "",
        "example": example or "",
        "file_num": file_num if file_num is not None else 1000
    }
    if relevant_documents is not None:
        inputs["relevant_documents"] = relevant_documents
    else:
        inputs["relevant_documents"] = []
    payload = {
        "inputs": inputs,
        "query": question,
        "response_mode": "streaming",
        "user": user,
        "conversation_id": conversation_id
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, stream=True)
    except Exception as e:
        yield json.dumps({"error": str(e)})
        return

    full_answer = ""
    last_conversation_id = conversation_id

    try:
        for line in response.iter_lines():
            # print(line)
            if not line:
                continue
            if not line.startswith(b"data: "):
                continue
            try:
                data = json.loads(line[6:])
            except Exception:
                # skip unparsable lines
                continue
            event = data.get("event")

            if event == "message":
                # server may send incremental answers under 'answer'
                chunk = data.get("answer", "")
                full_answer += chunk
                # yield raw text chunk for frontend streaming display
                yield chunk
                # capture conversation id updates from server
                last_conversation_id = data.get("conversation_id", last_conversation_id)
            elif event == "workflow_finished":
                # finished streaming
                break
            elif event == "error":
                # yield error payload as JSON string and stop
                yield json.dumps({"error": data})
                return
    except Exception as e:
        yield json.dumps({"error": str(e)})
        return

    # Post-process the accumulated full_answer similar to other helpers
    after_think = full_answer.split("</think>")[-1].strip()

    # strip ``` fences if present
    if after_think.startswith("```"):
        after_think = after_think.split("```", 1)[-1].strip()
    if after_think.endswith("```"):
        after_think = after_think.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(after_think)
    except Exception:
        parsed = {"text": after_think}

    # yield final structured result including conversation id
    final_payload = {"result": parsed, "conversation_id": last_conversation_id}
    yield "__RESULT__" + json.dumps(final_payload, ensure_ascii=False)


# 测试用
if __name__ == '__main__':
    # 测试dify_chatflow_stream_generator
    for chunk in dify_chatflow_stream_generator("你觉得我应该补充什么内容", "test", docx_create=False, conversation_id="b443421d-33a9-444f-9c8d-06e90f5c7500"):
        print(chunk)
