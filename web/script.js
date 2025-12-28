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
        pyodide.registerJsModule('js', {
            show_message_box: showMessageBox,
            show_choice_box: showChoiceBox,
            show_button_box: showButtonBox,
            show_input_box: showInputBox,
            append_output: appendOutput,
            request_input: requestInput,
            wait_for_input: waitForInput
        });

        // 设置 input 函数模拟
        await pyodide.runPythonAsync(`
import builtins
import js

# 模拟 input 函数
def web_input(prompt=""):
    # 使用对话框获取输入
    result = js.show_input_box("输入", prompt)
    return result

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

# Web 存储模拟
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

import JOJOSoul_ng
JOJOSoul_ng.get_save_path = web_get_save_path

display_manager.DisplayManager.gui_available = False

# Web 显示管理器 - 类似 easygui
class WebDisplayManager:
    def __init__(self):
        self.gui_available = False
        self.messages = []
    
    def show_message(self, title, message):
        import js
        js.show_message_box(title, message)
    
    def show_info(self, info):
        import js
        js.show_message_box("信息", info)
    
    def get_choice(self, title, choices):
        import js
        return js.show_choice_box(title, choices)
    
    def get_yes_no(self, title, message):
        import js
        return js.show_button_box(title, message, ["是", "否"]) == "是"
    
    def get_input(self, title, prompt):
        import js
        return js.show_input_box(title, prompt)
    
    def show_battle_info(self, title, message):
        import js
        js.show_message_box(title, message)
    
    def _sync_to_js(self):
        pass

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
    const pyodideLoaded = await initPyodide();
    if (!pyodideLoaded) return;

    const gameLoaded = await loadGameCode();
    if (!gameLoaded) return;

    await initWebDisplay();

    document.getElementById('loading').style.display = 'none';
    document.getElementById('game-container').style.display = 'flex';

    console.log('启动游戏...');
    await pyodide.runPythonAsync(`
game = Game()
game.display = web_display
game.player.display = web_display
game.run()
    `);
}

window.addEventListener('load', main);
