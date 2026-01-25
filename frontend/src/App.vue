<template>
  <div id="app" class="app-shell">
    <aside class="sidebar">
      <div class="user">
        <div class="avatar">U</div>
        <div class="username">用户</div>
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

      <div class="input-bar">
        <input v-model="question" @keyup.enter="send" :disabled="isLoading" placeholder="输入你的问题，按回车发送" />
        <button @click="send" :disabled="isLoading || !question.trim()">发送</button>
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
      finalResult: null
    };
  },
  methods: {
    hasBotContent() {
      // check if there is any bot message with non-empty content
      return this.messages.some(m => m.sender === 'bot' && (m.content || '').trim().length > 0);
    },

    async send() {
      this.error = null;
      const q = (this.question || '').trim();
      if (!q) {
        this.error = '问题不能为空';
        return;
      }

      // push user message and clear input
      this.messages.push({ sender: 'user', content: q });
      this.question = '';

      // prepare bot message placeholder
      this.messages.push({ sender: 'bot', content: '' });

      this.isLoading = true;

      try {
        const res = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q, stream: true })
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
        this.error = String(e);
      } finally {
        this.isLoading = false;
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
          let filename = (this.finalResult.title || 'result') + '.docx';
          const m = /filename\*?=([^;]+)/i.exec(cd);
          if (m) filename = m[1].trim().replace(/"/g, '');
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
:root {
  --sidebar-width: 260px;
  --bg: linear-gradient(135deg, #eef2f7 0%, #d7e1ec 100%);
  --accent: #2b7cff;
}

* { box-sizing: border-box; }
html, body, #app { height: 100%; }
body {
  margin: 0;
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
  background: var(--bg);
}

.app-shell {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.sidebar {
  width: var(--sidebar-width);
  background: white;
  border-right: 1px solid #e6ecf2;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.user { display: flex; align-items: center; margin-bottom: 20px; }
.avatar {
  width: 56px; height: 56px; border-radius: 50%; background: var(--accent); color: white; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:20px; margin-right:12px;
}
.username { font-weight: 600; }
.history { flex: 1; overflow: auto; }
.history h3 { margin-bottom: 8px; }
.placeholder { color: #9aa6b2; }

.main-area {
  flex: 1; display: flex; flex-direction: column; justify-content: space-between;
}

.content { padding: 24px; height: calc(100vh - 80px); overflow: auto; }
.messages { max-width: 900px; margin: 0 auto; display:flex; flex-direction:column; }
.message { padding: 12px 16px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); max-width: 75%; font-size: 16px; }
.message.system { background: transparent; box-shadow: none; color: #6b7280; max-width: 100%; }
.message.bot { background: white; color: #111; align-self: flex-start; }
.message.user { background: var(--accent); color: white; align-self: flex-end; }
.message.error { border-left: 4px solid #e74c3c; color: #e74c3c; align-self: flex-start; }
.message.loading { color: #2b7cff; align-self: flex-start; }
.chunk-text { margin: 0; font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; font-size: 16px; white-space: pre-wrap; word-break: break-word; }
.think { background: #f3f6f9; color: #374151; padding: 8px 10px; border-left: 3px solid #2b7cff; border-radius: 6px; margin-bottom: 8px; font-style: normal; }
.json-block { background: #0b1220; color: #d8eef8; padding: 12px; border-radius: 6px; overflow:auto; font-family: 'Courier New', monospace; font-size: 14px; white-space: pre-wrap; word-break: break-word; max-height: 420px; }
.result-actions { display:flex; justify-content: flex-start; }
.action-row { background: transparent; box-shadow: none; padding: 0; margin-bottom: 12px; align-self: flex-start; }
.download-btn { padding: 8px 14px; border-radius: 6px; background: #2ecc71; color: white; border: none; cursor: pointer; }

.input-bar { height: 80px; display:flex; gap: 12px; padding: 12px 20px; align-items: center; border-top: 1px solid #e6ecf2; background: white; }
.input-bar input { flex: 1; height: 52px; padding: 12px 14px; border-radius: 8px; border: 1px solid #d1d9e0; font-size: 16px; }
.input-bar button { width: 120px; height: 52px; border-radius: 8px; border: none; background: var(--accent); color: white; font-weight: 600; font-size: 16px; }

@media (max-width: 800px) {
  .sidebar { display: none; }
}
</style>
