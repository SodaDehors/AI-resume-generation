#!/bin/bash
# ================================================================
# AI 简历生成系统 — 一键部署脚本（Ubuntu 20.04/22.04）
# 适用于：阿里云轻量应用服务器 / ECS
# ================================================================
# 用法：
#   1. SSH 登录服务器
#   2. git clone https://github.com/SodaDehors/AI-resume-generation.git /opt/ai-resume
#   3. cd /opt/ai-resume && sudo bash deploy/deploy.sh
#
#   部署前请确保：
#     ① 域名已解析到服务器 IP
#     ② 阿里云控制台防火墙已开放 80 端口（轻量服务器 → 防火墙 → 添加规则）
#     ③ API Key 已准备好（DeepSeek / Claude / OpenAI 其一）
# ================================================================

set -e

APP_DIR="/opt/ai-resume"
VENV_DIR="$APP_DIR/venv"
SYSTEM_USER="www-data"

# ---- 交互式输入域名 ----
echo ""
echo "请输入你的域名（如 resume.example.com）："
read -p "> " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ 域名不能为空"
    exit 1
fi

echo ""
echo "=========================================="
echo " AI 简历生成系统 — 生产部署"
echo " 域名: $DOMAIN"
echo "=========================================="
echo ""

# ---- 0. 权限检查 ----
if [ "$(id -u)" -ne 0 ]; then
    echo "❌ 请用 sudo 运行: sudo bash deploy/deploy.sh"
    exit 1
fi

# ---- 1. 安装系统依赖 ----
echo "[1/7] 安装系统依赖..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv nginx git

# ---- 2. 创建目录和用户 ----
echo "[2/7] 创建目录..."
mkdir -p /var/log/ai-resume
mkdir -p /tmp/ai_resume_sessions
chown -R $SYSTEM_USER:$SYSTEM_USER /var/log/ai-resume /tmp/ai_resume_sessions
chown -R $SYSTEM_USER:$SYSTEM_USER "$APP_DIR"

# ---- 3. 配置 .env 文件 ----
echo "[3/7] 配置环境变量..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo ""
    echo "  ┌─────────────────────────────────────────┐"
    echo "  │  🔐 请现在编辑 .env 填入你的 API Key      │"
    echo "  │  按回车打开编辑器，保存后继续部署         │"
    echo "  └─────────────────────────────────────────┘"
    read -p "  按回车继续..." dummy
    # 用 nano 打开（Ubuntu 默认有），vi 作为 fallback
    ${EDITOR:-nano} "$APP_DIR/.env"
else
    echo "  .env 已存在，跳过"
fi
chown $SYSTEM_USER:$SYSTEM_USER "$APP_DIR/.env" 2>/dev/null || true
chmod 600 "$APP_DIR/.env"

# ---- 4. 配置 Python 虚拟环境 ----
echo "[4/7] 配置 Python 环境..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install gunicorn -q
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt" -q

# ---- 5. 配置 systemd 服务 ----
echo "[5/7] 配置 systemd 服务..."
cp "$APP_DIR/deploy/ai-resume.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable ai-resume
systemctl restart ai-resume
sleep 2
echo ""
systemctl status ai-resume --no-pager -l || true

# ---- 6. 配置 Nginx ----
echo ""
echo "[6/7] 配置 Nginx..."
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/ai-resume
sed -i "s/your-domain.com/$DOMAIN/" /etc/nginx/sites-available/ai-resume
if [ ! -L /etc/nginx/sites-enabled/ai-resume ]; then
    ln -s /etc/nginx/sites-available/ai-resume /etc/nginx/sites-enabled/
fi
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# ---- 7. 系统防火墙 ----
echo "[7/7] 系统防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp 2>/dev/null || true
    ufw allow 443/tcp 2>/dev/null || true
    ufw allow 22/tcp 2>/dev/null || true
fi

# ---- 完成 ----
echo ""
echo "=========================================="
echo " ✅ 部署完成！"
echo "=========================================="
echo ""
echo " 🌐 访问地址: http://$DOMAIN"
echo ""
echo " ⚠️  如果无法访问，请检查阿里云控制台："
echo "    轻量应用服务器 → 防火墙 → 添加规则"
echo "    协议: TCP  端口: 80  授权对象: 0.0.0.0/0"
echo ""
echo " 📋 常用命令:"
echo "    查看状态:  systemctl status ai-resume"
echo "    查看日志:  journalctl -u ai-resume -f"
echo "    重启服务:  systemctl restart ai-resume"
echo "    更新代码:  cd $APP_DIR && git pull && systemctl restart ai-resume"
echo "    修改配置:  nano $APP_DIR/.env && systemctl restart ai-resume"
echo "=========================================="
