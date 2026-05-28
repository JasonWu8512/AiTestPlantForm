import json
from pathlib import Path

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.views import View


class AllureReportView(View):
    def get(self, request, execution_id):
        results_dir = Path(settings.MEDIA_ROOT) / "allure-results" / str(execution_id)
        
        if not results_dir.exists():
            raise Http404("测试报告不存在")
        
        results_files = list(results_dir.glob("*-result.json"))
        
        results = []
        if results_files:
            results = self._load_results(results_files)
        
        stats = self._calculate_stats(results)
        
        context = {
            'results': results,
            'execution_id': execution_id,
            **stats
        }
        
        return render(request, 'reports/allure_report.html', context)
    
    def _load_results(self, results_files):
        results = []
        for file_path in results_files:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                processed_result = self._process_result(data)
                results.append(processed_result)
        return results
    
    def _process_result(self, result_data):
        status = result_data.get("status", "unknown")
        status_class = {
            "passed": "success",
            "failed": "danger",
            "blocked": "warning",
            "skipped": "secondary"
        }.get(status, "secondary")
        
        test_name = result_data.get("testCaseName") or result_data.get("fullName", "未知测试")
        message = ""
        
        if status == "failed":
            details = result_data.get("statusDetails", {})
            message = details.get("message", "") or ""
        
        return {
            'status': status,
            'status_class': status_class,
            'test_name': test_name,
            'message': message
        }
    
    def _calculate_stats(self, results):
        total = len(results)
        if total == 0:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'blocked': 0,
                'skipped': 0,
                'pass_rate': 0
            }
        
        passed = sum(1 for r in results if r['status'] == "passed")
        failed = sum(1 for r in results if r['status'] == "failed")
        blocked = sum(1 for r in results if r['status'] == "blocked")
        skipped = sum(1 for r in results if r['status'] == "skipped")
        pass_rate = round(passed / total * 100, 2)
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'blocked': blocked,
            'skipped': skipped,
            'pass_rate': pass_rate
        }