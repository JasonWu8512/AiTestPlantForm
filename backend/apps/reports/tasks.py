from tasks.celery import app

from apps.reports.services import generate_report_for_execution


@app.task
def generate_report_task(execution_id, allure_report_path=""):
    report = generate_report_for_execution(execution_id, allure_report_path)
    return report.id
