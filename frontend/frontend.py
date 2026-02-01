from flask import Flask, request, jsonify, send_from_directory, Response, send_file
import os
import sys

# ensure backend folder is on sys.path so runtime imports like `from dify import ...` work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

app = Flask(__name__, static_folder='dist')


@app.route("/", methods=["GET"])
def index():
    """Serve the Vue application"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route("/generate", methods=["POST"])
def generate_document():
    """Generate a document based on user input"""
    try:
        data = request.get_json()
        title = data.get("title", "").strip()
        summary = data.get("summary", "").strip()

        if not title or not summary:
            return jsonify({"error": "标题和概要不能为空"}), 400

        # 构建提示词给Dify
        prompt = f"根据以下标题和概要，生成一份结构化的文档：\n标题：{title}\n概要：{summary}"

        # 从Dify获取JSON格式的文档数据
        try:
            from dify import dify_request
        except Exception as e:
            print('Failed to import backend.dify:', e)
            return jsonify({'error': '后端模块未找到'}), 500

        doc_data = dify_request(prompt)

        # 设置文档标题
        doc_data["title"] = title

        # 创建Word文档
        try:
            from doc import create_docx
        except Exception as e:
            print('Failed to import backend.doc:', e)
            return jsonify({'error': '后端模块未找到'}), 500

        file_path = create_docx(doc_data)

        # 返回生成的文档
        return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), as_attachment=True)

    except Exception as e:
        print(f"Error generating document: {str(e)}")
        return jsonify({"error": f"生成文档时出错: {str(e)}"}), 500


# 新的 API：用于前端单问题询问并流式返回文本片段
@app.route('/api/ask', methods=['POST'])
def api_ask():
    """Accept JSON {question: str, stream: bool} and stream text chunks when possible."""
    try:
        data = request.get_json() or {}
        question = (data.get('question') or '').strip()
        stream = bool(data.get('stream', True))

        if not question:
            return jsonify({'error': '问题不能为空'}), 400

        # If client requests streaming, try to use the generator and stream plain text chunks.
        if stream:
            def generate():
                try:
                    try:
                        import importlib
                        mod = importlib.import_module('dify')
                        # prefer the new chatflow stream generator that supports conversation_id and user
                        gen = getattr(mod, 'dify_chatflow_stream_generator')
                    except Exception as e:
                        # yield a plain text error line so frontend can show it
                        yield 'ERROR: 后端模块未找到\n'
                        return

                    # prepare parameters from incoming request (optional fields)
                    user = data.get('user', 'human-user')
                    conversation_id = data.get('conversation_id', '') or ''
                    docx_create = bool(data.get('docx_create', False))
                    # call the chatflow stream generator with the parameters
                    for chunk in gen(question, user=user, conversation_id=conversation_id, docx_create=docx_create):
                        # Ensure chunk is str
                        if isinstance(chunk, bytes):
                            chunk = chunk.decode('utf-8', errors='ignore')
                        # Yield each chunk followed by a newline separator to simplify client parsing
                        yield str(chunk) + '\n'
                except GeneratorExit:
                    # client disconnected
                    print('Client disconnected during streaming')
                except Exception as e:
                    yield ('ERROR: ' + str(e) + '\n')

            return Response(generate(), mimetype='text/plain; charset=utf-8')
        else:
            # fallback: blocking request
            try:
                from dify import dify_request
            except Exception as e:
                return jsonify({'error': '后端模块未找到'}), 500

            result = dify_request(question, stream=False)
            return jsonify({'result': result})

    except Exception as e:
        print(f"api_ask error: {e}")
        return jsonify({'error': str(e)}), 500


# 新增：根据结构化 JSON 生成 docx 并返回
@app.route('/api/docx', methods=['POST'])
def api_docx():
    try:
        data = request.get_json() or {}
        # runtime import of create_docx
        try:
            from doc import create_docx
        except Exception as e:
            print('Failed to import backend.doc:', e)
            return jsonify({'error': '后端模块未找到'}), 500

        # call create_docx, which returns file path
        file_path = create_docx(data)
        if not os.path.exists(file_path):
            return jsonify({'error': '生成文件失败'}), 500
        # use send_file with absolute path and a safe download name
        filename = os.path.basename(file_path)
        return send_file(os.path.abspath(file_path), as_attachment=True, download_name=filename)
    except Exception as e:
        print('api_docx error:', e)
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    # catch-all static route (placed at the end so API routes have priority)
    @app.route('/<path:path>')
    def serve_static(path):
        # only serve files that actually exist in the dist folder
        full = os.path.join(app.static_folder, path)
        if os.path.exists(full) and os.path.isfile(full):
            return send_from_directory(app.static_folder, path)
        # If file not found, return 404 so client-side routing or API routes can handle it
        return jsonify({'error': '静态资源未找到'}), 404


    app.run(debug=True, host="0.0.0.0", port=5000)
