#!/bin/bash
# ================================================================
# AI 简历生成系统 — 一键部署脚本（Ubuntu 20.04/22.04）
# ================================================================
# 用法：
#   1. 把项目克隆到 /opt/ai-resume
#   2. sudo bash deploy/deploy.sh
#
#   或者逐步骤看下方的命令手动执行
# ================================================================

set -e

APP_DIR="/opt/ai-resume"
VENV_DIR="$APP_DIR/venv"
DOMAIN="your-domain.com"   # ← 改成你的域名
USER="www-data"

echo "=========================================="
echo " AI 简历生成系统 — 生产部署"
echo "=========================================="

# ---- 0. 权限检查 ----
if [ "$(id -u)" -ne 0 ]; then
    echo "❌ 请用 sudo 运行: sudo bash deploy/deploy.sh"
    exit 1
fi

# ---- 1. 安装系统依赖 ----
echo ""
echo "[1/6] 安装系统依赖..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv nginx

# WeasyPrint 依赖 (可选 — 需要 300MB+ 空间，如果空间紧张可以跳过)
# apt-get install -y -qq libgtk-3-dev libpango1.0-dev libcairo2-dev

# ---- 2. 创建目录和用户 ----
echo "[2/6] 创建目录..."
mkdir -p /var/log/ai-resume
mkdir -p /tmp/ai_resume_sessions
chown -R $USER:$USER /var/log/ai-resume /tmp/ai_resume_sessions
chown -R $USER:$USER "$APP_DIR"

# ---- 3. 配置 Python 虚拟环境 ----
echo "[3/6] 配置 Python 环境..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install gunicorn -q
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt" -q

# ---- 4. 配置 systemd 服务 ----
echo "[4/6] 配置 systemd 服务..."
cp "$APP_DIR/deploy/ai-resume.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable ai-resume
systemctl restart ai-resume
sleep 2
systemctl status ai-resume --no-pager || true

# ---- 5. 配置 Nginx ----
echo "[5/6] 配置 Nginx..."
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/ai-resume
sed -i "s/your-domain.com/$DOMAIN/" /etc/nginx/sites-available/ai-resume
if [ ! -L /etc/nginx/sites-enabled/ai-resume ]; then
    ln -s /etc/nginx/sites-available/ai-resume /etc/nginx/sites-enabled/
fi
# 移除默认站点
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# ---- 6. 配置防火墙 ----
echo "[6/6] 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp 2>/dev/null || true
    ufw allow 443/tcp 2>/dev/null || true
    ufw allow 22/tcp 2>/dev/null || true
    echo "  防火墙: 已开放 22, 80, 443 端口"
fi

echo ""
echo "=========================================="
echo " ✅ 部署完成！"
echo ""
echo " 访问: http://$DOMAIN"
echo ""
echo " 常用命令:"
echo "   查看状态:   sudo systemctl status ai-resume"
echo "   查看日志:   sudo journalctl -u ai-resume -f"
echo "   重启服务:   sudo systemctl restart ai-resume"
echo "   更新代码:   cd $APP_DIR && git pull && sudo systemctl restart ai-resume"
echo "=========================================="
