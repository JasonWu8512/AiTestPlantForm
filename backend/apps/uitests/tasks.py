from celery import shared_task
from django.utils import timezone

from apps.uitests.models import UITestCase, UITestExecution, UITestResult
from apps.uitests.services import UITestSuiteExecutor


@shared_task(bind=True)
def run_ui_tests_task(self, execution_id, testcase_ids=None):
    execution = UITestExecution.objects.get(id=execution_id)

    execution.status = "running"
    execution.started_at = timezone.now()
    execution.celery_task_id = self.request.id
    execution.save(update_fields=["status", "started_at", "celery_task_id", "updated_at"])

    try:
        if testcase_ids:
            testcases = UITestCase.objects.filter(id__in=testcase_ids, status="active")
        else:
            testcases = UITestCase.objects.filter(project=execution.project, status="active")

        testcases = list(testcases)

        if not testcases:
            execution.status = "failed"
            execution.finished_at = timezone.now()
            execution.save(update_fields=["status", "finished_at", "updated_at"])
            return {"status": "error", "message": "没有找到可执行的用例"}

        suite_executor = UITestSuiteExecutor(testcases)
        results = suite_executor.execute_all()

        passed_count = 0
        failed_count = 0

        for result in results:
            testcase_id = result.pop("testcase_id")
            UITestResult.objects.create(
                execution=execution,
                testcase_id=testcase_id,
                status=result["status"],
                screenshot=result.get("screenshot", ""),
                video_path=result.get("video_path", ""),
                logs=result.get("logs", ""),
                error_message=result.get("error_message", ""),
                duration=result.get("duration"),
                executed_at=result.get("executed_at"),
            )

            if result["status"] == "passed":
                passed_count += 1
            else:
                failed_count += 1

        execution.total = len(testcases)
        execution.passed = passed_count
        execution.failed = failed_count
        execution.status = "completed"
        execution.finished_at = timezone.now()
        execution.save(update_fields=["total", "passed", "failed", "status", "finished_at", "updated_at"])

        return {
            "status": "success",
            "total": len(testcases),
            "passed": passed_count,
            "failed": failed_count,
        }

    except Exception as e:
        execution.status = "failed"
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "finished_at", "updated_at"])
        return {"status": "error", "message": str(e)}
