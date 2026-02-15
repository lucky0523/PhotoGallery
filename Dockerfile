# ========================================
# Stage 1: Builder - 安装依赖
# ========================================
FROM python:3.13-slim AS builder

WORKDIR /app

# 安装 Pillow 等图片处理需要的系统库（你的 requirements 有 Pillow + pillow-heif）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    libwebp-dev \
    zlib1g-dev \
    libpng-dev \
    libheif-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ========================================
# Stage 2: Runtime - 运行阶段，尽量小
# ========================================
FROM python:3.13-slim

# 创建非 root 用户
RUN useradd -m -r appuser && \
    mkdir -p /app && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app /app/data

WORKDIR /app

# 安装运行时需要的系统库
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libwebp7 \
    zlib1g \
    libpng16-16 \
    libheif1 \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 复制依赖（极大减小镜像体积）
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目文件，并设置权限
COPY --chown=appuser:appuser . .

# 确保数据目录存在并设置权限
USER root
RUN mkdir -p /app/data \
    && chown -R appuser:appuser /app/data

# 切换到非 root 用户
USER appuser

# 收集静态文件（确保 settings.py 中 STATIC_ROOT = BASE_DIR / 'static' 或类似）
RUN python manage.py collectstatic --noinput --clear

# 暴露端口（与 uwsgi_conf.ini 一致）
EXPOSE 8000

# 前台运行 uWSGI（不要 daemonize）
CMD ["pyuwsgi", "--ini", "uwsgi_conf_docker.ini"]