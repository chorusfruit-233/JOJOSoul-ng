// JOJO Soul Web 版 - Pyodide 加载和游戏初始化

let pyodide = null;
let game = null;
let inputCallback = null;
let inputPrompt = '';

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
import os
from pathlib import Path
import builtins

# 设置命令行参数
sys.argv = ['JOJOSoul-ng.py', '--terminal']

# 模拟 input 函数
def web_input(prompt=""):
    # 将输入请求传递给 JavaScript
    import js
    js.request_input(prompt)
    # 等待用户输入
    return js.wait_for_input()

builtins.input = web_input
`);

        // 加载主游戏文件
        const response = await fetch('../JOJOSoul-ng.py');
        const gameCode = await response.text();

        // 加载显示管理器
        const displayResponse = await fetch('../display_manager.py');
        const displayCode = await displayResponse.text();

        // 执行显示管理器代码到全局命名空间
        await pyodide.runPythonAsync(displayCode);

        // 手动注册 display_manager 模块到 sys.modules
        await pyodide.runPythonAsync(`
import sys
# 将全局命名空间中的 display_manager 注册为模块
sys.modules['display_manager'] = type('Module', (), {
    'DisplayManager': DisplayManager,
    'display_manager': display_manager,
    'get_display_manager': get_display_manager,
    'set_display_mode': set_display_mode,
    'get_display_mode': get_display_mode,
})()
`);

        // 禁用 display_manager 的 GUI 功能
        await pyodide.runPythonAsync(`
import display_manager
display_manager.DisplayManager.gui_available = False
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

// 初始化 Web 显示管理器
async function initWebDisplay() {
    await pyodide.runPythonAsync(`
import sys
import os
from pathlib import Path
import builtins

# 模拟 print 函数
_original_print = print
def web_print(*args, **kwargs):
    import js
    text = ' '.join(str(arg) for arg in args)
    js.append_output(text)

print = web_print

# 获取存档路径（使用浏览器本地存储模拟）
class WebStorage:
    """Web 端存储模拟"""
    
    def __init__(self):
        self.data = {}
    
    def read(self, path):
        return self.data.get(str(path), None)
    
    def write(self, path, content):
        self.data[str(path)] = content
        return True
    
    def exists(self, path):
        return str(path) in self.data

# 创建 Web 存储实例
web_storage = WebStorage()

# 模拟 os.path.exists
_original_exists = os.path.exists
def web_exists(path):
    if 'savegame' in str(path):
        return web_storage.exists(path)
    return _original_exists(path)

os.path.exists = web_exists

# 模拟 open 函数
_original_open = open
class WebFile:
    def __init__(self, path, mode='r'):
        self.path = path
        self.mode = mode
        self.content = web_storage.read(path) or ''
        self.pos = 0
    
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

# 修改全局 open
builtins.open = web_open

# 修改 get_save_path 函数
def web_get_save_path():
    from pathlib import Path
    return Path('/web/savegame.dat')

# 直接替换全局命名空间中的 get_save_path 函数
import JOJOSoul_ng
JOJOSoul_ng.get_save_path = web_get_save_path

# 禁用 display_manager 的 GUI 功能
display_manager.DisplayManager.gui_available = False

# 创建 Web 显示管理器
class WebDisplayManager:
    """Web 端显示管理器"""
    
    def __init__(self):
        self.gui_available = False
        self.messages = []
    
    def show_message(self, title, message):
        """显示消息"""
        import js
        js.append_output(f"[{title}] {message}")
    
    def show_info(self, info):
        """显示信息"""
        import js
        js.append_output(info)
    
    def get_choice(self, title, choices):
        """获取用户选择"""
        import js
        js.append_output(f"{title}")
        for i, choice in enumerate(choices):
            js.append_output(f"{i+1}. {choice}")
        js.append_output("0. 取消")
        # 等待用户输入
        result = js.wait_for_input()
        try:
            choice_index = int(result) - 1
            if 0 <= choice_index < len(choices):
                return choices[choice_index]
        except:
            pass
        return None
    
    def get_yes_no(self, title, message):
        """获取是/否选择"""
        import js
        js.append_output(f"{title}")
        js.append_output(f"{message}")
        js.append_output("1=是, 2=否")
        # 等待用户输入
        result = js.wait_for_input()
        return result in ['1', 'y', 'yes', '是']
    
    def get_input(self, title, prompt):
        """获取文本输入"""
        import js
        result = js.wait_for_input()
        return result if result else None
    
    def show_battle_info(self, title, message):
        """显示战斗信息"""
        import js
        js.append_output(f"[{title}] {message}")
    
    def _sync_to_js(self):
        """同步消息到 JavaScript"""
        pass

# 创建全局 Web 显示管理器实例
web_display = WebDisplayManager()
    `);
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

// 请求用户输入
function requestInput(prompt) {
    inputPrompt = prompt;
    const inputField = document.getElementById('user-input');
    const submitBtn = document.getElementById('submit-btn');
    
    // 显示提示
    appendOutput(prompt, 'input-prompt');
    
    // 启用输入框
    inputField.disabled = false;
    submitBtn.disabled = false;
    inputField.value = '';
    inputField.focus();
}

// 等待用户输入（从 Python 调用）
function waitForInput() {
    return new Promise((resolve) => {
        inputCallback = resolve;
    });
}

// 提交用户输入
function submitInput() {
    const inputField = document.getElementById('user-input');
    const submitBtn = document.getElementById('submit-btn');
    const value = inputField.value.trim();
    
    // 禁用输入框
    inputField.disabled = true;
    submitBtn.disabled = true;
    
    // 显示用户输入
    appendOutput(value, 'choice');
    
    // 调用回调
    if (inputCallback) {
        inputCallback(value);
        inputCallback = null;
    }
}

// 主初始化函数
async function main() {
    // 设置输入事件监听器
    document.getElementById('submit-btn').addEventListener('click', submitInput);
    document.getElementById('user-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitInput();
        }
    });

    // 加载 Pyodide
    const pyodideLoaded = await initPyodide();
    if (!pyodideLoaded) return;

    // 加载游戏代码
    const gameLoaded = await loadGameCode();
    if (!gameLoaded) return;

    // 初始化 Web 显示管理器
    await initWebDisplay();

    // 隐藏加载界面，显示游戏界面
    document.getElementById('loading').style.display = 'none';
    document.getElementById('game-container').style.display = 'flex';

    // 启动游戏
    console.log('启动游戏...');
    await pyodide.runPythonAsync(`
game = Game()
game.display = web_display
game.player.display = web_display
game.run()
    `);
}

// 页面加载完成后初始化
window.addEventListener('load', main);
