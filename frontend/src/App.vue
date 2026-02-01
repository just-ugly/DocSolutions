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
            <div class="field"><label>问题输出 (Query)</label><input class="main-input" v-model="question" :disabled="isLoading" /></div>
            <div class="field"><label>目录 (Menu)</label><input v-model="menu" /></div>
            <div class="field"><label>提纲 (Outline)</label><textarea v-model="outline"></textarea></div>
            <div class="field"><label>示例 (Example)</label><textarea v-model="example"></textarea></div>
          </div>

          <div class="two-cols">
            <div class="left-col">
              <label>预期文档字数</label>
              <input type="number" v-model.number="file_num" min="1" placeholder="仅数字" />

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
                  <p v-if="docFiles.length" class="added-list">已添加: <span v-for="(f,i) in docFiles" :key="i">{{ f.name }}<span v-if="i < docFiles.length - 1">, </span></span></p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="input-bar">
          <input class="main-input" v-model="question" @keyup.enter="send(false)" :disabled="isLoading" placeholder="输入你的问题，按回车发送" />
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
      messages: [
        { sender: 'system', content: '请输入一个问题，按回车或点击发送开始。' }
      ],
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
      file_num: null,
      style: '',
      first_page_toc: false,
      docFiles: [],
      fileDropOver: false
    };
  },
  created() {
    // Load theme from localStorage if available and apply class to documentElement so variables affect body
    try {
      const t = localStorage.getItem('theme');
      if (t === 'light' || t === 'dark') this.theme = t;
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
        // append, but keep only metadata for now
        this.docFiles.push(...files);
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
        this.docFiles.push(...files);
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
        // build payload including new options
        const payload = {
          question: q,
          stream: true,
          docx_create: !!docx_create,
          file_num: this.file_num || null,
          style: this.style || '',
          first_page_toc: !!this.first_page_toc,
          files: this.docFiles.map(f => ({ name: f.name, size: f.size, type: f.type })),
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

        if (first.index > 0) {
          segments.push({ type: 'text', content: rest.slice(0, first.index) });
          rest = rest.slice(first.index);
        }

        if (first.type === 'think') {
          if (thinkClose !== -1 && thinkClose > thinkOpen) {
            const inner = rest.substring(7, thinkClose);
            segments.push({ type: 'think', content: inner.trim() });
            rest = rest.slice(thinkClose + 8);
          } else {
            const inner = rest.substring(7);
            segments.push({ type: 'think', content: inner.trim() });
            rest = '';
          }
        } else {
          const langMatch = rest.match(/^```(\w*)\s*\n?/);
          let lang = '';
          let afterFenceIndex = 3;
          if (langMatch) {
            lang = (langMatch[1] || '').toLowerCase();
            afterFenceIndex = langMatch[0].length;
          }

          const closeIdx = rest.indexOf('\n```', afterFenceIndex);
          const altCloseIdx = rest.indexOf('```', afterFenceIndex);
          const endIdx = closeIdx !== -1 ? closeIdx : altCloseIdx;

          if (endIdx !== -1) {
            const codeContent = rest.substring(afterFenceIndex, endIdx).replace(/^\n/, '');
            if (lang === 'json') {
              try {
                const obj = JSON.parse(codeContent);
                segments.push({ type: 'json', content: JSON.stringify(obj, null, 2) });
              } catch (e) {
                segments.push({ type: 'json', content: codeContent });
              }
            } else {
              segments.push({ type: 'code', content: codeContent });
            }
            const closingFenceIdx = rest.indexOf('```', afterFenceIndex);
            if (closingFenceIdx !== -1) rest = rest.slice(closingFenceIdx + 3);
            else rest = '';
          } else {
            const codeContent = rest.substring(afterFenceIndex).replace(/^\n/, '');
            if (lang === 'json') {
              try {
                const obj = JSON.parse(codeContent);
                segments.push({ type: 'json', content: JSON.stringify(obj, null, 2) });
              } catch (e) {
                segments.push({ type: 'json', content: codeContent });
              }
            } else {
              segments.push({ type: 'code', content: codeContent });
            }
            rest = '';
          }
        }
      }

      return segments;
    },

    downloadResult() {
      // If structured finalResult, POST to /api/docx to generate docx; fallback to JSON download
      if (this.finalResult && typeof this.finalResult === 'object') {
        // send to backend and download
        fetch('/api/docx', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.finalResult)
        }).then(async res => {
          if (!res.ok) {
            const t = await res.text();
            this.error = '下载失败: ' + t;
            return;
          }
          const blob = await res.blob();
          const cd = res.headers.get('content-disposition') || '';

          // helper to parse Content-Disposition header robustly
          const parseFilenameFromContentDisposition = (cdHeader) => {
            if (!cdHeader) return null;
            // try filename* (RFC5987) first (may be percent-encoded)
            const filenameStarMatch = cdHeader.match(/filename\*=(?:[\w-]+''?)?([^;\n]+)/i);
            if (filenameStarMatch && filenameStarMatch[1]) {
              let raw = filenameStarMatch[1].trim();
              // strip surrounding quotes (' or ")
              raw = raw.replace(/^['"]|['"]$/g, '');
              try {
                return decodeURIComponent(raw);
              } catch (e) {
                return raw;
              }
            }

            // fallback to filename=
            const filenameMatch = cdHeader.match(/filename=([^;\n]+)/i);
            if (filenameMatch && filenameMatch[1]) {
              let raw = filenameMatch[1].trim();
              raw = raw.replace(/^['"]|['"]$/g, '');
              return raw;
            }

            return null;
          };

          let filename = parseFilenameFromContentDisposition(cd) || (this.finalResult.title || 'result') + '.docx';
          // strip any path components just in case
          filename = filename.split(/[\\\/]/).pop();
           const url = URL.createObjectURL(blob);
           const a = document.createElement('a');
           a.href = url;
           a.download = filename;
           document.body.appendChild(a);
           a.click();
           a.remove();
           URL.revokeObjectURL(url);
         }).catch(e => this.error = String(e));
         return;
       }

      const content = this.messages.filter(m => m.sender === 'bot').map(m => m.content).join('\n');
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'result.txt';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
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
  --accent-2: #ffd27a; /* gold highlight */
  --avatar-bg: linear-gradient(135deg,#0c0c0c 0%, #2b1f0a 100%);
  --avatar-shadow: 0 4px 12px rgba(0,0,0,0.15);
  --avatar-border: 1px solid rgba(255,255,255,0.06);
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
}

/* Mirror vars on the html element so documentElement.classList = 'dark'|'light' controls page colors */
html.dark {
  --sidebar-width: 260px;
  --bg: linear-gradient(180deg, #071017 0%, #0b1418 100%);
  --accent: #b8860b; /* black-gold */
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
  --accent-2: #ffd27a;
  --avatar-bg: linear-gradient(135deg,#0c0c0c 0%, #2b1f0a 100%);
  --avatar-shadow: 0 4px 12px rgba(0,0,0,0.15);
  --avatar-border: 1px solid rgba(255,255,255,0.06);
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
.input-bar { height: 84px; display:flex; gap: 12px; padding: 12px 20px; align-items: center; border-top: 1px solid rgba(0,0,0,0.04); background: var(--sidebar-bg); }
.input-bar input { flex: 1; height: 56px; padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.06); background: var(--input-bg); color: var(--text); font-size: 16px; }
.input-bar input::placeholder { color: var(--muted); }
.input-bar button { width: 120px; height: 56px; border-radius: 12px; border: none; background: linear-gradient(90deg, var(--accent), var(--accent-2)); color: #081217; font-weight: 700; font-size: 16px; box-shadow: 0 8px 20px rgba(184,134,11,0.12); cursor: pointer; }

.theme-toggle { margin-left: 10px; background: transparent; border: 1px solid var(--sidebar-border); color: var(--accent); padding: 6px 8px; border-radius: 8px; cursor: pointer; font-size: 16px; }
.app-shell.light .theme-toggle { color: var(--accent); border-color: rgba(43,124,255,0.12); }

/* placeholder color should adapt to theme */
.input-bar input::placeholder { color: var(--muted); }

@media (max-width: 800px) { .sidebar { display: none; } }

/* fade-out/fade-in transition for theme toggling */
html.theme-fading {
  transition: background 180ms ease-in-out, color 180ms ease-in-out;
}

/* compose-area and expanded panel styles */
.compose-area { display:flex; flex-direction:column; gap:8px; padding: 12px 20px; }
.expand-btn { width:44px; height:44px; border-radius:8px; border:1px solid var(--sidebar-border); background:transparent; color:var(--accent); cursor:pointer; display:inline-flex; align-items:center; justify-content:center; }
.expand-panel { border:1px solid rgba(0,0,0,0.04); padding:12px; border-radius:10px; background:var(--sidebar-bg); display:flex; flex-direction:column; gap:12px; }
.top-fields { display:flex; gap:12px; flex-direction:column; }
.top-fields .field { display:flex; flex-direction:column; gap:6px; }
.top-fields input, .top-fields textarea { width:100%; padding:8px; border-radius:8px; border:1px solid rgba(0,0,0,0.06); background:var(--input-bg); color:var(--text); }
.two-cols { display:flex; gap:12px; }
.left-col { flex:1; display:flex; flex-direction:column; gap:8px; }
.right-col { flex:2; }
.dropzone { border:2px dashed rgba(0,0,0,0.12); border-radius:10px; padding:18px; height:140px; display:flex; align-items:center; justify-content:center; cursor:pointer; background:transparent; }
.dropzone-inner { text-align:center; color:var(--muted); }
.added-list { color:var(--text); margin-top:8px; font-size:13px; }
.checkbox-row { display:flex; align-items:center; gap:8px; }
.main-input { flex:1; height:56px; padding:12px 14px; border-radius:12px; border:1px solid rgba(0,0,0,0.06); background:var(--input-bg); color:var(--text); font-size:16px; }
.btn-send, .btn-gen { width:120px; height:56px; border-radius:12px; border:none; background:linear-gradient(90deg,var(--accent),var(--accent-2)); color:#081217; font-weight:700; font-size:16px; cursor:pointer; }
.input-bar { height:84px; display:flex; gap:12px; padding:0; align-items:center; border-top:1px solid rgba(0,0,0,0.04); background:var(--sidebar-bg); }
.compose-area .input-bar { padding:12px 0 0 0; }
</style>
