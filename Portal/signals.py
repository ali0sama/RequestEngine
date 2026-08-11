import logging

audit_logger = logging.getLogger("portal.audit")


def log_failed_login(sender, credentials, request=None, **kwargs):
    username = credentials.get("username", "<unknown>")
    audit_logger.warning("Login failed for username=%s", username)
