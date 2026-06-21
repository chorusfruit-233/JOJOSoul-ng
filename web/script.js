/*!
 * JOJO Soul Web 版 - 主线程 UI
 * 管理现代 HTML 模态框，与 Web Worker 中的 Pyodide 通信。
 * 用户输入通过 SharedArrayBuffer 传回 Worker。
 */

let worker = null;
let sharedBuffer = null;
let sharedView = null;
const SHARED_BUFFER_SIZE = 65536; // Int32 个数

// DOM 元素引用
const $loading = () => document.getElementById("loading");
const $container = () => document.getElementById("game-container");
const $output = () => document.getElementById("game-output");
const $modal = () => document.getElementById("modal-overlay");
const $modalTitle = () => document.getElementById("modal-title");
const $modalBody = () => document.getElementById("modal-body");
const $modalInput = () => document.getElementById("modal-input");
const $modalInputGroup = () => document.getElementById("modal-input-group");
const $modalActions = () => document.getElementById("modal-actions");

// ---- 初始化 ----
async function main() {
    try {
        // 检查 SharedArrayBuffer 是否可用（需要 COOP/COEP）
        if (typeof SharedArrayBuffer === "undefined") {
            showCOIError();
            return;
        }

        // 创建 SharedArrayBuffer
        sharedBuffer = new SharedArrayBuffer(
            SHARED_BUFFER_SIZE * 4
        );
        sharedView = new Int32Array(sharedBuffer);

        // 创建 Web Worker
        worker = new Worker("worker.js");

        worker.onmessage = (e) => handleMessage(e.data);
        worker.onerror = (e) => {
            showError("Worker 错误: " + e.message);
        };

        // 初始化 Pyodide（在 Worker 中）
        updateLoadingStatus("正在加载 Pyodide...");
        worker.postMessage({
            type: "init",
            sharedBuffer: sharedBuffer,
        });
    } catch (err) {
        showError("初始化失败: " + err.message);
    }
}

// ---- 处理 Worker 消息 ----
function handleMessage(msg) {
    switch (msg.type) {
        case "ready":
            updateLoadingStatus("正在加载游戏代码...");
            worker.postMessage({ type: "start" });
            break;

        case "status":
            updateLoadingStatus(msg.message);
            break;

        case "print":
            appendOutput(msg.text);
            break;

        case "print_html":
            appendOutputHTML(msg.html);
            break;

        case "input":
            handleInputRequest(msg.prompt);
            break;

        case "done":
            appendOutput("游戏已结束。", "system");
            showRestartHint();
            break;

        case "gameover":
            appendOutput("游戏结束。", "system");
            showRestartHint();
            break;

        case "error":
            showError(msg.message);
            break;
    }
}

// ---- 输出区管理 ----
function appendOutput(text, className = "") {
    const output = $output();
    const p = document.createElement("p");
    p.textContent = text;
    if (className) p.className = className;
    output.appendChild(p);
    output.scrollTop = output.scrollHeight;
}

function appendOutputHTML(html) {
    const output = $output();
    const div = document.createElement("div");
    div.innerHTML = html;
    output.appendChild(div);
    output.scrollTop = output.scrollHeight;
}

// ---- 加载状态 ----
function updateLoadingStatus(text) {
    const el = document.getElementById("loading-text");
    if (el) el.textContent = text;
}

function showGameUI() {
    $loading().style.display = "none";
    $container().style.display = "flex";
}

