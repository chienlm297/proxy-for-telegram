# 🚀 Telegram Proxy Server

Proxy server để bypass việc chặn Telegram ở công ty. Hỗ trợ HTTP và HTTPS tunneling.

## ✨ Tính năng

- **HTTP Proxy**: Hỗ trợ HTTP requests
- **HTTPS Tunneling**: Hỗ trợ HTTPS connections (CONNECT method)
- **Web Interface**: Giao diện web để quản lý và monitor
- **Real-time Status**: Theo dõi trạng thái server và số kết nối
- **Multi-threading**: Xử lý nhiều kết nối đồng thời
- **Docker Support**: Dễ dàng deploy và test

## 🚀 Cách sử dụng

### 1. Chạy locally

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
python app.py
```

### 2. Sử dụng Docker

```bash
# Build và chạy
docker-compose up --build

# Hoặc chạy trực tiếp
docker build -t telegram-proxy .
docker run -p 5000:5000 -p 8080:8080 telegram-proxy
```

### 3. Deploy trên Render

1. Fork repository này về GitHub
2. Tạo tài khoản trên [Render.com](https://render.com)
3. Tạo new Web Service
4. Connect với GitHub repository
5. Chọn branch và deploy

## ⚙️ Cấu hình

### Proxy Settings

- **HTTP Proxy**: `localhost:8080` (local) hoặc `your-server-ip:8080` (remote)
- **Port**: 8080 (có thể thay đổi trong code)

### Web Interface

- **URL**: `http://localhost:5000` (local) hoặc `https://your-app-name.onrender.com`
- **Port**: 5000 (có thể thay đổi qua environment variable `PORT`)

## 📱 Cấu hình Telegram

### Telegram Desktop

1. Mở Telegram Desktop
2. Vào **Settings** → **Advanced** → **Connection type**
3. Chọn **"Use custom proxy"**
4. Điền thông tin:
   - **Server**: `localhost` (local) hoặc IP của server
   - **Port**: `8080`
   - **Type**: `HTTP`

### Telegram Mobile

1. Mở Telegram
2. Vào **Settings** → **Data and Storage** → **Proxy Settings**
3. Bật **Use Proxy**
4. Chọn **HTTP** và điền:
   - **Server**: IP của server
   - **Port**: `8080`

## 🔧 Kiểm tra hoạt động

### 1. Test kết nối

Truy cập web interface và click nút "Test kết nối Telegram"

### 2. Kiểm tra logs

```bash
# Nếu chạy Docker
docker-compose logs -f

# Nếu chạy trực tiếp
# Logs sẽ hiển thị trên console
```

### 3. Test proxy

```bash
# Test HTTP proxy
curl -x localhost:8080 http://httpbin.org/ip

# Test HTTPS (cần client hỗ trợ proxy)
curl --proxy localhost:8080 https://api.telegram.org
```

## 🚨 Lưu ý quan trọng

### Bảo mật

- **KHÔNG** expose proxy server ra internet public mà không có authentication
- Chỉ sử dụng cho mục đích cá nhân
- Cân nhắc thêm username/password nếu deploy public

### Hiệu suất

- Proxy server có thể làm chậm kết nối
- Sử dụng cho mục đích bypass firewall, không phải tăng tốc độ
- Monitor số kết nối để tránh quá tải

### Pháp lý

- Đảm bảo việc sử dụng proxy tuân thủ quy định công ty
- Chỉ sử dụng cho mục đích hợp pháp
- Không bypass các biện pháp bảo mật quan trọng

## 🐛 Troubleshooting

### Lỗi thường gặp

1. **Port đã được sử dụng**
   ```bash
   # Kiểm tra port
   netstat -tulpn | grep :8080
   
   # Kill process sử dụng port
   sudo kill -9 <PID>
   ```

2. **Không thể bind port**
   - Kiểm tra firewall
   - Đảm bảo có quyền bind port

3. **Proxy không hoạt động**
   - Kiểm tra logs
   - Đảm bảo server đang chạy
   - Test kết nối đến server

### Debug mode

```python
# Trong app.py, thay đổi
app.run(host='0.0.0.0', port=port, debug=True)
```

## 📁 Cấu trúc project

```
proxy-for-telegram/
├── app.py                 # Main application (Render)
├── proxy_server.py        # Full proxy server (local)
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker compose
├── templates/
│   └── index.html       # Web interface
└── README.md            # This file
```

## 🤝 Đóng góp

1. Fork project
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Project này được phát hành dưới MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## ⚠️ Disclaimer

Project này được tạo ra chỉ để học tập và nghiên cứu. Người sử dụng chịu trách nhiệm về việc sử dụng proxy server một cách hợp pháp và tuân thủ các quy định của tổ chức/công ty.

---

**Lưu ý**: Đây là proxy server cơ bản, không có các tính năng bảo mật nâng cao. Không nên sử dụng cho mục đích production mà không có các biện pháp bảo mật bổ sung.
# proxy-for-telegram
