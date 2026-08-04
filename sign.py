#!/usr/bin/env python3
"""
Mefrp 全自动签到脚本（支持自动登录）
环境变量：
  MEFRP_USERNAME           - 用户名
  MEFRP_PASSWORD           - 密码
  MEFRP_LOGIN_CAPTCHA_TOKEN - 登录人机验证 Token
  MEFRP_CAPTCHA_TOKEN      - 签到人机验证 Token（若已登录则不需）
  MEFRP_USER_TOKEN         - 可选，若存在则直接使用，否则自动登录获取并缓存
"""

import os
import sys
import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# API 端点
BASE_URL = "https://api.mefrp.com/api"
LOGIN_URL = f"{BASE_URL}/public/login"
SIGN_URL = f"{BASE_URL}/auth/user/sign"

# 缓存文件（用于存储 Token，避免每次重新登录）
TOKEN_CACHE_FILE = "/tmp/mefrp_token.json"  # GitHub Actions 环境可写

def get_session():
    """创建带重试机制的会话"""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def load_cached_token():
    """从缓存文件读取 Token"""
    if os.path.exists(TOKEN_CACHE_FILE):
        try:
            with open(TOKEN_CACHE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('token')
        except:
            pass
    return None

def save_cached_token(token):
    """缓存 Token 到文件"""
    try:
        with open(TOKEN_CACHE_FILE, 'w') as f:
            json.dump({'token': token}, f)
        logger.info("Token 已缓存")
    except Exception as e:
        logger.warning(f"缓存 Token 失败: {e}")

def login_and_get_token(username, password, captcha_token):
    """
    登录并获取用户 Token
    注意：登录接口响应可能不直接返回 token，需根据实际情况调整提取方式
    """
    logger.info("尝试自动登录...")
    session = get_session()
    payload = {
        "username": username,
        "password": password,
        "captchaToken": captcha_token
    }
    headers = {"Content-Type": "application/json"}

    try:
        resp = session.post(LOGIN_URL, json=payload, headers=headers, timeout=15)
        data = resp.json()
        code = data.get("code")
        msg = data.get("message", "")

        if code == 200:
            logger.info(f"登录成功: {msg}")
            # 尝试从响应中提取 token（请根据实际响应结构调整）
            token = data.get("data", {}).get("token") or data.get("token") or resp.headers.get("Authorization")
            if not token:
                # 如果响应中没有 token，尝试从 Cookie 中获取（假设 token 在 cookie 中名为 'token' 或 'access_token'）
                token = session.cookies.get("token") or session.cookies.get("access_token")
            if token:
                logger.info("成功获取用户 Token")
                save_cached_token(token)
                return token
            else:
                logger.error("登录响应中未找到 Token，请检查接口响应结构")
                # 打印完整响应以便调试
                logger.debug(f"响应内容: {data}")
                logger.debug(f"响应头: {resp.headers}")
                return None
        else:
            logger.error(f"登录失败 (code={code}): {msg}")
            return None
    except Exception as e:
        logger.error(f"登录请求异常: {e}")
        return None

def sign_in(user_token, captcha_token):
    """执行签到"""
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    payload = {"captchaToken": captcha_token}
    try:
        resp = requests.post(SIGN_URL, json=payload, headers=headers, timeout=10)
        data = resp.json()
        code = data.get("code")
        msg = data.get("message", "")
        if code == 200:
            logger.info(f"✅ 签到成功: {msg}")
        elif code == 403 and "已签到" in msg:
            logger.info(f"ℹ️ 今日已签到: {msg}")
        elif code == 401:
            logger.error("❌ 用户 Token 无效或过期，将尝试重新登录")
            # 删除缓存 Token，以便下次重新获取
            if os.path.exists(TOKEN_CACHE_FILE):
                os.remove(TOKEN_CACHE_FILE)
            return False
        elif code == 400:
            logger.error("❌ captchaToken 无效或已过期，请更新 Secrets")
            return False
        else:
            logger.error(f"❌ 签到失败 (code={code}): {msg}")
            return False
        return True
    except Exception as e:
        logger.error(f"❌ 签到请求异常: {e}")
        return False

def main():
    # 读取环境变量
    username = os.getenv("MEFRP_USERNAME")
    password = os.getenv("MEFRP_PASSWORD")
    login_captcha = os.getenv("MEFRP_LOGIN_CAPTCHA_TOKEN")
    sign_captcha = os.getenv("MEFRP_CAPTCHA_TOKEN")
    user_token = os.getenv("MEFRP_USER_TOKEN")

    # 1. 尝试从环境变量或缓存获取 Token
    if not user_token:
        user_token = load_cached_token()

    # 2. 如果 Token 无效，尝试登录获取
    if not user_token:
        if not username or not password or not login_captcha:
            logger.error("缺少登录凭据（用户名、密码或登录验证码），请设置环境变量")
            sys.exit(1)
        user_token = login_and_get_token(username, password, login_captcha)
        if not user_token:
            logger.error("自动登录失败，请检查凭据和验证码")
            sys.exit(1)

    # 3. 执行签到
    if not sign_captcha:
        logger.error("缺少签到人机验证 Token (MEFRP_CAPTCHA_TOKEN)")
        sys.exit(1)

    success = sign_in(user_token, sign_captcha)
    if not success:
        # 如果签到失败且是因为 Token 无效，尝试重新登录后再签到一次
        if not user_token:
            logger.info("尝试重新登录...")
            user_token = login_and_get_token(username, password, login_captcha)
            if user_token:
                sign_in(user_token, sign_captcha)
            else:
                logger.error("重新登录失败")
                sys.exit(1)

if __name__ == "__main__":
    main()
