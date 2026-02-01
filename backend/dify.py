import json
import os
import mimetypes
import unicodedata

import requests


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
                                   files: list = None,
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
    :param files: 可选，向 Dify /chat-messages 接口发送的 files 列表（每项为 InputFileObject），示例: [{"type":"document","transfer_method":"local_file","upload_file_id": "..."}]
    :return: 生成器，逐步 yield 文本块，最后 yield 结果
    """

    API_KEY = os.environ.get("DIFY_API_KEY", "app-6nsFy8O8xGGivOFkT6kZJvzt")
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

    # include files if provided
    if files:
        payload["files"] = files

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


def upload_file_to_dify(file_path, user: str = "unknown"):
    """
    Upload a file to Dify and return the upload file id.

    :param file_path: Path to the file to upload.
    :param user: User identifier (required by Dify file upload API) - should match the user used in chat messages.
    :return: upload_file_id (uuid string) if successful, None otherwise.
    """
    url = "https://api.dify.ai/v1/files/upload"
    API_KEY = os.environ.get("DIFY_API_KEY", "app-6nsFy8O8xGGivOFkT6kZJvzt")

    headers = {
        "Authorization": f"Bearer {API_KEY}"
        # NOTE: Do NOT set Content-Type here; requests will set the multipart boundary for us.
    }

    # Determine MIME type; prefer guessed type but fall back to common docx MIME
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        # common fallback for docx if guess_type didn't know it
        if file_path.lower().endswith('.docx'):
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_path.lower().endswith('.pdf'):
            mime_type = 'application/pdf'
        else:
            mime_type = 'application/octet-stream'

    # Log what we're about to send (helps debugging 415 unsupported file type)
    try:
        print(f"Uploading file to Dify: {file_path}, mime={mime_type}, user={user}")
    except Exception:
        pass

    # open file and send as multipart/form-data; include the required 'user' field
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, mime_type)}
            data = {"user": user}
            response = requests.post(url, headers=headers, files=files, data=data)
    except Exception as e:
        print(f"Exception when uploading file to Dify: {e}")
        return None

    if response.status_code in (200, 201):
        try:
            data = response.json()
        except Exception:
            print("Upload succeeded but response is not valid JSON:", response.text)
            return None
        # Dify may return 'id' or 'upload_file_id' - accept both for compatibility
        print("Dify 文件ID:", data)
        return data.get("id") or data.get("upload_file_id")
    else:
        print(f"Failed to upload file to Dify: {response.status_code}, {response.text}")
        print("文件位置:", file_path)
        # 如果是415错误，尝试使用ASCII文件名重试
        if response.status_code == 415:
            basename = os.path.basename(file_path)
            # 检查文件名是否为非ASCII字符
            if any(ord(char) > 127 for char in basename):
                # 尝试进行Unicode到ASCII的转码
                ascii_filename = unicodedata.normalize('NFKD', basename).encode('ascii', 'ignore').decode('ascii')
                print(f"Retrying upload with ASCII filename: {ascii_filename}")
                try:
                    with open(file_path, "rb") as f:
                        files = {"file": (ascii_filename, f, mime_type)}
                        data = {"user": user}
                        response = requests.post(url, headers=headers, files=files, data=data)
                        if response.status_code in (200, 201):
                            data = response.json()
                            print("Dify 文件ID:", data)
                            return data.get("id") or data.get("upload_file_id")
                except Exception as e:
                    print(f"Exception when retrying file upload to Dify: {e}")
                    return None
        return None


def delete_file_on_dify(upload_file_id: str):
    """
    Best-effort delete of an uploaded file on Dify. Returns True if deletion reported success.
    """
    if not upload_file_id:
        return False
    API_KEY = os.environ.get("DIFY_API_KEY", "app-6nsFy8O8xGGivOFkT6kZJvzt")
    url = f"https://api.dify.ai/v1/files/{upload_file_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        resp = requests.delete(url, headers=headers)
        if resp.status_code in (200, 204):
            print(f"Deleted file on Dify: {upload_file_id}")
            return True
        else:
            print(f"Failed to delete file on Dify: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"Exception calling Dify delete API: {e}")
        return False


# 测试用
if __name__ == '__main__':
    # 测试dify_chatflow_stream_generator (this will try to contact the remote API)
    for chunk in dify_chatflow_stream_generator("你觉得我应该补充什么内容", "test", docx_create=False, conversation_id="b443421d-33a9-444f-9c8d-06e90f5c7500"):
        print(chunk)

    # 测试文件上传 (ensure DIFY_API_KEY env var is set or the function will use "YOUR_API_KEY" placeholder)
    file_id = upload_file_to_dify("path_to_your_file", user="test-user")
    if file_id:
        print(f"File uploaded successfully, file_id: {file_id}")
    else:
        print("File upload failed")
