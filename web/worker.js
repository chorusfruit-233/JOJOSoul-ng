/*!
 * JOJO Soul Web Worker
 * 在 Web Worker 中加载 Pyodide 并运行游戏。
 * 使用 SharedArrayBuffer + Atomics 实现同步阻塞的 input()，
 * 使主线程能自由渲染现代 HTML 模态框。
 *
 * 通信协议：
 *   Worker → Main:  postMessage({type:'print', text})     — 输出文本
 *   Worker → Main:  postMessage({type:'input', prompt})    — 请求输入
 *   Main → Worker:  通过 SharedArrayBuffer 写入结果 + Atomics.notify
 *   Worker 内部:    Atomics.wait 阻塞直到结果就绪
 */

importScripts(
    "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"
);

let pyodide = null;
// SharedArrayBuffer 布局 (Int32Array 视图):
//   [0] = 信号量: 0=空闲, 1=主线程已写入结果, 2=Worker 请求输入中
//   [1] = 结果长度 (字符数)
//   [2..N] = UTF-16 码元 (每个 Int32 存一个 char code)
// 总容量: 65536 个 Int32 → 约 64K 字符
let sharedView = null;

self.onmessage = async (e) => {
    const msg = e.data;

    if (msg.type === "init") {
        sharedView = new Int32Array(msg.sharedBuffer);
        try {
            pyodide = await loadPyodide();
            await setupEnvironment();
            self.postMessage({ type: "ready" });
        } catch (err) {
            self.postMessage({
                type: "error",
                message: "Pyodide 初始化失败: " + err.message,
            });
        }
    } else if (msg.type === "start") {
        try {
            await runGame();
        } catch (err) {
            self.postMessage({
                type: "error",
                message: "游戏运行失败: " + err.message,
            });
        }
    }
};

/**
 * 同步阻塞等待用户输入（从 Worker JS 层调用）。
 * 1. 通知主线程需要输入
 * 2. Atomics.wait 阻塞
 * 3. 主线程写入结果后 Atomics.notify 唤醒
 * 4. 从 SharedArrayBuffer 读取结果返回
 */
function syncInput(prompt) {
    // 通知主线程显示输入框
    self.postMessage({ type: "input", prompt: prompt });

    // 阻塞等待主线程写入结果
    // 信号量 [0]: 主线程写入结果后设为 1
    sharedView[0] = 0;
    Atomics.wait(sharedView, 0, 0);

    // 读取结果长度
    const length = sharedView[1];
    if (length < 0) {
        // 用户取消
        return "";
    }

    // 读取结果字符串 (UTF-16 码元)
    let result = "";
    for (let i = 0; i < length; i++) {
        result += String.fromCharCode(sharedView[2 + i]);
    }
    return result;
}

async function setupEnvironment() {
    await pyodide.runPythonAsync(`
import sys
sys.argv = ['JOJOSoul-ng.py', '--terminal']
`);

    // 注册 JS 函数到 Pyodide
    // syncInput 是同步阻塞的 JS 函数，Python 可直接调用获取字符串结果
    pyodide.registerJsModule("webgui", {
        append_output: (text) =>
            self.postMessage({ type: "print", text: String(text) }),
        sync_input: (prompt) => syncInput(String(prompt)),
    });

    // 设置同步的 print / input
    await pyodide.runPythonAsync(`
import builtins
import webgui

_output_buffer = []

def web_print(*args, **kwargs):
    text = ' '.join(str(arg) for arg in args)
    _output_buffer.append(text)
    webgui.append_output(text)

def web_input(prompt=""):
    # 将最近输出作为上下文附带在 prompt 中
    # 主线程会把这些上下文显示在模态框里
    context = '\\n'.join(_output_buffer[-40:])
    _output_buffer.clear()
    if context:
        full_prompt = context + '\\n\\n>>> ' + str(prompt)
    else:
        full_prompt = str(prompt)
    # 调用同步阻塞的 JS 函数
    result = webgui.sync_input(full_prompt)
    return result

builtins.print = web_print
builtins.input = web_input
`);
}

async function runGame() {
    // 加载显示管理器
    const displayResponse = await fetch("../display_manager.py");
    const displayCode = await displayResponse.text();
    await pyodide.runPythonAsync(displayCode);

    await pyodide.runPythonAsync(`
import sys
sys.modules['display_manager'] = type('Module', (), {
    'DisplayManager': DisplayManager,
    'display_manager': display_manager,
    'get_display_manager': get_display_manager,
    'set_display_mode': set_display_mode,
    'get_display_mode': get_display_mode,
})()
`);

    // 加载游戏主文件（剥离 __main__ 守卫）
    const response = await fetch("../JOJOSoul-ng.py");
    let gameCode = await response.text();
    gameCode = gameCode.replace(
        /if __name__ == .__main__.:[\s\S]*$/,
        ""
    );
    await pyodide.runPythonAsync(gameCode);

    // 设置 Web 环境（存储、存档路径）
    await pyodide.runPythonAsync(`
import os, builtins
from pathlib import Path

class WebStorage:
    def __init__(self):
        self.data = {}
    def read(self, path):
        return self.data.get(str(path), None)
    def write(self, path, content):
        self.data[str(path)] = content
        return True
    def exists(self, path):
        return str(path) in self.data

web_storage = WebStorage()

_original_exists = os.path.exists
def web_exists(path):
    if 'savegame' in str(path):
        return web_storage.exists(path)
    return _original_exists(path)
os.path.exists = web_exists

_original_open = open
class WebFile:
    def __init__(self, path, mode='r'):
        self.path = path
        self.mode = mode
        self.content = web_storage.read(path) or ''
    def read(self):
        return self.content
    def write(self, content):
        self.content += content
    def close(self):
        if 'w' in self.mode:
            web_storage.write(self.path, self.content)

def web_open(path, mode='r'):
    if 'savegame' in str(path):
        return WebFile(path, mode)
    return _original_open(path, mode)
builtins.open = web_open

def web_get_save_path():
    return Path('/web/savegame.dat')
get_save_path = web_get_save_path
`);

    // 运行游戏
    self.postMessage({ type: "status", message: "游戏启动中..." });
    await pyodide.runPythonAsync(`
game = Game()
game.run()
`);
    self.postMessage({ type: "done" });
}
