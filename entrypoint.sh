#!/bin/bash
set -e

# 确保数据目录存在
mkdir -p /app/data

# 设置数据目录权限
chown -R appuser:appuser /app/data
chmod -R 755 /app/data

# 自动执行数据库迁移
echo "Running database migrations..."
gosu appuser python manage.py makemigrations --noinput
gosu appuser python manage.py migrate --noinput
echo "Migrations completed."

# 切换到 appuser 并执行命令
exec gosu appuser "$@"
