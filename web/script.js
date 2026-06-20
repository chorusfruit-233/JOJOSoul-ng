// JOJO Soul Web 版 - Pyodide 加载和游戏初始化

let pyodide = null;
let modalCallback = null;

// 初始化 Pyodide
async function initPyodide() {
    try {
        console.log('正在加载 Pyodide...');
        pyodide = await loadPyodide();
        console.log('Pyodide 加载完成！');
        return true;
    } catch (error) {
        console.error('Pyodide 加载失败:', error);
        showError('游戏加载失败，请刷新页面重试。');
        return false;
    }
}

// 加载游戏代码
async function loadGameCode() {
    try {
        // 先设置命令行参数和模拟 input 函数
        await pyodide.runPythonAsync(`
import sys
sys.argv = ['JOJOSoul-ng.py', '--terminal']
`);

        // 注册 JavaScript 函数到 Pyodide
        // 注意：不使用 'js' 作为模块名，避免遮蔽 Pyodide 内置的 js 全局模块
        // （内置 js 模块提供 js.prompt/js.alert/js.confirm 等同步阻塞对话框）
        // Web 版交互通过终端 DisplayManager + 重定向的 print/input 完成，
        // 此处仅需注册 append_output 用于将 print 输出写入页面日志区。
        pyodide.registerJsModule('webgui', {
            append_output: appendOutput
        });

        // 设置 input 函数模拟
        // 关键：使用浏览器原生 js.prompt（同步阻塞），使同步 Python 代码
        // 能真正等待用户输入。Pyodide 同步 Python 无法 await Promise。
        await pyodide.runPythonAsync(`
import builtins
import webgui

# 最近输出缓冲：让 input 对话框能显示上下文（菜单选项等）
_output_buffer = []

def web_print(*args, **kwargs):
    import webgui
    text = ' '.join(str(arg) for arg in args)
    _output_buffer.append(text)
    webgui.append_output(text)

def web_input(prompt=""):
    import js
    # 将最近的输出作为上下文显示在 prompt 对话框中，
    # 这样用户在选择时能看到菜单/战斗状态等信息。
    context = '\\n'.join(_output_buffer[-30:])
    _output_buffer.clear()
    full_prompt = (context + '\\n\\n' + str(prompt)) if context else str(prompt)
    result = js.prompt(full_prompt)
    # 用户点击取消时返回空字符串（避免 .strip() 在 None 上崩溃）
    if result is None:
        return ""
    return str(result)

builtins.print = web_print
builtins.input = web_input
`);

        // 加载主游戏文件
        const response = await fetch('../JOJOSoul-ng.py');
        let gameCode = await response.text();

        // 剥离 __main__ 守卫块，避免游戏在加载时自动启动
        // （Pyodide 全局命名空间中 __name__ == "__main__"，会导致 game.run() 立即执行）
        gameCode = gameCode.replace(/if __name__ == .__main__.:[\s\S]*$/, '');

        // 加载显示管理器
        const displayResponse = await fetch('../display_manager.py');
        const displayCode = await displayResponse.text();

        // 执行显示管理器代码到全局命名空间
        await pyodide.runPythonAsync(displayCode);

        // 手动注册 display_manager 模块到 sys.modules
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

        // 执行游戏代码到全局命名空间
        await pyodide.runPythonAsync(gameCode);

        console.log('游戏代码加载完成！');
        return true;
    } catch (error) {
        console.error('游戏代码加载失败:', error);
        showError('游戏代码加载失败: ' + error.message);
        return false;
    }
}

// 初始化 Web 环境（存储、文件 IO、存档路径覆盖）
async function initWebDisplay() {
    try {
        await pyodide.runPythonAsync(`
import sys
import os
from pathlib import Path
import builtins

# 注：print/input 的 web 模拟已在 loadGameCode 中设置（带输出缓冲上下文）

# Web 存储模拟（存档持久化到内存，页面刷新后丢失）
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
    from pathlib import Path
    return Path('/web/savegame.dat')

# 游戏代码已在全局命名空间中执行，直接覆盖 get_save_path
get_save_path = web_get_save_path
`);
    } catch (error) {
        console.error('Web 环境初始化失败:', error);
        showError('Web 环境初始化失败: ' + error.message);
        return false;
    }
    return true;
}

// 显示错误
function showError(message) {
    document.getElementById('loading').innerHTML = `
        <div style="color: #ff6b6b; text-align: center; padding: 20px;">
            <h2>错误</h2>
            <p>${message}</p>
        </div>
    `;
}

