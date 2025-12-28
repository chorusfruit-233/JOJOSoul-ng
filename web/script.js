// JOJO Soul Web 版 - Pyodide 加载和游戏初始化

let pyodide = null;
let game = null;

// 初始化 Pyodide
async function initPyodide() {
    try {
        console.log('正在加载 Pyodide...');
        pyodide = await loadPyodide();

        // 安装依赖
        console.log('正在安装依赖...');
        await pyodide.installPackage('micropip');

        // 加载 micropip
        await pyodide.runPythonAsync(`
            import micropip
            await micropip.install('easygui==0.98.3')
        `);

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

        // 执行代码
        await pyodide.runPythonAsync(displayCode);
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
from display_manager import DisplayManager

class WebDisplayManager(DisplayManager):
    """Web 端显示管理器"""
    
    def __init__(self):
        super().__init__(mode="terminal")
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
        # 等待用户选择（这里需要实现异步等待）
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
game.run()
    `);
}

// 页面加载完成后初始化
window.addEventListener('load', main);