#!/bin/zsh
cd "${0:A:h}" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo "需要 Python 3.9 或更新版本。"
  read -r "?按回车关闭窗口…"
  exit 1
fi
echo "浏览器访问 http://127.0.0.1:8765，按 Control+C 停止服务。"
PYTHONDONTWRITEBYTECODE=1 python3 app.py
