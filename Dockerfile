# 使用官方 Python 3.13 slim 镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（Pillow 和 pillow-heif 所需）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libimagequant-dev \
    libraqm-dev \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 赋予 entrypoint 执行权限
RUN chmod +x entrypoint.sh

# 暴露端口
EXPOSE 8000

# 入口点
ENTRYPOINT ["/app/entrypoint.sh"]

# 启动命令
CMD ["pyuwsgi", "--ini", "uwsgi_conf_docker.ini"]
