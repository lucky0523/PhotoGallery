# ========================================
# Stage 1: Builder - 安装所有依赖（包含编译工具）
# ========================================
FROM python:3.13-slim AS builder

WORKDIR /app

# 安装构建时需要的系统依赖（Pillow、pillow-heif 编译需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libimagequant-dev \
    libraqm-dev \
    && rm -rf /var/lib/apt/lists/*

# 先复制 requirements.txt 并安装（缓存优化）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*   # 清理 pip 缓存，节省空间

# ========================================
# Stage 2: Runtime - 最终运行镜像（最精简）
# ========================================
FROM python:3.13-slim

# 安装运行时最小的动态库（Pillow 和 pillow-heif 运行需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    libpng16-16 \
    libwebp7 \
    libopenjp2-7 \
    libimagequant0 \
    libraqm0 \
    libheif1 \
    libexpat1 \
    gosu \
    media-types \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 从 builder 阶段复制已安装的 Python 包和工具（核心优化点）
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目代码
COPY . .

# 收集静态文件（在正确用户下执行）
RUN python manage.py collectstatic --noinput --clear

# 赋予 entrypoint 执行权限
RUN chmod +x entrypoint.sh

# 暴露端口
EXPOSE 8000

# 入口点
ENTRYPOINT ["/app/entrypoint.sh"]

# 启动命令
CMD ["pyuwsgi", "--ini", "uwsgi_conf_docker.ini"]