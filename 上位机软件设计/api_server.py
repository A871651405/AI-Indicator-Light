"""
HTTP API服务模块 - 提供REST API供Agent调用
"""

from flask import Flask, request, jsonify
from serial_handler import SerialHandler
import threading


class APIServer:
    """API服务器，提供HTTP接口控制指示灯"""

    def __init__(self, serial_handler: SerialHandler):
        self.serial_handler = serial_handler
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """设置API路由"""

        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取当前状态"""
            return jsonify({
                'success': True,
                'data': self.serial_handler.get_status()
            })

        @self.app.route('/api/light/green', methods=['POST'])
        def set_green():
            """设置绿灯（AI空闲）"""
            if not self.serial_handler.is_connected:
                return jsonify({
                    'success': False,
                    'error': '串口未连接'
                }), 400

            success = self.serial_handler.set_green()
            return jsonify({
                'success': success,
                'message': '绿灯已点亮（AI空闲）' if success else '发送指令失败'
            })

        @self.app.route('/api/light/yellow', methods=['POST'])
        def set_yellow():
            """设置黄灯（AI思考）"""
            if not self.serial_handler.is_connected:
                return jsonify({
                    'success': False,
                    'error': '串口未连接'
                }), 400

            success = self.serial_handler.set_yellow()
            return jsonify({
                'success': success,
                'message': '黄灯已点亮（AI思考）' if success else '发送指令失败'
            })

        @self.app.route('/api/light/red', methods=['POST'])
        def set_red():
            """设置红灯（故障/异常）"""
            if not self.serial_handler.is_connected:
                return jsonify({
                    'success': False,
                    'error': '串口未连接'
                }), 400

            success = self.serial_handler.set_red()
            return jsonify({
                'success': success,
                'message': '红灯已点亮（故障/异常）' if success else '发送指令失败'
            })

        @self.app.route('/api/buzzer', methods=['POST'])
        def set_buzzer():
            """设置蜂鸣器"""
            if not self.serial_handler.is_connected:
                return jsonify({
                    'success': False,
                    'error': '串口未连接'
                }), 400

            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '缺少参数'
                }), 400

            volume = data.get('volume', 50)
            duration = data.get('duration', 5)

            # 验证参数范围
            if not (0 <= volume <= 100):
                return jsonify({
                    'success': False,
                    'error': '音量必须在0-100之间'
                }), 400

            if not (0 <= duration <= 60):
                return jsonify({
                    'success': False,
                    'error': '时长必须在0-60秒之间'
                }), 400

            success = self.serial_handler.set_buzzer(volume, duration)
            return jsonify({
                'success': success,
                'message': f'蜂鸣器设置已发送（音量:{volume}, 时长:{duration}s）' if success else '发送指令失败'
            })

        @self.app.route('/api/light/off', methods=['POST'])
        def turn_off():
            """关闭灯光"""
            if not self.serial_handler.is_connected:
                return jsonify({
                    'success': False,
                    'error': '串口未连接'
                }), 400

            success = self.serial_handler.turn_off()
            return jsonify({
                'success': success,
                'message': '灯光已关闭' if success else '发送指令失败'
            })

        @self.app.route('/api/serial/connect', methods=['POST'])
        def connect_serial():
            """连接串口"""
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '缺少参数'
                }), 400

            port = data.get('port')
            baudrate = data.get('baudrate', 115200)  # 固定为115200

            if not port:
                return jsonify({
                    'success': False,
                    'error': '缺少串口号'
                }), 400

            success = self.serial_handler.connect(port, baudrate)
            return jsonify({
                'success': success,
                'message': f'已连接串口 {port}' if success else '连接失败'
            })

        @self.app.route('/api/serial/disconnect', methods=['POST'])
        def disconnect_serial():
            """断开串口"""
            self.serial_handler.disconnect()
            return jsonify({
                'success': True,
                'message': '已断开连接'
            })

        @self.app.route('/api/serial/ports', methods=['GET'])
        def get_ports():
            """获取可用串口列表"""
            ports = self.serial_handler.get_available_ports()
            return jsonify({
                'success': True,
                'data': ports
            })

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({
                'success': True,
                'message': 'AI指示灯服务运行正常'
            })

    def run(self, host='127.0.0.1', port=5000, debug=False):
        """运行API服务器"""
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == '__main__':
    # 测试API服务器
    from serial_handler import SerialHandler

    handler = SerialHandler()
    server = APIServer(handler)
    server.run(debug=True)
