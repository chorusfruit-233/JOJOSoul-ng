// JOJO Soul Web 版 - Pyodide 加载和游戏初始化

let pyodide = null;
let game = null;

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
        // 加载主游戏文件
        const response = await fetch('../JOJOSoul-ng.py');
        const gameCode = await response.text();

        // 加载显示管理器
        const displayResponse = await fetch('../display_manager.py');
        const displayCode = await displayResponse.text();

        // 先执行显示管理器代码
        await pyodide.runPythonAsync(displayCode);

        // 修改 display_manager，禁用 easygui
        await pyodide.runPythonAsync(`
import display_manager
display_manager.DisplayManager.gui_available = False
`);

        // 执行游戏代码
        await pyodide.runPythonAsync(gameCode);

        console.log('游戏代码加载完成！');
        return true;
    } catch (error) {
        console.error('游戏代码加载失败:', error);
        showError('游戏代码加载失败，请刷新页面重试。');
        return false;
    }
}

// 初始化 Web 显示管理器
async function initWebDisplay() {
    await pyodide.runPythonAsync(`
import sys
import os
from pathlib import Path

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
import builtins
builtins.open = web_open

# 修改 get_save_path 函数
def web_get_save_path():
    from pathlib import Path
    return Path('/web/savegame.dat')

# 注入到全局命名空间
import sys
sys.modules['JOJOSoul_ng'] = type('Module', (), {'get_save_path': web_get_save_path})()

# 创建 Web 显示管理器
class WebDisplayManager:
    """Web 端显示管理器"""
    
    def __init__(self):
        self.gui_available = False
        self.messages = []
    
    def show_message(self, title, message):
        """显示消息"""
        self.messages.append({'type': 'message', 'title': title, 'content': message})
        self._sync_to_js()
    
    def show_info(self, info):
        """显示信息"""
        self.messages.append({'type': 'info', 'content': info})
        self._sync_to_js()
    
    def get_choice(self, title, choices):
        """获取用户选择"""
        self.messages.append({'type': 'choice', 'title': title, 'choices': choices})
        self._sync_to_js()
        # 简化版本：返回第一个选项
        return choices[0] if choices else None
    
    def get_yes_no(self, title, message):
        """获取是/否选择"""
        self.messages.append({'type': 'yesno', 'title': title, 'message': message})
        self._sync_to_js()
        return True  # 简化版本
    
    def get_input(self, title, prompt):
        """获取文本输入"""
        self.messages.append({'type': 'input', 'title': title, 'prompt': prompt})
        self._sync_to_js()
        return "勇者"  # 简化版本
    
    def show_battle_info(self, title, message):
        """显示战斗信息"""
        self.messages.append({'type': 'battle', 'title': title, 'content': message})
        self._sync_to_js()
    
    def _sync_to_js(self):
        """同步消息到 JavaScript"""
        import json
        messages_json = json.dumps(self.messages)
        # 这里需要实现与 JavaScript 的通信
        # 简化版本：打印到控制台
        print(f"WebDisplay: {messages_json}")

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

// 主初始化函数
async function main() {
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
import sys
sys.argv = ['JOJOSoul-ng.py', '--terminal']
game = Game()
game.display = web_display
game.player.display = web_display
game.run()
    `);
}

// 页面加载完成后初始化
window.addEventListener('load', main);