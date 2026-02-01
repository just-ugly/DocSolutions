<template>
  <div id="app" class="app-shell" :class="theme">
    <aside class="sidebar">
      <div class="user">
        <div class="avatar">U</div>
        <div class="username">用户</div>
        <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? '切换到浅色主题' : '切换到深色主题'">
          <svg v-if="theme === 'dark'" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" fill="currentColor" />
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M6.76 4.84l-1.8-1.79L3.17 4.84l1.79 1.79 1.8-1.79zM1 13h3v-2H1v2zm10 9h2v-3h-2v3zm9-9v-2h-3v2h3zM17.24 4.84l1.79-1.79 1.79 1.79-1.79 1.79-1.79-1.79zM12 6a6 6 0 100 12 6 6 0 000-12z" fill="currentColor" />
          </svg>
        </button>
      </div>
      <div class="history">
        <h3>历史对话</h3>
        <p class="placeholder">（暂未实现）</p>
      </div>
    </aside>

    <main class="main-area">
      <div class="content">
        <div class="messages">
          <div v-for="(m, i) in messages" :key="i" :class="['message', m.sender === 'user' ? 'user' : 'bot']">
            <!-- bot messages are parsed into segments -->
            <template v-if="m.sender === 'bot'">
              <div v-for="(seg, sidx) in parseSegments(m.content)" :key="sidx">
                <template v-if="seg.type === 'text'">
                  <pre class="chunk-text">{{ seg.content }}</pre>
                </template>
                <template v-else-if="seg.type === 'think'">
                  <div class="think">{{ seg.content }}</div>
                </template>
                <template v-else-if="seg.type === 'json'">
                  <pre class="json-block">{{ seg.content }}</pre>
                </template>
                <template v-else>
                  <pre class="chunk-text">{{ seg.content }}</pre>
                </template>
              </div>
            </template>

            <!-- user messages are plain, right-aligned -->
            <template v-else>
              <pre class="chunk-text">{{ m.content }}</pre>
            </template>
          </div>

          <div v-if="error" class="message error">{{ error }}</div>
          <div v-if="isLoading && !hasBotContent()" class="message loading">正在回答…</div>

          <!-- download aligned with bot messages -->
          <div v-if="finalResult" class="message bot action-row">
            <div class="result-actions">
              <button @click="downloadResult" class="download-btn">下载结果</button>
            </div>
          </div>
        </div>
      </div>

      <!-- compose area: expand button + optional panel above input bar -->
      <div class="compose-area">
        <button class="expand-btn" @click="toggleExpand" :aria-expanded="panelExpanded" :title="panelExpanded ? '收起选项' : '展开更多选项'">
          <!-- inverted V path to indicate expanded/up -->
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M7 15l5-5 5 5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>

        <div class="expand-panel" v-if="panelExpanded">
          <div class="top-fields">
            <div class="field"><label>问题</label><input class="main-input" v-model="question" :disabled="isLoading" /></div>
            <div class="field"><label>目录</label><textarea class="menu-textarea" v-model="menu" rows="2"></textarea></div>
            <div class="field"><label>提纲</label><textarea v-model="outline"></textarea></div>
            <div class="field"><label>示例</label><textarea v-model="example"></textarea></div>
          </div>

          <div class="two-cols">
            <div class="left-col">
              <label>预期文档字数</label>
              <input type="number" v-model.number="file_num" min="1" />

              <label>预期文档文风</label>
              <select v-model="style">
                <option value="">不指定</option>
                <option value="技术说明">技术说明</option>
                <option value="学术论文">学术论文</option>
                <option value="营销">营销</option>
                <option value="新闻">新闻</option>
                <option value="日常">日常</option>
              </select>

              <label class="checkbox-row"><input type="checkbox" v-model="first_page_toc" /> 第一页是否生成目录</label>
            </div>

            <div class="right-col">
              <div class="dropzone" @dragover.prevent="onDragOver" @dragleave.prevent="onDragLeave" @drop.prevent="onDrop" @click="triggerFileInput">
                <input ref="fileInput" type="file" multiple style="display:none" @change="onFileInputChange" />
                <div class="dropzone-inner">
                  <p>点击添加文件，或将文件拖动于此</p>
                  <div v-if="docFiles.length" class="added-list">
                    <div v-for="(f,i) in docFiles" :key="i" class="file-item">
                      <span class="file-name">{{ f.name }}</span>
                      <button class="file-delete-btn" @click.stop="deleteFile(i)" :title="f.uploading ? '上传中，稍后可删除' : '删除文件'">✕</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="input-bar">
          <input class="main-input" v-model="question" @keyup.enter="send(false)" :disabled="isLoading" />
          <button class="btn-send" @click="send(false)" :disabled="isLoading || !question.trim()">发送</button>
          <button class="btn-gen" @click="send(true)" :disabled="isLoading || !question.trim()">生成</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      question: '',
      messages: [],
      isLoading: false,
      error: null,
      finalResult: null,
      currentAbortController: null,
      // theme: 'dark' or 'light'
      theme: 'dark',
      // new UI state for expanded options
      panelExpanded: false,
      menu: '',
      outline: '',
      example: '',
      file_num: 1000,
      style: '',
      first_page_toc: false,
      docFiles: [],
      // store active conversation id after first response so subsequent sends continue the conversation
      currentConversationId: null,
      // track promises for in-flight uploads so send() can wait for them
      uploadPromises: [],
      fileDropOver: false
    };
  },
  created() {
    // Load theme from localStorage if available and apply class to documentElement so variables affect body
    try {
      const t = localStorage.getItem('theme');
      if (t === 'light' || t === 'dark') this.theme = t;
    } catch (e) {}
    // load persisted conversation id if available
    try {
      const cid = localStorage.getItem('conversation_id');
      if (cid) this.currentConversationId = cid;
    } catch (e) {}
    try {
      document.documentElement.classList.remove('light', 'dark');
      document.documentElement.classList.add(this.theme);
    } catch (e) {}
  },
  methods: {
    toggleTheme() {
      // fade out -> change theme -> fade in to ensure smooth transition both directions
      try {
        document.documentElement.classList.add('theme-fading');
      } catch (e) {}

      // short delay to allow fade-out, then switch theme and remove fading class
      setTimeout(() => {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        try {
          localStorage.setItem('theme', this.theme);
          document.documentElement.classList.remove('light', 'dark');
          document.documentElement.classList.add(this.theme);
        } catch (e) {}

        // allow a tiny timeout for the new theme to render, then fade in
        setTimeout(() => {
          try { document.documentElement.classList.remove('theme-fading'); } catch (e) {}
        }, 40);
      }, 180);
    },
    hasBotContent() {
      // check if there is any bot message with non-empty content
      return this.messages.some(m => m.sender === 'bot' && (m.content || '').trim().length > 0);
    },

    toggleExpand() {
      this.panelExpanded = !this.panelExpanded;
    },

    triggerFileInput() {
      try { this.$refs.fileInput.click(); } catch (e) {}
    },

    onFileInputChange(e) {
      const files = Array.from(e.target.files || []);
      if (files.length) {
        // upload each file immediately and store metadata + upload_file_id
        for (const f of files) {
          const p = this.uploadAndAppend(f);
          // keep track so we can await all uploads before sending
          this.uploadPromises.push(p);
        }
      }
      // clear the native input so selecting same file again still fires
      e.target.value = null;
    },

    onDragOver() {
      this.fileDropOver = true;
    },

    onDragLeave() {
      this.fileDropOver = false;
    },

    onDrop(e) {
      this.fileDropOver = false;
      const dt = e.dataTransfer;
      if (!dt) return;
      const files = Array.from(dt.files || []);
      if (files.length) {
        // upload each file immediately and store metadata + upload_file_id
        for (const f of files) {
          const p = this.uploadAndAppend(f);
          this.uploadPromises.push(p);
        }
      }
    },

    // Upload a single File object to backend /api/upload and append to docFiles
    async uploadAndAppend(file) {
      // create a placeholder entry so the UI shows the file immediately
      const placeholder = { name: file.name, size: file.size, type: file.type, uploading: true, upload_file_id: null, file_path: null };
      const idx = this.docFiles.length;
      this.docFiles.push(placeholder);

      try {
        const form = new FormData();
        // include original filename
        form.append('file', file, file.name);
        // include user id expected by Dify; ensure it matches the user used in /api/ask
        form.append('user', 'human-user');

        const res = await fetch('/api/upload', {
          method: 'POST',
          body: form
        });

        if (!res.ok) {
          const text = await res.text();
          console.error('Upload failed:', text);
          this.docFiles[idx].uploading = false;
          this.docFiles[idx].error = text;
          return null;
        }

        const json = await res.json();
        // response expected to include upload_file_id and file_path
        const upload_file_id = json.upload_file_id || json.id || null;
        const file_path = json.file_path || null;

        // update placeholder with upload id and saved path
        this.docFiles[idx].upload_file_id = upload_file_id;
        this.docFiles[idx].file_path = file_path;
         this.docFiles[idx].uploading = false;
         return upload_file_id;
      } catch (err) {
        console.error('Exception while uploading file to backend:', err);
        this.docFiles[idx].uploading = false;
        this.docFiles[idx].error = String(err);
        return null;
      }
    },

    async send(docx_create = false) {
      this.error = null;
      const q = (this.question || '').trim();
      if (!q) {
        this.error = '问题不能为空';
        return;
      }

      // Abort any previous pending request/stream
      try {
        if (this.currentAbortController) {
          this.currentAbortController.abort();
        }
      } catch (e) {
        // ignore
      }

      // clear previous final result and push new messages
      this.finalResult = null;
      this.messages.push({ sender: 'user', content: q });
      this.question = '';
      // remove any trailing empty bot placeholders from prior aborted requests
      for (let i = this.messages.length - 1; i >= 0; i--) {
        if (this.messages[i].sender === 'bot' && (!this.messages[i].content || this.messages[i].content.trim() === '')) {
          this.messages.splice(i, 1);
        } else break;
      }
      this.messages.push({ sender: 'bot', content: '' });

      this.isLoading = true;

      try {
        // create a new AbortController for this request so we can cancel it if a new send happens
        const controller = new AbortController();
        this.currentAbortController = controller;
        // Wait for any in-flight uploads to finish so we include upload_file_id values
        if (this.uploadPromises && this.uploadPromises.length) {
          try {
            await Promise.allSettled(this.uploadPromises);
          } catch (e) {
            // ignore; we'll filter out files without upload_file_id below
          }
          // clear tracked promises
          this.uploadPromises = [];
        }

        // build payload including new options
        const payload = {
          question: q,
          stream: true,
          docx_create: !!docx_create,
          file_num: this.file_num || null,
          style: this.style || '',
          first_page_toc: !!this.first_page_toc,
          // include user id so backend can forward to Dify and match uploads
          user: 'human-user',
          // continue conversation if we have an id
          conversation_id: this.currentConversationId || undefined,
          // If upload_file_id is available, send Dify InputFileObject for local_file transfer
          files: this.docFiles.filter(f => f.upload_file_id).map(f => ({ type: 'document', transfer_method: 'local_file', upload_file_id: f.upload_file_id })),
           menu: this.menu || '',
           outline: this.outline || '',
           example: this.example || ''
         };

        const res = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          signal: controller.signal
        });

        if (!res.ok) {
          const eText = await res.text();
          this.error = '请求失败: ' + eText;
          this.isLoading = false;
          return;
        }

        if (res.body && res.body.getReader) {
          const reader = res.body.getReader();
          const decoder = new TextDecoder('utf-8');
          let done = false;
          let accumulated = '';

          while (!done) {
            const { value, done: streamDone } = await reader.read();
            done = streamDone;
            if (value) {
              const text = decoder.decode(value, { stream: true });
              const parts = text.split('\n');
              if (accumulated) {
                parts[0] = accumulated + parts[0];
                accumulated = '';
              }
              if (text[text.length - 1] !== '\n') accumulated = parts.pop();

              for (const part of parts) {
                if (!part) continue;
                if (part.startsWith('__RESULT__')) {
                  const jsonStr = part.slice('__RESULT__'.length);
                  try {
                    this.finalResult = JSON.parse(jsonStr);
                    // if Dify returned a conversation_id, keep it for following messages
                    if (this.finalResult && this.finalResult.conversation_id) {
                      this.currentConversationId = this.finalResult.conversation_id;
                    }
                  } catch (e) {
                    this.finalResult = { text: jsonStr };
                  }
                } else {
                  // append to last bot message
                  const lastBotIndex = this.findLastBotIndex();
                  if (lastBotIndex === -1) {
                    this.messages.push({ sender: 'bot', content: part });
                  } else {
                    this.messages[lastBotIndex].content += part;
                  }
                }
              }
            }
          }

          // flush remaining
          if (accumulated) {
            const part = accumulated;
            if (part.startsWith('__RESULT__')) {
              const jsonStr = part.slice('__RESULT__'.length);
              try {
                this.finalResult = JSON.parse(jsonStr);
              } catch (e) {
                this.finalResult = { text: jsonStr };
              }
            } else {
              const lastBotIndex = this.findLastBotIndex();
              if (lastBotIndex === -1) this.messages.push({ sender: 'bot', content: part });
              else this.messages[lastBotIndex].content += part;
            }
          }

        } else {
          const json = await res.json();
          if (json.error) {
            this.error = json.error;
          } else if (json.result) {
            this.finalResult = json.result;
            const text = JSON.stringify(json.result, null, 2);
            const lastBotIndex = this.findLastBotIndex();
            if (lastBotIndex === -1) this.messages.push({ sender: 'bot', content: text });
            else this.messages[lastBotIndex].content += '\n' + text;
          } else {
            const text = await res.text();
            const lastBotIndex = this.findLastBotIndex();
            if (lastBotIndex === -1) this.messages.push({ sender: 'bot', content: text });
            else this.messages[lastBotIndex].content += text;
          }
        }

      } catch (e) {
        // if aborted, do not treat as error
        if (e && e.name === 'AbortError') {
          // aborted by a new request; just return
          return;
        }
        this.error = String(e);
      } finally {
        this.isLoading = false;
        // clear and release controller
        if (this.currentAbortController) {
          try { this.currentAbortController = null; } catch (e) {}
        }
      }
    },

    findLastBotIndex() {
      for (let i = this.messages.length - 1; i >= 0; i--) {
        if (this.messages[i].sender === 'bot') return i;
      }
      return -1;
    },

    // parse message into segments: text, think, json (handles open tags streaming)
    parseSegments(text) {
      if (!text) return [];
      const segments = [];
      let rest = String(text);

      while (rest.length > 0) {
        const thinkOpen = rest.indexOf('<think>');
        const thinkClose = rest.indexOf('</think>');
        const codeOpen = rest.indexOf('```');

        const candidates = [];
        if (thinkOpen !== -1) candidates.push({ type: 'think', index: thinkOpen });
        if (codeOpen !== -1) candidates.push({ type: 'code', index: codeOpen });
        if (candidates.length === 0) {
          segments.push({ type: 'text', content: rest });
          break;
        }

        candidates.sort((a, b) => a.index - b.index);
        const first = candidates[0];

        if (first.type === 'think') {
          // text before think tag
          if (first.index > 0) {
            segments.push({ type: 'text', content: rest.slice(0, first.index) });
          }
          // think tag itself
          segments.push({ type: 'think', content: rest.slice(first.index + '<think>'.length, thinkClose !== -1 ? thinkClose : undefined) });
          // rest after think tag
          rest = rest.slice(thinkClose !== -1 ? thinkClose + '</think>'.length : first.index);
        } else {
          // code block or inline code
          const isCodeBlock = rest[first.index + 3] === '\n';
          if (isCodeBlock) {
            // code block: split by lines, preserve line breaks
            const lines = rest.slice(0, first.index).split('\n');
            for (const line of lines) {
              if (line) segments.push({ type: 'text', content: line });
            }
            segments.push({ type: 'code', content: rest.slice(first.index + 3, codeOpen !== -1 ? codeOpen : undefined) });
            rest = rest.slice(codeOpen !== -1 ? codeOpen + 3 : first.index);
          } else {
            // inline code: treat as text
            segments.push({ type: 'text', content: rest.slice(0, first.index) });
            segments.push({ type: 'code', content: rest.slice(first.index + 1, codeOpen !== -1 ? codeOpen : undefined) });
            rest = rest.slice(codeOpen !== -1 ? codeOpen + 1 : first.index);
          }
        }
      }

      return segments;
    },

    // Download the generated result as a .docx file.
    async downloadResult() {
      if (!this.finalResult) {
        this.error = '没有可下载的结果';
        return;
      }

      const prevLoading = this.isLoading;
      this.isLoading = true;
      this.error = null;

      try {
        // If finalResult is a wrapper like { result: {...}, conversation_id: ... }, prefer inner result
        const docObj = (this.finalResult && this.finalResult.result) ? this.finalResult.result : this.finalResult;

        // If backend returned a direct URL we can download, prefer it (check wrapper and inner)
        const direct = (this.finalResult && (this.finalResult.download_url || this.finalResult.url || this.finalResult.file_path)) || (docObj && (docObj.download_url || docObj.url || docObj.file_path)) || null;
        if (direct && typeof direct === 'string') {
          const fetchUrl = direct.startsWith('http') ? direct : direct.startsWith('/') ? direct : `/api/docx?path=${encodeURIComponent(direct)}`;

          const res = await fetch(fetchUrl, { method: 'GET' });
          if (!res.ok) {
            const txt = await res.text();
            throw new Error('下载失败: ' + txt);
          }

          const ct = (res.headers.get('content-type') || '').toLowerCase();
          if (ct.includes('application/json')) {
            const j = await res.json();
            throw new Error(j.error || j.message || '服务器返回 JSON 而非文件');
          }

          const blob = await res.blob();
          const disposition = res.headers.get('content-disposition') || '';
          let filename = (docObj && (docObj.filename || docObj.name)) || (this.finalResult && (this.finalResult.filename || this.finalResult.name)) || 'result.docx';
          const m = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(disposition);
          if (m) filename = decodeURIComponent(m[1] || m[2]);

          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
          return;
        }

        // Fallback: POST the structured document (docObj) to backend /api/docx which will create and return the docx
        const res = await fetch('/api/docx', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(docObj)
        });

        if (!res.ok) {
          const ct = (res.headers.get('content-type') || '').toLowerCase();
          if (ct.includes('application/json')) {
            const j = await res.json();
            throw new Error(j.error || j.message || '生成文档失败');
          }
          const txt = await res.text();
          throw new Error('生成文档失败: ' + txt);
        }

        const contentType = (res.headers.get('content-type') || '').toLowerCase();
        if (contentType.includes('application/json')) {
          const j = await res.json();
          if (j.error) throw new Error(j.error);
          const maybeUrl = j.download_url || j.file_path || j.url || null;
          if (maybeUrl) {
            const r2 = await fetch(maybeUrl.startsWith('http') ? maybeUrl : maybeUrl.startsWith('/') ? maybeUrl : `/api/docx?path=${encodeURIComponent(maybeUrl)}`);
            if (!r2.ok) throw new Error('下载中转失败');
            const blob2 = await r2.blob();
            const disposition2 = r2.headers.get('content-disposition') || '';
            let filename2 = j.filename || (docObj && (docObj.filename || docObj.name)) || 'result.docx';
            const m2 = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(disposition2);
            if (m2) filename2 = decodeURIComponent(m2[1] || m2[2]);
            const url2 = URL.createObjectURL(blob2);
            const a2 = document.createElement('a');
            a2.href = url2;
            a2.download = filename2;
            document.body.appendChild(a2);
            a2.click();
            document.body.removeChild(a2);
            URL.revokeObjectURL(url2);
            return;
          }

          throw new Error('后端未返回文件');
        }

        const blob = await res.blob();
        const disposition = res.headers.get('content-disposition') || '';
        let filename = (docObj && (docObj.filename || docObj.name)) || (this.finalResult && (this.finalResult.filename || this.finalResult.name)) || 'result.docx';
        const m3 = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(disposition);
        if (m3) filename = decodeURIComponent(m3[1] || m3[2]);

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error('downloadResult error', err);
        this.error = err && err.message ? err.message : String(err);
      } finally {
        this.isLoading = prevLoading;
      }
    },

    // Delete an uploaded file from UI and, if uploaded, request backend to remove it
    async deleteFile(idx) {
      if (idx == null || idx < 0 || idx >= this.docFiles.length) return;

      const file = this.docFiles[idx];

      // If uploading, allow immediate removal from UI
      if (file.uploading) {
        // simply remove placeholder
        this.docFiles.splice(idx, 1);
        return;
      }

      // If file has upload_file_id, try to delete on server as well
      if (file.upload_file_id) {
        try {
          // try common endpoint names
          const endpoints = ['/api/delete', '/api/delete_upload', '/api/delete_file'];
          let deleted = false;
          for (const ep of endpoints) {
            try {
              const res = await fetch(ep, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ upload_file_id: file.upload_file_id, file_path: file.file_path })
              });
              if (res.ok) {
                deleted = true;
                break;
              }
            } catch (e) {
              // ignore and try next
            }
          }
          // remove from UI regardless of backend success, but log if failed
          this.docFiles.splice(idx, 1);
          if (!deleted) console.warn('Server-side file delete may have failed for', file.upload_file_id);
          return;
        } catch (err) {
          console.error('deleteFile error', err);
          // still remove from UI to avoid blocking user
          this.docFiles.splice(idx, 1);
          this.error = '删除文件时出现错误（已从列表移除）';
          return;
        }
      }

      // otherwise just remove from UI
      this.docFiles.splice(idx, 1);
    }

    },
    watch: {
      // watch currentConversationId and persist to localStorage
      currentConversationId(newCid) {
        try {
          localStorage.setItem('conversation_id', newCid);
        } catch (e) {}
      }
    }
  };
