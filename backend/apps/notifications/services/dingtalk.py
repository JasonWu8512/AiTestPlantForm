import json
import requests
from django.conf import settings


class DingTalkNotifier:
    def __init__(self):
        self.webhook_url = getattr(settings, 'DINGTALK_WEBHOOK_URL', '')
        self.access_token = getattr(settings, 'DINGTALK_ACCESS_TOKEN', '')
        self.secret = getattr(settings, 'DINGTALK_SECRET', '')

    def send_text_message(self, content, at_mobiles=None, at_all=False):
        if not self.webhook_url:
            return {'success': False, 'message': '钉钉Webhook URL未配置'}

        data = {
            'msgtype': 'text',
            'text': {
                'content': content
            },
            'at': {
                'atMobiles': at_mobiles or [],
                'isAtAll': at_all
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()
            if result.get('errcode') == 0:
                return {'success': True, 'message': '发送成功'}
            else:
                return {'success': False, 'message': result.get('errmsg', '发送失败')}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def send_markdown_message(self, title, text, at_mobiles=None, at_all=False):
        if not self.webhook_url:
            return {'success': False, 'message': '钉钉Webhook URL未配置'}

        data = {
            'msgtype': 'markdown',
            'markdown': {
                'title': title,
                'text': text
            },
            'at': {
                'atMobiles': at_mobiles or [],
                'isAtAll': at_all
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()
            if result.get('errcode') == 0:
                return {'success': True, 'message': '发送成功'}
            else:
                return {'success': False, 'message': result.get('errmsg', '发送失败')}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def send_report_notification(self, report):
        title = f"测试报告生成完成"
        text = f"""## 📊 测试报告通知

**报告名称**: {report.name}
**执行记录**: {report.execution.name if report.execution else '未知'}
**测试时间**: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}

### 📈 测试结果
- **总用例数**: {report.total_cases}
- **通过**: {report.passed_cases}
- **失败**: {report.failed_cases}
- **跳过**: {report.skipped_cases}
- **通过率**: {report.pass_rate}%

### 🔗 查看详情
[点击查看报告]({settings.SITE_URL}/reports/{report.id})"""

        return self.send_markdown_message(title, text)

    def send_execution_notification(self, execution):
        title = f"测试执行状态更新"
        text = f"""## 🧪 测试执行通知

**执行名称**: {execution.name}
**所属项目**: {execution.plan.project.name if execution.plan and execution.plan.project else '未知'}
**执行状态**: {execution.status}
**创建时间**: {execution.created_at.strftime('%Y-%m-%d %H:%M:%S')}

### 📋 执行详情
- **计划名称**: {execution.plan.name if execution.plan else '未知'}
- **执行者**: {execution.created_by.username if execution.created_by else '未知'}
- **用例总数**: {execution.total_cases}
- **完成数**: {execution.completed_cases}"""

        return self.send_markdown_message(title, text)