from typing import Dict, Optional

from fastapi import Request


DEFAULT_LOCALE = "en"


MESSAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "backend.api_running": "Neuro Pulse API is running.",
        "backend.api_only": "Neuro Pulse API is running (API-only mode).",
        "backend.frontend_missing": "<h1>Neuro Pulse</h1><p>Frontend not built yet.</p>",
        "auth.invalid_credentials": "Unable to validate credentials.",
        "auth.user_disabled": "User account is disabled.",
        "auth.email_exists": "This email is already registered.",
        "auth.username_exists": "This username is already in use.",
        "auth.login_failed": "Incorrect email/username or password.",
        "auth.logout_success": "Logged out successfully.",
        "auth.password_incorrect": "Current password is incorrect.",
        "auth.password_updated": "Password updated successfully.",
        "device.bound_elsewhere": "This device is already linked to another account.",
        "device.not_found": "Device not found or not linked to this account.",
        "device.default_name": "Device {suffix}",
        "data.session_not_found": "Session not found.",
        "data.upload_received": "Data received.",
        "data.batch_received": "Batch data received.",
        "report.custom_dates_required": "Custom reports require a start and end date.",
        "report.observation.severity_up": "Tremor severity is trending upward and should be monitored closely.",
        "report.observation.severity_down": "Tremor severity improved during the selected period.",
        "report.observation.frequency_up": "Tremor episode frequency increased.",
        "report.observation.frequency_down": "Tremor episode frequency decreased.",
        "report.observation.severe_count": "{count} severe tremor episodes (levels 3-4) were recorded in the past {days} days.",
        "report.recommendation.medication": "Discuss medication timing or dosage with the treating clinician.",
        "report.recommendation.monitoring": "Increase monitoring frequency to improve trend confidence.",
        "report.recommendation.wear_time": "Increase wearable usage time to capture more reliable daily data.",
        "ai.not_configured": "AI service is not configured.",
        "ai.gateway_error": "AI service returned status {status_code}.",
        "ai.timeout": "AI service timed out.",
        "ai.error": "AI service error: {error}",
        "ai.chat_intro": "You are the Neuro Pulse AI assistant. Help users understand tremor trends, explain symptom patterns, and suggest appropriate next steps without making diagnoses.",
        "ai.chat_role_1": "Explain the user's tremor data clearly.",
        "ai.chat_role_2": "Offer educational guidance about Parkinsonian tremor.",
        "ai.chat_role_3": "Suggest practical daily-management ideas without replacing clinical care.",
        "ai.chat_role_4": "Recommend professional follow-up when needed.",
        "ai.chat_reminder_1": "Encourage consultation with clinicians for diagnosis or treatment decisions.",
        "ai.chat_reminder_2": "Avoid diagnostic claims.",
        "ai.chat_reminder_3": "Respond in concise English.",
        "ai.suggestion_1": "What stands out in my tremor patterns?",
        "ai.suggestion_2": "How can I reduce tremor symptoms during the day?",
        "ai.suggestion_3": "When should I contact a clinician?",
    },
    "zh-CN": {
        "backend.api_running": "Neuro Pulse API 服务正常运行。",
        "backend.api_only": "Neuro Pulse API 服务正常运行（仅 API 模式）。",
        "backend.frontend_missing": "<h1>Neuro Pulse</h1><p>前端尚未构建。</p>",
        "auth.invalid_credentials": "无法验证凭据。",
        "auth.user_disabled": "用户已被禁用。",
        "auth.email_exists": "该邮箱已被注册。",
        "auth.username_exists": "该用户名已被使用。",
        "auth.login_failed": "邮箱/用户名或密码错误。",
        "auth.logout_success": "登出成功。",
        "auth.password_incorrect": "当前密码错误。",
        "auth.password_updated": "密码修改成功。",
        "device.bound_elsewhere": "设备已绑定到其他账户。",
        "device.not_found": "设备不存在或未绑定。",
        "device.default_name": "设备 {suffix}",
        "data.session_not_found": "会话不存在。",
        "data.upload_received": "数据已接收。",
        "data.batch_received": "批量数据已接收。",
        "report.custom_dates_required": "自定义报告需要指定起止日期。",
        "report.observation.severity_up": "震颤严重程度呈上升趋势，建议密切关注。",
        "report.observation.severity_down": "震颤严重程度有所改善。",
        "report.observation.frequency_up": "震颤发作频率增加。",
        "report.observation.frequency_down": "震颤发作频率减少。",
        "report.observation.severe_count": "过去 {days} 天内有 {count} 次严重震颤（等级 3-4）。",
        "report.recommendation.medication": "建议与主治医生讨论用药方案。",
        "report.recommendation.monitoring": "建议增加监测频率。",
        "report.recommendation.wear_time": "建议增加佩戴时间以获得更准确的数据。",
        "ai.not_configured": "AI 服务未配置。",
        "ai.gateway_error": "AI 服务响应错误：{status_code}。",
        "ai.timeout": "AI 服务响应超时。",
        "ai.error": "AI 服务错误：{error}",
        "ai.chat_intro": "你是 Neuro Pulse 的 AI 健康助手，帮助用户理解震颤趋势、解释症状模式，并在不做诊断的前提下给出适当建议。",
        "ai.chat_role_1": "帮助用户理解他们的震颤数据。",
        "ai.chat_role_2": "提供关于帕金森性震颤的科普说明。",
        "ai.chat_role_3": "给出日常管理建议，但不能替代医生诊疗。",
        "ai.chat_role_4": "在需要时建议寻求专业医生帮助。",
        "ai.chat_reminder_1": "涉及诊断和治疗决策时提醒用户咨询医生。",
        "ai.chat_reminder_2": "不要做出诊断性表述。",
        "ai.chat_reminder_3": "使用简洁友好的中文回答。",
        "ai.suggestion_1": "我的震颤趋势最值得关注的是什么？",
        "ai.suggestion_2": "白天如何减轻震颤症状？",
        "ai.suggestion_3": "什么时候应该联系医生？",
    },
}


def resolve_locale_from_header(header_value: Optional[str]) -> str:
    if not header_value:
        return DEFAULT_LOCALE

    normalized = header_value.lower()
    if normalized.startswith("zh"):
        return "zh-CN"
    return "en"


def get_locale(request: Request) -> str:
    return resolve_locale_from_header(request.headers.get("accept-language"))


def msg(locale: str, key: str, **kwargs) -> str:
    template = MESSAGES.get(locale, MESSAGES[DEFAULT_LOCALE]).get(key) or MESSAGES[DEFAULT_LOCALE].get(key, key)
    return template.format(**kwargs)