</script>

<style>
/* Also expose theme variables on the html element so body and other ancestors can read them
   (we add both html.dark/html.light in addition to .app-shell.* so toggling the html class works) */
.app-shell.dark {
  --sidebar-width: 260px;
  --bg: linear-gradient(180deg, #071017 0%, #0b1418 100%);
  --accent: #b8860b; /* black-gold */
  --muted: #9aa6ad;
  --glass: rgba(255,255,255,0.03);
  --text: #d9e6eb;
  --sidebar-bg: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005));
  --sidebar-border: rgba(255,255,255,0.02);
  --bot-bg: rgba(255,255,255,0.02);
  --bot-text: #dbe9ec;
  --user-bg: rgba(255,255,255,0.96);
  --user-text: #0b0f12;
  /* Centralized control colors for dark theme — tuned for visibility without glare */
  --input-bg: rgba(0,0,0,0.45);      /* slightly dark surface for inputs */
  --control-bg: rgba(0,0,0,0.45);
  --control-border: rgba(255,255,255,0.04);
  --dropzone-border: rgba(255,255,255,0.22); /* stronger to be clearly visible */
  --dropzone-bg: rgba(255,255,255,0.02);
  --scroll-thumb: rgba(255,255,255,0.025);   /* darker but subtle */
  --code-bg: #071017;
  --message-shadow: 0 6px 18px rgba(2,6,10,0.35);
  --accent-2: #ffd27a; /* gold highlight */
  --avatar-bg: linear-gradient(135deg,#0c0c0c 0%, #2b1f0a 100%);
  --avatar-shadow: 0 4px 12px rgba(0,0,0,0.15);
  --avatar-border: 1px solid rgba(255,255,255,0.04);
  --border-color: rgba(255,255,255,0.06);
  --error-color: #ff6b6b;
}
.app-shell.light {
  --sidebar-width: 260px;
  --bg: linear-gradient(135deg, #eef2f7 0%, #d7e1ec 100%);
  --accent: #2b7cff; /* blue accent */
  --muted: #6b7280;
  --glass: rgba(0,0,0,0.04);
  --text: #081217; /* dark text */
  --sidebar-bg: #ffffff;
  --sidebar-border: #e6ecf2;
  --bot-bg: #ffffff; /* generated messages white */
  --bot-text: #0b1720;
  --user-bg: #eaf4ff; /* subtle blue-ish white for user */
  --user-text: #062036;
  --input-bg: #ffffff;
  --code-bg: #f5f7fb;
  --message-shadow: 0 4px 12px rgba(11,20,30,0.06);
  --accent-2: #8ec4ff; /* lighter blue highlight */
  --avatar-bg: linear-gradient(135deg,#ffffff 0%, #eaf4ff 100%);
  --avatar-shadow: 0 4px 12px rgba(0,0,0,0.1);
  --avatar-border: 1px solid rgba(0,0,0,0.06);
  --border-color: rgba(0,0,0,0.06);
  --error-color: #d93025;
}

/* Mirror vars on the html element so documentElement.classList = 'dark'|'light' controls page colors */
html.dark {
  --sidebar-width: 260px;
  --bg: linear-gradient(180deg, #071017 0%, #0b1418 100%);
  --accent: #b8860b; /* black-gold */
  --muted: #9aa6ad;
  --glass: rgba(255,255,255,0.03);
  --text: #d9e6eb;
  --sidebar-bg: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005));
  --sidebar-border: rgba(255,255,255,0.02);
  --bot-bg: rgba(255,255,255,0.02);
  --bot-text: #dbe9ec;
  --user-bg: rgba(255,255,255,0.96);
  --user-text: #0b0f12;
  /* same control variables mirrored for html.dark */
  --input-bg: rgba(0,0,0,0.45);
  --control-bg: rgba(0,0,0,0.45);
  --control-border: rgba(255,255,255,0.04);
  --dropzone-border: rgba(255,255,255,0.22);
  --dropzone-bg: rgba(255,255,255,0.02);
  --scroll-thumb: rgba(255,255,255,0.025);
}
html.light {
  --sidebar-width: 260px;
  --bg: linear-gradient(135deg, #eef2f7 0%, #d7e1ec 100%);
  --accent: #2b7cff; /* blue accent */
  --muted: #6b7280;
  --glass: rgba(0,0,0,0.04);
  --text: #081217; /* dark text */
  --sidebar-bg: #ffffff;
  --sidebar-border: #e6ecf2;
  --bot-bg: #ffffff; /* generated messages white */
  --bot-text: #0b1720;
  --user-bg: #eaf4ff; /* subtle blue-ish white for user */
  --user-text: #062036;
  --input-bg: #ffffff;
  --code-bg: #f5f7fb;
  --message-shadow: 0 4px 12px rgba(11,20,30,0.06);
  --accent-2: #8ec4ff;
  --avatar-bg: linear-gradient(135deg,#ffffff 0%, #eaf4ff 100%);
  --avatar-shadow: 0 4px 12px rgba(0,0,0,0.1);
  --avatar-border: 1px solid rgba(0,0,0,0.06);
}

/* Smooth transition for html background and color when toggling theme */
html {
  transition: background 260ms ease-in-out, color 260ms ease-in-out;
}

:root {
  --sidebar-width: 260px;
  --bg: linear-gradient(180deg, #071017 0%, #0b1418 100%);
  --accent: #b8860b; /* fallback */
  --muted: #9aa6ad;
  --glass: rgba(255,255,255,0.04);
  --text: #d9e6eb;
  --sidebar-bg: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  --sidebar-border: rgba(255,255,255,0.03);
  --bot-bg: rgba(255,255,255,0.03);
  --bot-text: #dbe9ec;
  --user-bg: rgba(255,255,255,0.96);
  --user-text: #0b0f12;
  --input-bg: rgba(255,255,255,0.02);
  --code-bg: #071017;
  --message-shadow: 0 6px 18px rgba(2,6,10,0.35);
  --border-color: rgba(255,255,255,0.06);
  --error-color: #ff6b6b;
}

* { box-sizing: border-box; }
html, body, #app { height: 100%; }
body {
  margin: 0;
  font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
}

/* smooth transitions for theme-related properties */
.app-shell,
.sidebar,
.message,
.input-bar,
.input-bar input,
.avatar,
.theme-toggle,
.json-block {
  transition: background-color 260ms ease, color 260ms ease, border-color 260ms ease, box-shadow 260ms ease;
}

.app-shell {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: var(--bg);
}

.sidebar {
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  padding: 22px;
  display: flex;
  flex-direction: column;
  color: var(--text);
}

.user { display: flex; align-items: center; margin-bottom: 20px; }
.avatar {
  width: 56px; height: 56px; border-radius: 50%;
  background: var(--avatar-bg);
  color: #ffdf8f; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:20px; margin-right:12px;
  box-shadow: var(--avatar-shadow), var(--message-shadow), inset 0 -2px 6px rgba(0,0,0,0.12);
  border: var(--avatar-border);
}
.username { font-weight: 600; color: var(--text); }
.history { flex: 1; overflow: auto; }
.history h3 { margin-bottom: 8px; color: var(--muted); }
.placeholder { color: var(--muted); }

.main-area { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }

.content { padding: 24px; height: calc(100vh - 80px); overflow: auto; }
.messages { max-width: 900px; margin: 0 auto; display:flex; flex-direction:column; gap: 10px; }

/* message bubbles */
.message { padding: 14px 18px; border-radius: 12px; margin-bottom: 8px; box-shadow: var(--message-shadow); max-width: 78%; font-size: 17px; backdrop-filter: blur(6px); }
.message.system { background: transparent; box-shadow: none; color: var(--muted); max-width: 100%; }

/* Bot (generated) messages: use vars */
.message.bot { background: var(--bot-bg); color: var(--bot-text); align-self: flex-start; border: 1px solid rgba(0,0,0,0.04); }

/* User messages: refined */
.message.user { background: var(--user-bg); color: var(--user-text); align-self: flex-end; border: 1px solid rgba(0,0,0,0.04); box-shadow: 0 8px 24px rgba(11,15,18,0.06); }

.message.error { border-left: 4px solid #e74c3c; color: #ffb4b0; align-self: flex-start; }
.message.loading { color: #b1d6ff; align-self: flex-start; }

.chunk-text { margin: 0; font-family: 'Segoe UI', 'Microsoft YaHei', 'Inter', system-ui, -apple-system, sans-serif; font-size: 17px; white-space: pre-wrap; word-break: break-word; color: inherit; }

/* think block: subtle panel with accent */
.think { background: rgba(255,255,255,0.03); color: var(--bot-text); padding: 10px 12px; border-left: 3px solid var(--accent); border-radius: 8px; margin-bottom: 8px; font-style: normal; }

/* JSON code block */
.json-block { background: var(--code-bg); color: var(--bot-text); padding: 14px; border-radius: 8px; overflow:auto; font-family: 'Courier New', monospace; font-size: 14px; white-space: pre-wrap; word-break: break-word; max-height: 420px; border: 1px solid rgba(0,0,0,0.04); }

/* download action pinned to bot left edge */
.result-actions { display:flex; justify-content: flex-start; }
.action-row { background: transparent; box-shadow: none; padding: 0; margin-bottom: 12px; align-self: flex-start; }
.download-btn { padding: 8px 14px; border-radius: 8px; background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%); color: white; border: none; cursor: pointer; box-shadow: 0 6px 18px rgba(39,174,96,0.14); }

/* input bar */
.input-bar { height: 84px; display:flex; gap: 12px; padding: 14px 20px; align-items: center; border-top: 1px solid rgba(0,0,0,0.04); background: var(--sidebar-bg); border-radius: 14px; }
.input-bar input { flex: 1; height: 56px; padding: 14px 16px; border-radius: 14px; border: 1px solid rgba(0,0,0,0.06); background: var(--input-bg); color: var(--text); font-size: 16px; }
.input-bar input::placeholder { color: var(--muted); }
.input-bar button { width: 120px; height: 56px; border-radius: 14px; border: none; background: linear-gradient(90deg, var(--accent), var(--accent-2)); color: #081217; font-weight: 700; font-size: 16px; box-shadow: 0 8px 20px rgba(184,134,11,0.12); cursor: pointer; }

.input-help { color: var(--muted); font-size: 13px; margin: 6px 20px 2px; }

/* Ensure menu/outline/example textareas only resize vertically */
.top-fields input, .top-fields textarea { width:100%; padding:8px; border-radius:8px; border:1px solid rgba(0,0,0,0.06); background:var(--input-bg); color:var(--text); }
.top-fields textarea { resize: vertical; }
.menu-textarea { resize: vertical; min-height:42px; max-height:200px; }

/* Dark-theme tweaks: reuse centralized variables so we can tweak brightness easily */
.app-shell.dark .dropzone {
  border: 2px dashed var(--dropzone-border);
  background: var(--dropzone-bg);
  border-radius: 10px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
}
.app-shell.dark .dropzone-inner { color: var(--muted); }
.app-shell.dark .left-col input,
.app-shell.dark .left-col select,
.app-shell.dark .top-fields input,
.app-shell.dark .top-fields textarea {
  background: var(--control-bg);
  border: 1px solid var(--control-border);
  color: var(--text);
}
.app-shell.dark .left-col select { color: var(--text); background-image: none; }

/* Tone down number input spin buttons on dark theme (subtle) */
.app-shell.dark input[type="number"]::-webkit-inner-spin-button,
.app-shell.dark input[type="number"]::-webkit-outer-spin-button {
  opacity: 0.25;
  background: transparent;
}

/* Scrollbar styling for WebKit - slightly more visible but not glaring */
html.dark ::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 8px; }
html.dark ::-webkit-scrollbar { background: transparent; width: 10px; }

/* compose-area and expanded panel styles */
.compose-area { display:flex; flex-direction:column; gap:8px; padding: 12px 20px; }
.expand-btn { width:44px; height:44px; border-radius:8px; border:1px solid var(--sidebar-border); background:transparent; color:var(--accent); cursor:pointer; display:inline-flex; align-items:center; justify-content:center; }
.theme-toggle { margin-left: 10px; background: transparent; border: 1px solid var(--sidebar-border); color: var(--accent); padding: 6px 8px; border-radius: 8px; cursor: pointer; font-size: 16px; }
.theme-toggle:hover { background: rgba(255,255,255,0.02); }
.app-shell.light .theme-toggle { color: var(--accent); border-color: rgba(43,124,255,0.12); }
.app-shell.dark .theme-toggle { color: var(--accent); border-color: rgba(255,255,255,0.06); }
.expand-panel { border:1px solid rgba(0,0,0,0.04); padding:12px; border-radius:10px; background:var(--sidebar-bg); display:flex; flex-direction:column; gap:12px; }
.top-fields { display:flex; gap:12px; flex-direction:column; }
.top-fields .field { display:flex; flex-direction:column; gap:6px; }

/* two-cols: left and right columns; left width 1, right width 2 (flex ratio 1:2) */
.two-cols {
  display: flex;
  gap: 12px;
  align-items: stretch;
}
.two-cols .left-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.two-cols .right-col {
  flex: 2;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.two-cols .left-col input,
.two-cols .left-col select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,0.06);
  background: var(--input-bg);
  color: var(--text);
  width: 100%;
  height: 42px;
  box-sizing: border-box;
  font-size: 15px;
}
.checkbox-row input[type="checkbox"] {
  width: 16px;           /* 标准大小 */
  height: 16px;
  margin: 0 6px 0 0;     /* 右边距保留，其他清零 */
  vertical-align: middle; /* 与文字中线对齐 */
  cursor: pointer;
}
.dropzone {
  flex: 1;                    /* 关键：占满 right-col 的所有剩��高度 */
  display: flex;              /* 内部内容居中 */
  flex-direction: column;
  justify-content: center;    /* 垂直居中 */
  align-items: center;        /* 水平居中 */
  min-height: 0;              /* 防止内容撑开，确保能压缩 */
  border: 2px dashed var(--dropzone-border, rgba(0,0,0,0.15));
  border-radius: 10px;
  background: var(--dropzone-bg, rgba(0,0,0,0.02));
  cursor: pointer;
  transition: all 0.2s ease;
}
.dropzone:hover {
  border-color: var(--accent);
  background: var(--glass);
}
.dropzone-inner {
  text-align: center;
  padding: 20px;
}
.app-shell.dark .two-cols .left-col input,
.app-shell.dark .two-cols .left-col select {
  background: var(--control-bg);
  border-color: var(--control-border);
}

@media (max-width: 800px) { .two-cols { flex-direction: column; } }

/* File list styles (keep them consistent with theme vars) */
.added-list { display:flex; flex-direction:column; gap:6px; margin-top:8px; }
.file-item { display:flex; align-items:center; gap:8px; background: rgba(255,255,255,0.02); padding:6px 8px; border-radius:8px; }
.file-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.file-delete-btn { background:transparent; border:1px solid rgba(0,0,0,0.06); color:var(--muted); padding:4px 8px; border-radius:6px; cursor:pointer; }
.app-shell.dark .file-item { background: rgba(255,255,255,0.02); }
.app-shell.dark .file-delete-btn { background:transparent; border-color: rgba(255,255,255,0.06); color: var(--muted); }
.app-shell.light .file-item { background: rgba(0,0,0,0.03); }
.app-shell.light .file-delete-btn { background:transparent; border-color: rgba(0,0,0,0.06); color: var(--muted); }

/* small helpers */
.result-actions { display:flex; }
</style>
