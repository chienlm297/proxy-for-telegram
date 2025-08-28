#!/usr/bin/env python3
"""
Telegram Proxy Server
Proxy server để bypass việc chặn Telegram ở công ty
"""

import socket
import threading
import time
import logging
from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import urlparse
import json

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramProxy:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.connections = []
        
        # Telegram server endpoints
        self.telegram_servers = [
            '149.154.167.51',  # DC1
            '149.154.175.53',  # DC2
            '149.154.176.53',  # DC3
            '149.154.177.53',  # DC4
            '149.154.178.53',  # DC5
        ]
        
        # Web app
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/status')
        def status():
            return jsonify({
                'status': 'running' if self.running else 'stopped',
                'connections': len(self.connections),
                'uptime': getattr(self, 'start_time', 0)
            })
        
        @self.app.route('/test_telegram')
        def test_telegram():
            try:
                # Test kết nối đến Telegram
                response = requests.get('https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/getMe', 
                                     timeout=10)
                return jsonify({
                    'success': True,
                    'status_code': response.status_code,
                    'message': 'Kết nối Telegram thành công'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'message': 'Không thể kết nối đến Telegram'
                })
    
    def start_proxy(self):
        """Khởi động proxy server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            
            self.running = True
            self.start_time = time.time()
            logger.info(f"Proxy server đang chạy trên {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"Kết nối mới từ {client_address}")
                    
                    # Tạo thread mới cho mỗi kết nối
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                    self.connections.append(client_socket)
                    
                except Exception as e:
                    if self.running:
                        logger.error(f"Lỗi khi chấp nhận kết nối: {e}")
                        
        except Exception as e:
            logger.error(f"Lỗi khi khởi động proxy server: {e}")
        finally:
            self.stop_proxy()
    
    def handle_client(self, client_socket, client_address):
        """Xử lý kết nối từ client"""
        try:
            # Đọc request từ client
            request_data = client_socket.recv(4096)
            if not request_data:
                return
            
            # Parse HTTP request
            request_lines = request_data.decode('utf-8', errors='ignore').split('\n')
            if not request_lines:
                return
            
            first_line = request_lines[0]
            if not first_line.startswith(('GET', 'POST', 'CONNECT')):
                return
            
            method, url, version = first_line.split(' ', 2)
            
            if method == 'CONNECT':
                # HTTPS tunneling
                self.handle_https_tunnel(client_socket, url)
            else:
                # HTTP proxy
                self.handle_http_proxy(client_socket, request_data)
                
        except Exception as e:
            logger.error(f"Lỗi khi xử lý client {client_address}: {e}")
        finally:
            try:
                client_socket.close()
                if client_socket in self.connections:
                    self.connections.remove(client_socket)
            except:
                pass
    
    def handle_https_tunnel(self, client_socket, target):
        """Xử lý HTTPS tunneling"""
        try:
            host, port = target.split(':')
            port = int(port)
            
            # Kết nối đến target server
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((host, port))
            
            # Gửi "Connection established" cho client
            client_socket.send(b'HTTP/1.1 200 Connection established\r\n\r\n')
            
            # Tạo tunnel giữa client và target
            self.create_tunnel(client_socket, target_socket)
            
        except Exception as e:
            logger.error(f"Lỗi HTTPS tunnel: {e}")
            try:
                client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            except:
                pass
    
    def handle_http_proxy(self, client_socket, request_data):
        """Xử lý HTTP proxy"""
        try:
            # Parse request để lấy target URL
            request_lines = request_data.decode('utf-8', errors='ignore').split('\n')
            first_line = request_lines[0]
            method, url, version = first_line.split(' ', 2)
            
            # Tìm Host header
            host = None
            for line in request_lines:
                if line.lower().startswith('host:'):
                    host = line.split(':', 1)[1].strip()
                    break
            
            if not host:
                client_socket.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
                return
            
            # Kết nối đến target server
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((host, 80))
            
            # Gửi request đến target
            target_socket.send(request_data)
            
            # Nhận response và gửi về client
            while True:
                response_data = target_socket.recv(4096)
                if not response_data:
                    break
                client_socket.send(response_data)
                
        except Exception as e:
            logger.error(f"Lỗi HTTP proxy: {e}")
            try:
                client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            except:
                pass
    
    def create_tunnel(self, client_socket, target_socket):
        """Tạo tunnel giữa client và target"""
        def forward_data(src, dst):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.send(data)
            except:
                pass
            finally:
                try:
                    src.close()
                    dst.close()
                except:
                    pass
        
        # Tạo 2 thread để forward data
        t1 = threading.Thread(target=forward_data, args=(client_socket, target_socket))
        t2 = threading.Thread(target=forward_data, args=(target_socket, client_socket))
        
        t1.daemon = True
        t2.daemon = True
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
    
    def stop_proxy(self):
        """Dừng proxy server"""
        self.running = False
        
        # Đóng tất cả kết nối
        for conn in self.connections:
            try:
                conn.close()
            except:
                pass
        self.connections.clear()
        
        # Đóng server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Proxy server đã dừng")
    
    def start_web_interface(self, host='0.0.0.0', port=5000):
        """Khởi động web interface"""
        self.app.run(host=host, port=port, debug=False)

def main():
    """Hàm main"""
    proxy = TelegramProxy()
    
    # Khởi động proxy server trong thread riêng
    proxy_thread = threading.Thread(target=proxy.start_proxy)
    proxy_thread.daemon = True
    proxy_thread.start()
    
    # Khởi động web interface
    try:
        proxy.start_web_interface()
    except KeyboardInterrupt:
        logger.info("Đang dừng server...")
        proxy.stop_proxy()

if __name__ == '__main__':
    main()
