import json
import time
from typing import Any, Dict, List

import requests
from django.utils import timezone


class ApiTestExecutor:
    def __init__(self, testcase, timeout=None):
        self.testcase = testcase
        self.timeout = timeout or testcase.timeout or 30
        self.response = None
        self.error = None

    def execute(self) -> Dict[str, Any]:
        start_time = time.time()

        try:
            response = self._send_request()
            response_time = int((time.time() - start_time) * 1000)

            validation_results = self._validate_response(response)

            status = "passed"
            if not validation_results["all_passed"]:
                status = "failed"
            elif response.status_code != self.testcase.expected_status:
                status = "failed"
                validation_results["errors"].append(
                    f"状态码不匹配: 期望 {self.testcase.expected_status}, 实际 {response.status_code}"
                )

            return {
                "status": status,
                "response_status": response.status_code,
                "response_body": self._parse_response_body(response),
                "response_time": response_time,
                "validation_results": validation_results,
                "error_message": "",
                "executed_at": timezone.now(),
            }

        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "response_status": None,
                "response_body": {},
                "response_time": int((time.time() - start_time) * 1000),
                "validation_results": {"all_passed": False, "errors": ["请求超时"]},
                "error_message": f"请求超时 (timeout={self.timeout}s)",
                "executed_at": timezone.now(),
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "response_status": None,
                "response_body": {},
                "response_time": int((time.time() - start_time) * 1000),
                "validation_results": {"all_passed": False, "errors": [str(e)]},
                "error_message": str(e),
                "executed_at": timezone.now(),
            }

        except Exception as e:
            return {
                "status": "error",
                "response_status": None,
                "response_body": {},
                "response_time": int((time.time() - start_time) * 1000),
                "validation_results": {"all_passed": False, "errors": [str(e)]},
                "error_message": str(e),
                "executed_at": timezone.now(),
            }

    def _send_request(self) -> requests.Response:
        url = self.testcase.url
        headers = self.testcase.headers or {}
        params = self.testcase.params or {}

        data = None
        if self.testcase.body_type == "json":
            data = json.dumps(self.testcase.body) if self.testcase.body else None
            headers["Content-Type"] = "application/json"
        elif self.testcase.body_type == "form-data":
            data = self.testcase.body
        elif self.testcase.body_type == "x-www-form-urlencoded":
            data = self.testcase.body
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif self.testcase.body_type == "raw":
            data = self.testcase.body.get("content", "") if isinstance(self.testcase.body, dict) else str(self.testcase.body)
            headers["Content-Type"] = headers.get("Content-Type", "text/plain")

        return requests.request(
            method=self.testcase.method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            timeout=self.timeout,
            verify=False,
        )

    def _parse_response_body(self, response: requests.Response) -> Dict[str, Any]:
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError):
            return {"_raw": response.text[:1000]}

    def _validate_response(self, response: requests.Response) -> Dict[str, Any]:
        validation_results = {
            "all_passed": True,
            "checks": [],
            "errors": [],
        }

        if not self.testcase.validation_rules:
            return validation_results

        for rule in self.testcase.validation_rules:
            rule_type = rule.get("type", "status_code")
            rule_params = rule.get("params", {})

            if rule_type == "status_code":
                expected = rule_params.get("expected", self.testcase.expected_status)
                if response.status_code != expected:
                    validation_results["all_passed"] = False
                    validation_results["errors"].append(f"状态码验证失败: 期望 {expected}, 实际 {response.status_code}")
                validation_results["checks"].append({
                    "type": "status_code",
                    "passed": response.status_code == expected,
                    "expected": expected,
                    "actual": response.status_code,
                })

            elif rule_type == "json_path":
                json_path = rule_params.get("json_path", "")
                expected_value = rule_params.get("expected")
                operator = rule_params.get("operator", "equals")

                try:
                    actual_value = self._extract_json_path(response.json(), json_path)
                    check_passed = self._compare_values(actual_value, expected_value, operator)

                    if not check_passed:
                        validation_results["all_passed"] = False
                        validation_results["errors"].append(
                            f"JSON路径验证失败: {json_path} {operator} {expected_value}, 实际: {actual_value}"
                        )
                    validation_results["checks"].append({
                        "type": "json_path",
                        "passed": check_passed,
                        "json_path": json_path,
                        "expected": expected_value,
                        "operator": operator,
                        "actual": actual_value,
                    })
                except Exception as e:
                    validation_results["all_passed"] = False
                    validation_results["errors"].append(f"JSON路径提取失败: {json_path} - {str(e)}")
                    validation_results["checks"].append({
                        "type": "json_path",
                        "passed": False,
                        "json_path": json_path,
                        "error": str(e),
                    })

            elif rule_type == "contains":
                expected_text = rule_params.get("text", "")
                if expected_text not in response.text:
                    validation_results["all_passed"] = False
                    validation_results["errors"].append(f"响应内容不包含: {expected_text}")
                validation_results["checks"].append({
                    "type": "contains",
                    "passed": expected_text in response.text,
                    "expected_text": expected_text,
                })

            elif rule_type == "response_time":
                max_time = rule_params.get("max_time", 5000)
                response_time_ms = int((time.time() - time.time()) * 1000)
                if response_time_ms > max_time:
                    validation_results["all_passed"] = False
                    validation_results["errors"].append(f"响应时间超过限制: {response_time_ms}ms > {max_time}ms")
                validation_results["checks"].append({
                    "type": "response_time",
                    "passed": response_time_ms <= max_time,
                    "max_time": max_time,
                    "actual_time": response_time_ms,
                })

        return validation_results

    def _extract_json_path(self, json_data: Any, json_path: str) -> Any:
        if not json_path:
            return json_data

        parts = json_path.split(".")
        current = json_data

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    return None
            else:
                return None

        return current

    def _compare_values(self, actual: Any, expected: Any, operator: str) -> bool:
        if operator == "equals":
            return actual == expected
        elif operator == "not_equals":
            return actual != expected
        elif operator == "contains":
            return expected in str(actual) if actual is not None else False
        elif operator == "not_contains":
            return expected not in str(actual) if actual is not None else True
        elif operator == "greater_than":
            return actual > expected if (actual is not None and expected is not None) else False
        elif operator == "less_than":
            return actual < expected if (actual is not None and expected is not None) else False
        elif operator == "exists":
            return actual is not None
        elif operator == "not_exists":
            return actual is None
        else:
            return actual == expected


class ApiTestSuiteExecutor:
    def __init__(self, testcases: List):
        self.testcases = testcases
        self.results = []

    def execute_all(self) -> List[Dict[str, Any]]:
        results = []
        for testcase in self.testcases:
            executor = ApiTestExecutor(testcase)
            result = executor.execute()
            result["testcase_id"] = testcase.id
            result["testcase_name"] = testcase.name
            result["testcase_method"] = testcase.method
            result["testcase_url"] = testcase.url
            results.append(result)

        return results
