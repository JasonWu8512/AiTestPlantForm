import json
import os
from datetime import datetime

from apps.executions.models import TestExecution
from apps.reports.models import TestReport

from django.conf import settings


def build_execution_summary(execution):
    results = execution.results.all()
    total = results.count()
    passed = results.filter(status="passed").count()
    failed = results.filter(status="failed").count()
    blocked = results.filter(status="blocked").count()
    skipped = results.filter(status="skipped").count()
    pass_rate = round(passed / total * 100, 2) if total else 0
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "blocked": blocked,
        "skipped": skipped,
        "pass_rate": pass_rate,
    }


def generate_allure_results(execution):
    allure_results_dir = os.path.join(settings.MEDIA_ROOT, "allure-results", str(execution.id))
    os.makedirs(allure_results_dir, exist_ok=True)
    
    results = execution.results.all().select_related("testcase")
    
    for result in results:
        testcase = result.testcase
        timestamp = int(result.executed_at.timestamp() * 1000) if result.executed_at else int(datetime.now().timestamp() * 1000)
        
        result_data = {
            "uuid": f"test-{result.id}-{execution.id}",
            "historyId": f"tc-{testcase.id}",
            "testCaseName": testcase.title,
            "fullName": f"{execution.plan.name}/{testcase.title}",
            "className": execution.plan.name,
            "status": result.status,
            "start": timestamp,
            "stop": timestamp + 1000,
        }
        
        if result.status == "failed":
            result_data["statusDetails"] = {
                "message": result.actual_result or "测试失败",
                "trace": result.actual_result or "测试失败"
            }
        
        file_name = f"{result_data['uuid']}-result.json"
        file_path = os.path.join(allure_results_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False)
    
    return allure_results_dir


def generate_report_for_execution(execution_id, allure_report_path=""):
    execution = TestExecution.objects.select_related("plan").get(id=execution_id)
    summary = build_execution_summary(execution)
    
    generate_allure_results(execution)
    
    allure_report_path = f"/allure-report/{execution.id}/"
    
    report, _ = TestReport.objects.update_or_create(
        execution=execution,
        defaults={
            "name": f"{execution.plan.name} 测试报告",
            "summary": summary,
            "allure_report_path": allure_report_path,
            "status": "generated",
        },
    )
    return report