// 添加输出到游戏界面
function appendOutput(text, className = '') {
    const outputDiv = document.getElementById('game-output');
    const p = document.createElement('p');
    p.textContent = text;
    if (className) {
        p.className = className;
    }
    outputDiv.appendChild(p);
    outputDiv.scrollTop = outputDiv.scrollHeight;
}

// 显示消息框（类似 easygui.msgbox）
function showMessageBox(title, message) {
    return new Promise((resolve) => {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-message').textContent = message;
        document.getElementById('modal-choices').innerHTML = '';
        document.getElementById('modal-input-group').style.display = 'none';
        
        const footer = document.getElementById('modal-footer');
        footer.innerHTML = '<button class="button">确定</button>';
        
        footer.querySelector('.button').addEventListener('click', () => {
            closeModal();
            resolve();
        });
        
        showModal();
    });
}

// 显示选择框（类似 easygui.choicebox）
function showChoiceBox(title, choices) {
    return new Promise((resolve) => {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-message').textContent = '';
        document.getElementById('modal-input-group').style.display = 'none';
        
        const choicesDiv = document.getElementById('modal-choices');
        choicesDiv.innerHTML = '';
        
        choices.forEach((choice, index) => {
            const btn = document.createElement('button');
            btn.className = 'choice-button';
            btn.textContent = choice;
            btn.addEventListener('click', () => {
                closeModal();
                resolve(choice);
            });
            choicesDiv.appendChild(btn);
        });
        
        const footer = document.getElementById('modal-footer');
        footer.innerHTML = '<button id="modal-cancel" class="button secondary">取消</button>';
        
        footer.querySelector('#modal-cancel').addEventListener('click', () => {
            closeModal();
            resolve(null);
        });
        
        showModal();
    });
}

// 显示按钮框（类似 easygui.buttonbox）
function showButtonBox(title, message, buttons) {
    return new Promise((resolve) => {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-message').textContent = message;
        document.getElementById('modal-input-group').style.display = 'none';
        
        const choicesDiv = document.getElementById('modal-choices');
        choicesDiv.innerHTML = '';
        
        buttons.forEach((button) => {
            const btn = document.createElement('button');
            btn.className = 'choice-button';
            btn.textContent = button;
            btn.addEventListener('click', () => {
                closeModal();
                resolve(button);
            });
            choicesDiv.appendChild(btn);
        });
        
        const footer = document.getElementById('modal-footer');
        footer.innerHTML = '<button id="modal-cancel" class="button secondary">取消</button>';
        
        footer.querySelector('#modal-cancel').addEventListener('click', () => {
            closeModal();
            resolve(null);
        });
        
        showModal();
    });
}

// 显示输入框（类似 easygui.enterbox）
function showInputBox(title, prompt) {
    return new Promise((resolve) => {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-message').textContent = prompt;
        document.getElementById('modal-choices').innerHTML = '';
        document.getElementById('modal-input-group').style.display = 'block';
        
        const input = document.getElementById('modal-input');
        input.value = '';
        
        const footer = document.getElementById('modal-footer');
        footer.innerHTML = '<button class="button">确定</button> <button id="modal-cancel" class="button secondary">取消</button>';
        
        footer.querySelector('.button').addEventListener('click', () => {
            closeModal();
            resolve(input.value.trim() || null);
        });
        
        footer.querySelector('#modal-cancel').addEventListener('click', () => {
            closeModal();
            resolve(null);
        });
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                closeModal();
                resolve(input.value.trim() || null);
            }
        });
        
        showModal();
        setTimeout(() => input.focus(), 100);
    });
}

// 显示模态框
function showModal() {
    document.getElementById('modal-overlay').style.display = 'flex';
}

// 关闭模态框
function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

// 主初始化函数
async function main() {
    try {
        const pyodideLoaded = await initPyodide();
        if (!pyodideLoaded) return;

        const gameLoaded = await loadGameCode();
        if (!gameLoaded) return;

        const webReady = await initWebDisplay();
        if (!webReady) return;

        document.getElementById('loading').style.display = 'none';
        document.getElementById('game-container').style.display = 'flex';

        console.log('启动游戏...');
        // run() 会读取 sys.argv 中的 '--terminal' 并创建终端 DisplayManager，
        // 其所有交互通过已重定向的 print(→ append_output) 和 input(→ js.prompt) 完成。
        await pyodide.runPythonAsync(`
game = Game()
game.run()
        `);
    } catch (error) {
        console.error('游戏运行失败:', error);
        showError('游戏运行失败: ' + error.message);
    }
}

window.addEventListener('load', main);
