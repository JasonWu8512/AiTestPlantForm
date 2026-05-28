import time
import traceback
from typing import Any, Dict, List

from django.utils import timezone


class UIExecutor:
    def __init__(self, testcase):
        self.testcase = testcase
        self.browser = None
        self.page = None
        self.context = None
        self.logs = []
        self.start_time = None
        self.end_time = None

    def log(self, message: str):
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")

    def execute(self) -> Dict[str, Any]:
        try:
            import playwright.sync_api as playwright
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "status": "error",
                "error_message": "Playwright 库未安装，请运行: pip install playwright && playwright install",
                "executed_at": timezone.now(),
                "logs": "Playwright not installed",
            }

        self.start_time = time.time()
        screenshot_base64 = ""

        try:
            self.log(f"开始执行用例: {self.testcase.name}")
            self.log(f"浏览器: {self.testcase.browser}, 视口: {self.testcase.viewport_width}x{self.testcase.viewport_height}")

            with sync_playwright() as p:
                browser_type = getattr(p, self.testcase.browser)
                self.log("启动浏览器...")

                browser_kwargs = {"headless": self.testcase.headless}
                if self.testcase.browser == "chromium":
                    browser_kwargs["slow_mo"] = 100

                self.browser = browser_type.launch(**browser_kwargs)

                self.context = self.browser.new_context(
                    viewport={"width": self.testcase.viewport_width, "height": self.testcase.viewport_height},
                    record_video_dir="/tmp" if self.testcase.headless else None
                )

                self.page = self.context.new_page()
                self.page.set_default_timeout(self.testcase.timeout)

                self.log("浏览器已启动，开始执行步骤...")

                for i, step in enumerate(self.testcase.steps, 1):
                    self.log(f"执行步骤 {i}: {step.get('type', 'unknown')}")
                    success = self._execute_step(step)
                    if not success:
                        raise Exception(f"步骤 {i} 执行失败")

                self.log("所有步骤执行完成")
                screenshot_base64 = self.page.screenshot(full_page=True, encoding="base64")

                self.end_time = time.time()

                return {
                    "status": "passed",
                    "screenshot": screenshot_base64,
                    "logs": "\n".join(self.logs),
                    "error_message": "",
                    "duration": int((self.end_time - self.start_time) * 1000),
                    "executed_at": timezone.now(),
                }

        except Exception as e:
            self.log(f"错误: {str(e)}")
            self.log(traceback.format_exc())

            if self.page:
                try:
                    screenshot_base64 = self.page.screenshot(full_page=True, encoding="base64")
                except:
                    pass

            self.end_time = time.time()

            return {
                "status": "failed" if isinstance(e, AssertionError) else "error",
                "screenshot": screenshot_base64,
                "logs": "\n".join(self.logs),
                "error_message": str(e),
                "duration": int((self.end_time - self.start_time) * 1000),
                "executed_at": timezone.now(),
            }

        finally:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()

    def _execute_step(self, step: Dict[str, Any]) -> bool:
        step_type = step.get("type", "")
        selector = step.get("selector", "")
        value = step.get("value", "")
        text = step.get("text", "")
        url = step.get("url", self.testcase.base_url)

        try:
            if step_type == "navigate":
                self.log(f"导航到: {url}")
                self.page.goto(url, wait_until="networkidle" if step.get("wait_network", True) else "domcontentloaded")
                return True

            elif step_type == "click":
                self.log(f"点击: {selector}")
                self.page.click(selector)
                return True

            elif step_type == "fill":
                self.log(f"输入: {selector} -> {value}")
                self.page.fill(selector, value)
                return True

            elif step_type == "type":
                self.log(f"输入(逐字): {selector} -> {value}")
                self.page.type(selector, value)
                return True

            elif step_type == "select_option":
                self.log(f"选择选项: {selector} -> {value}")
                self.page.select_option(selector, value)
                return True

            elif step_type == "check":
                self.log(f"勾选: {selector}")
                self.page.check(selector)
                return True

            elif step_type == "uncheck":
                self.log(f"取消勾选: {selector}")
                self.page.uncheck(selector)
                return True

            elif step_type == "hover":
                self.log(f"悬停: {selector}")
                self.page.hover(selector)
                return True

            elif step_type == "wait":
                wait_time = step.get("duration", 1000)
                self.log(f"等待: {wait_time}ms")
                self.page.wait_for_timeout(wait_time)
                return True

            elif step_type == "wait_for":
                self.log(f"等待元素: {selector}")
                self.page.wait_for_selector(selector, state=step.get("state", "visible"))
                return True

            elif step_type == "assert_text":
                self.log(f"断言文本: {selector} 包含 '{text}'")
                element_text = self.page.text_content(selector)
                assert text in element_text, f"期望文本 '{text}' 未找到，实际: '{element_text}'"
                return True

            elif step_type == "assert_url":
                self.log(f"断言URL: 包含 '{value}'")
                current_url = self.page.url
                assert value in current_url, f"期望URL包含 '{value}'，实际: '{current_url}'"
                return True

            elif step_type == "assert_title":
                self.log(f"断言标题: 包含 '{text}'")
                title = self.page.title()
                assert text in title, f"期望标题包含 '{text}'，实际: '{title}'"
                return True

            elif step_type == "assert_exists":
                self.log(f"断言存在: {selector}")
                count = self.page.locator(selector).count()
                assert count > 0, f"元素 '{selector}' 不存在"
                return True

            elif step_type == "assert_not_exists":
                self.log(f"断言不存在: {selector}")
                count = self.page.locator(selector).count()
                assert count == 0, f"元素 '{selector}' 仍然存在"
                return True

            elif step_type == "scroll_to":
                self.log(f"滚动到: {selector}")
                self.page.locator(selector).scroll_into_view_if_needed()
                return True

            elif step_type == "upload":
                self.log(f"上传文件: {selector} -> {value}")
                self.page.set_input_files(selector, value)
                return True

            elif step_type == "drag_drop":
                self.log(f"拖拽: {step.get('source')} -> {step.get('target')}")
                self.page.drag_and_drop(step.get("source"), step.get("target"))
                return True

            else:
                self.log(f"未知步骤类型: {step_type}")
                return False

        except Exception as e:
            self.log(f"步骤执行异常: {str(e)}")
            raise


class UITestSuiteExecutor:
    def __init__(self, testcases: List):
        self.testcases = testcases
        self.results = []

    def execute_all(self) -> List[Dict[str, Any]]:
        results = []
        for testcase in self.testcases:
            executor = UIExecutor(testcase)
            result = executor.execute()
            result["testcase_id"] = testcase.id
            results.append(result)
        return results