// ---- 输入请求处理（核心：显示模态框 → 用户输入 → 写入 SAB → 唤醒 Worker）----
function handleInputRequest(prompt) {
    // 首次收到输入请求时，切换到游戏界面
    if ($loading().style.display !== "none") {
        showGameUI();
    }

    // 解析 prompt：游戏终端模式把菜单上下文和提示符一起传过来
    // 格式: "菜单输出...\n\n>>> 请选择（输入数字）: "
    const lines = prompt.split("\n");
    const promptLine = lines[lines.length - 1].replace(/^>>>\s*/, "");
    const context = lines.slice(0, -1).join("\n").trim();

    // 显示输入模态框
    $modalTitle().textContent = "游戏输入";
    $modalBody().innerHTML = "";

    // 上下文区（菜单选项等）
    if (context) {
        const ctxDiv = document.createElement("div");
        ctxDiv.className = "input-context";
        ctxDiv.textContent = context;
        $modalBody().appendChild(ctxDiv);
    }

    // 提示文本
    const promptP = document.createElement("p");
    promptP.className = "input-prompt-text";
    promptP.textContent = promptLine;
    $modalBody().appendChild(promptP);

    // 输入框
    $modalInputGroup().style.display = "block";
    $modalInput().value = "";
    $modalInput().placeholder = promptLine;

    // 操作按钮
    $modalActions().innerHTML = "";
    const submitBtn = document.createElement("button");
    submitBtn.className = "btn btn-primary";
    submitBtn.textContent = "确认";
    const cancelBtn = document.createElement("button");
    cancelBtn.className = "btn btn-secondary";
    cancelBtn.textContent = "取消";

    $modalActions().appendChild(cancelBtn);
    $modalActions().appendChild(submitBtn);

    $modal().classList.add("active");
    setTimeout(() => $modalInput().focus(), 50);

    function submit() {
        const value = $modalInput().value;
        closeInputModal();
        sendInputResult(value);
    }

    function cancel() {
        closeInputModal();
        sendInputResult(null);
    }

    submitBtn.onclick = submit;
    cancelBtn.onclick = cancel;
    $modalInput().onkeydown = (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            submit();
        }
    };
}

function closeInputModal() {
    $modal().classList.remove("active");
    $modalInputGroup().style.display = "none";
}

/**
 * 将用户输入结果写入 SharedArrayBuffer 并唤醒 Worker
 */
function sendInputResult(value) {
    if (value === null) {
        // 用户取消
        sharedView[0] = 0;
        sharedView[1] = -1; // 标记为取消
    } else {
        // 写入字符串 (UTF-16 码元)
        const len = Math.min(value.length, SHARED_BUFFER_SIZE - 2);
        sharedView[1] = len;
        for (let i = 0; i < len; i++) {
            sharedView[2 + i] = value.charCodeAt(i);
        }
        sharedView[0] = 0;
    }

    // 唤醒 Worker 中阻塞的 Atomics.wait
    Atomics.store(sharedView, 0, 1);
    Atomics.notify(sharedView, 0, 1);
}

// ---- 游戏结束提示 ----
function showRestartHint() {
    const output = $output();
    const div = document.createElement("div");
    div.className = "restart-hint";
    div.innerHTML =
        '<button class="btn btn-primary" onclick="location.reload()">' +
        "重新开始</button>";
    output.appendChild(div);
    output.scrollTop = output.scrollHeight;
}

// ---- 错误处理 ----
function showError(message) {
    const loading = $loading();
    if (loading.style.display !== "none") {
        loading.innerHTML = `
            <div class="error-box">
                <h2>出错了</h2>
                <p>${escapeHtml(message)}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    重新加载
                </button>
            </div>
        `;
    } else {
        appendOutput("错误: " + message, "error");
    }
}

function showCOIError() {
    $loading().innerHTML = `
        <div class="error-box">
            <h2>需要跨域隔离</h2>
            <p>Web 版需要 SharedArrayBuffer 支持，正在通过 Service Worker
               注入 COOP/COEP 头。请刷新页面重试。</p>
            <p>如果多次刷新无效，请使用支持 COOP/COEP 的浏览器
              （Chrome/Edge/Firefox 最新版）。</p>
            <button class="btn btn-primary" onclick="location.reload()">
                刷新页面
            </button>
        </div>
    `;
}

function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
}

// ---- 启动 ----
window.addEventListener("load", main);
