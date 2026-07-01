"""
Agent集成示例 - 展示如何在Agent中集成AI指示灯
"""

import requests
from typing import Optional


class AIIndicatorController:
    """
    AI指示灯控制器

    用于在Agent中控制物理指示灯，直观显示AI状态
    """

    def __init__(self, api_url: str = "http://127.0.0.1:5000"):
        """
        初始化控制器

        Args:
            api_url: API服务地址，默认 http://127.0.0.1:5000
        """
        self.api_url = api_url.rstrip('/')

    def _send_command(self, endpoint: str) -> bool:
        """
        发送指令到API

        Args:
            endpoint: API端点

        Returns:
            bool: 是否成功
        """
        try:
            response = requests.post(f"{self.api_url}{endpoint}", timeout=2)
            result = response.json()
            return result.get('success', False)
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到API服务: {self.api_url}")
            print("   请确保AI指示灯软件已启动，且已启用API服务")
            return False
        except Exception as e:
            print(f"❌ 控制指示灯失败: {e}")
            return False

    def set_idle(self) -> bool:
        """
        设置AI为空闲状态（绿灯）

        当AI完成所有任务，等待新指令时调用
        """
        print("🟢 AI指示灯: 空闲（绿灯）")
        return self._send_command('/api/light/green')

    def set_thinking(self) -> bool:
        """
        设置AI为思考状态（黄灯）

        当AI开始处理任务、生成代码、分析问题等时调用
        """
        print("🟡 AI指示灯: 思考中（黄灯）")
        return self._send_command('/api/light/yellow')

    def set_need_permission(self) -> bool:
        """
        设置AI为需要权限状态（红灯）

        当AI需要执行敏感操作、修改重要文件、访问受限资源时调用
        """
        print("🔴 AI指示灯: 需要权限（红灯）")
        return self._send_command('/api/light/red')

    def turn_off(self) -> bool:
        """
        关闭指示灯
        """
        print("⚫ AI指示灯: 关闭")
        return self._send_command('/api/light/off')

    def get_status(self) -> Optional[dict]:
        """
        获取当前状态

        Returns:
            dict: 状态信息，如 {'is_connected': True, 'port': 'COM3', ...}
        """
        try:
            response = requests.get(f"{self.api_url}/api/status", timeout=2)
            result = response.json()
            if result.get('success'):
                return result.get('data')
            return None
        except:
            return None


# =============================================================================
# 使用示例
# =============================================================================

def example_1_basic_usage():
    """示例1：基本使用"""
    print("=" * 60)
    print("示例1：基本使用")
    print("=" * 60)

    # 创建控制器
    indicator = AIIndicatorController()

    # AI开始思考
    indicator.set_thinking()
    # ... AI处理任务 ...

    # AI需要权限
    indicator.set_need_permission()
    # ... 等待用户授权 ...

    # 获得授权，继续处理
    indicator.set_thinking()
    # ... 继续处理 ...

    # 任务完成
    indicator.set_idle()

    print("\n")


def example_2_decorator():
    """示例2：使用装饰器自动管理状态"""
    print("=" * 60)
    print("示例2：使用装饰器")
    print("=" * 60)

    indicator = AIIndicatorController()

    def with_indicator(func):
        """装饰器：在函数执行期间显示黄灯"""
        def wrapper(*args, **kwargs):
            indicator.set_thinking()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                indicator.set_idle()
        return wrapper

    @with_indicator
    def process_task(task_name: str):
        """模拟处理任务"""
        print(f"正在处理任务: {task_name}")
        import time
        time.sleep(2)
        print(f"任务完成: {task_name}")

    # 使用装饰器
    process_task("分析代码")
    process_task("生成文档")

    print("\n")


def example_3_context_manager():
    """示例3：使用上下文管理器"""
    print("=" * 60)
    print("示例3：使用上下文管理器")
    print("=" * 60)

    class IndicatorContext:
        """上下文管理器：在with块内自动管理指示灯"""

        def __init__(self, indicator: AIIndicatorController, status: str = "thinking"):
            self.indicator = indicator
            self.status = status

        def __enter__(self):
            if self.status == "thinking":
                self.indicator.set_thinking()
            elif self.status == "need_permission":
                self.indicator.set_need_permission()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.indicator.set_idle()

    indicator = AIIndicatorController()

    # 使用上下文管理器
    with IndicatorContext(indicator, "thinking"):
        print("正在处理任务...")
        import time
        time.sleep(2)
        print("任务完成！")

    print("\n")


def example_4_in_agent():
    """示例4：在Agent中的完整集成"""
    print("=" * 60)
    print("示例4：在Agent中的完整集成")
    print("=" * 60)

    class MyAgent:
        """自定义Agent，集成AI指示灯"""

        def __init__(self):
            self.indicator = AIIndicatorController()
            self.indicator.set_idle()  # 初始状态：空闲

        def process_user_request(self, request: str):
            """处理用户请求"""
            # 开始思考
            self.indicator.set_thinking()

            print(f"收到请求: {request}")

            # 分析请求
            if "敏感操作" in request:
                # 需要权限
                self.indicator.set_need_permission()
                print("⚠️  需要用户授权...")
                # 这里应该等待用户响应
                import time
                time.sleep(2)

            # 处理请求
            print("处理中...")
            import time
            time.sleep(2)

            # 完成
            self.indicator.set_idle()
            print("✅ 请求处理完成")

    # 使用Agent
    agent = MyAgent()
    agent.process_user_request("帮我分析这段代码")
    agent.process_user_request("执行敏感操作")

    print("\n")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == '1':
            example_1_basic_usage()
        elif example_num == '2':
            example_2_decorator()
        elif example_num == '3':
            example_3_context_manager()
        elif example_num == '4':
            example_4_in_agent()
        else:
            print(f"未知示例: {example_num}")
            print("可用示例: 1, 2, 3, 4")
    else:
        # 运行所有示例
        example_1_basic_usage()
        example_2_decorator()
        example_3_context_manager()
        example_4_in_agent()

        print("=" * 60)
        print("所有示例运行完成")
        print("=" * 60)
