# [新] 隐形浏览器，专门打硬仗
import time
import logging
import os
import pickle
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.fetchers.base import BaseFetcher

logger = logging.getLogger("StealthBrowser")


class StealthBrowserFetcher(BaseFetcher):
    """
    基于 undetected_chromedriver 的隐形浏览器
    专门用于对抗 Realestate.com.au 这种高防网站
    """

    def __init__(self, headless=False, timeout=30):
        """
        :param headless: 默认为 False。
        注意：uc 的无头模式在某些系统上容易被识别，
        为了稳定性，建议在服务器上使用 XVFB 虚拟显示，而在本地开发时开启窗口。
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None

    def _init_driver(self):
        if self.driver:
            return

        logger.info("🚀 启动隐形战机 (Undetected Chrome)...")

        try:
            options = uc.ChromeOptions()

            # --- 关键反爬配置 ---
            # 1. 禁用密码保存提示
            options.add_argument("--password-store=basic")
            options.add_argument("--no-default-browser-check")

            # 2. 窗口大小随机化 (模拟真实用户) - 这里先定死大屏方便调试
            options.add_argument("--window-size=1920,1080")

            # 3. 禁用不必要的日志
            options.add_argument("--log-level=3")

            # 4. 启动 UC Driver
            # version_main=None 表示自动检测本地 Chrome 版本
            # use_subprocess=True 可以防止进程卡死
            self.driver = uc.Chrome(
                options=options,
                headless=self.headless,
                use_subprocess=True,
                version_main=None
            )

            logger.info("✅ 隐形浏览器启动成功")

        except Exception as e:
            logger.critical(f"❌ 浏览器启动惨败: {e}")
            # 如果启动失败，尝试清理残留进程 (Linux/Mac)
            try:
                os.system("pkill -f chrome")
            except:
                pass
            raise e

    def fetch(self, url, wait_for_selector=None, sleep_time=5):
        """
        :param sleep_time: 强制等待时间。对于高防网站，不仅要等元素，还要等 Cloudflare 验证跳过。
        """
        self._init_driver()

        try:
            logger.info(f"🕵️‍♂️ 潜入: {url}")
            self.driver.get(url)

            # 1. 刚进入页面，大概率会遇到 Cloudflare 验证
            # 策略：硬等。UC driver 通常能自动通过验证，但需要时间。
            logger.info(f"⏳ 等待 Cloudflare/页面加载 ({sleep_time}s)...")
            time.sleep(sleep_time)

            # 2. 检查是否被拦截 (Title 包含 'Just a moment' 通常是被拦了)
            if "Just a moment" in self.driver.title or "Access denied" in self.driver.title:
                logger.error("⛔️ 被 Cloudflare 拦截！")
                # 这里可以接入打码平台 (Level 5 内容)，现在先抛错
                # 或者尝试刷新
                self.driver.refresh()
                time.sleep(sleep_time + 5)

            # 3. 智能等待目标元素
            if wait_for_selector:
                logger.info(f"👁️ 寻找目标: {wait_for_selector}")
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )

            # 4. 模拟人类滚动 (Scroll)
            # 很多网站的数据是懒加载的，不滚到底部不出来
            self._human_scroll()

            return self.driver.page_source

        except Exception as e:
            logger.error(f"❌ 抓取中断: {e}")
            # 截图留证 (Debugging)
            try:
                self.driver.save_screenshot("logs/error_screenshot.png")
                logger.info("📸 已保存报错截图到 logs/error_screenshot.png")
            except:
                pass
            return None

    def _human_scroll(self):
        """模拟人类不匀速滚动"""
        import random
        logger.info("👇 模拟滚动页面...")
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        for i in range(1, total_height, random.randint(300, 700)):
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(random.uniform(0.1, 0.5))

    def save_cookies(self, filename="twitter_cookies.pkl"):
        """保存当前登录状态"""
        if not self.driver:
            return

        cookie_path = os.path.join("data", filename)
        cookies = self.driver.get_cookies()

        # 创建 data 目录
        os.makedirs("data", exist_ok=True)

        with open(cookie_path, "wb") as f:
            pickle.dump(cookies, f)
        logger.info(f"🍪 Cookies 已保存到 {cookie_path}")
        try:
            with open(cookie_path, "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass  # 忽略无效 Cookie

            logger.info("✅ Cookies 注入成功，刷新页面...")
            self.driver.refresh()
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"❌ Cookie 加载失败: {e}")
            return False

    def load_cookies(self, domain, filename="twitter_cookies.pkl"):
        """加载登录状态"""
        cookie_path = os.path.join("data", filename)
        if not os.path.exists(cookie_path):
            logger.warning("⚠️ 没有找到 Cookie 文件，需要手动登录一次")
            return False

        self._init_driver()

        # 关键点：Selenium 要求先访问该域名，才能设置该域名的 Cookie
        # 所以我们要先打开 twitter.com (空页面也可以)
        logger.info(f"🌐 预访问 {domain} 以注入 Cookie...")
        self.driver.get(domain)
        time.sleep(3)

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🛑 隐形浏览器已归库")
            except:
                pass
            self.driver = None
