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
        question = data.get('question').strip()

        if not question:
            return jsonify({'error': '问题不能为空'}), 400

        # 生成请求
        def generate():
            try:
                import importlib
                mod = importlib.import_module('dify')
                gen = getattr(mod, 'dify_chatflow_stream_generator')
            except Exception as e:
                # 输出错误
                yield 'ERROR: 后端模块未找到'
                return

            # 准备参数
            user = data.get('user', 'default')
            conversation_id = data.get('conversation_id', '')
            docx_create = bool(data.get('docx_create', False))
            menu = data.get('menu', '')
            outline = data.get('outline', '')
            example = data.get('example', '')
            file_num = data.get('file_num', 1000)
            style = data.get('style', '不指定')
            facing = data.get('facing', '不指定')
            files = list(data.get('files') or [])

            # 使用参数调用聊天流程流生成器，包括提供的文件id
            for chunk in gen(
                    question=question,
                    user=user,
                    conversation_id=conversation_id,
                    docx_create=docx_create,
                    style=style,
                    facing=facing,
                    menu=menu,
                    outline=outline,
                    example=example,
                    file_num=file_num,
                    files=files
            ):
                if isinstance(chunk, bytes):
                    chunk = chunk.decode('utf-8', errors='ignore')
                yield str(chunk)

        return Response(generate(), mimetype='text/plain; charset=utf-8')


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


# 从前端接受文件提交，并上传至 Dify
@app.route('/api/upload', methods=['POST'])
def api_upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '[149]请求中未找到文件信息'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '[153]未选择文件'}), 400

        original_filename = file.filename
        # 去掉路径，只留文件名
        basename = os.path.basename(original_filename)
        # 替换危险字符
        filename = basename.replace(os.path.sep, '_')
        if os.path.altsep:
            filename = filename.replace(os.path.altsep, '_')
        filename = filename.replace(':', '_')

        # 保存文件至本地 (files/uploads)
        upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'files', 'uploads')
        upload_dir = os.path.abspath(upload_dir)
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, filename)
        file.save(save_path)

        user = request.form.get('user', 'human-user')

        # 进行上传 (dify.py)
        try:
            from dify import upload_file_to_dify
        except Exception as e:
            print('Failed to import dify.upload helper:', e)
            return jsonify({'error': '后端上传模块未找到'}), 500

        upload_file_id = upload_file_to_dify(save_path, user=user)
        if not upload_file_id:
            return jsonify({'error': 'Failed to upload file to Dify'}), 500

        return jsonify({'message': 'File uploaded successfully', 'original_filename': original_filename, 'file_path': save_path, 'upload_file_id': upload_file_id}), 200
    except Exception as e:
        print('api_upload error:', e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete_upload', methods=['POST'])
def api_delete_upload():
    """Best-effort: delete the saved local file and remove it from Dify if upload_file_id provided."""
    try:
        data = request.get_json() or {}
        upload_file_id = data.get('upload_file_id')
        file_path = data.get('file_path')

        deleted_local = False
        deleted_remote = False

        # delete local file if path provided
        if file_path:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_local = True
            except Exception as e:
                print('Error deleting local file:', e)

        # attempt to delete on Dify if id provided
        if upload_file_id:
            try:
                from dify import delete_file_on_dify
                deleted_remote = delete_file_on_dify(upload_file_id)
            except Exception as e:
                print('Error calling delete_file_on_dify:', e)

        return jsonify({'deleted_local': deleted_local, 'deleted_remote': deleted_remote}), 200
    except Exception as e:
        print('api_delete_upload error:', e)
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
