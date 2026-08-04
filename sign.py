#!/usr/bin/env python3
"""
Mefrp 自动签到脚本（GitHub Actions 版）
环境变量：MEFRP_USER_TOKEN, MEFRP_CAPTCHA_TOKEN
"""

import os
import sys
import json
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

SIGN_URL = "https://api.mefrp.com/api/auth/user/sign"

def main():
    user_token = os.getenv("MEFRP_USER_TOKEN")
    captcha_token = os.getenv("MEFRP_CAPTCHA_TOKEN")

    if not user_token:
        logger.error("缺少 MEFRP_USER_TOKEN，请检查 GitHub Secrets")
        sys.exit(1)
    if not captcha_token:
        logger.error("缺少 MEFRP_CAPTCHA_TOKEN，请检查 GitHub Secrets")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    payload = {"captchaToken": captcha_token}

    try:
        resp = requests.post(SIGN_URL, json=payload, headers=headers, timeout=10)
        data = resp.json()
        code = data.get("code")
        message = data.get("message", "")

        if code == 200:
            logger.info(f"✅ 签到成功: {message}")
        elif code == 403 and "已签到" in message:
            logger.info(f"ℹ️ 今日已签到: {message}")
        elif code == 401:
            logger.error("❌ 用户 Token 无效或过期，请重新获取并更新 Secrets")
            sys.exit(1)
        elif code == 400:
            logger.error("❌ captchaToken 无效或已过期，请重新获取并更新 Secrets")
            sys.exit(1)
        else:
            logger.error(f"❌ 签到失败 (code={code}): {message}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ 请求异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
