FROM python:3.9-slim

# Cài đặt các package cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy requirements và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Tạo thư mục templates nếu chưa có
RUN mkdir -p templates

# Expose ports
EXPOSE 5000 8080

# Khởi động ứng dụng
CMD ["python", "app.py"]
