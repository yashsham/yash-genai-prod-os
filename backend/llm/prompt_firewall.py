# Delegation to Security Framework
from backend.input_defense.injection_scanner import RegexInjectionScanner
from backend.input_defense.content_filter import KeywordContentFilter

scanner = RegexInjectionScanner()
fileter = KeywordContentFilter()

def scan_and_filter_input(prompt: str) -> str:
    """
    Scans input for injections and bad content.
    Raises ValueError if unsafe.
    Returns cleaned prompt (if applicable).
    """
    # 1. Injection Scan
    scan_res = scanner.scan_prompt(prompt)
    if not scan_res["is_safe"]:
        raise ValueError(f"Security Alert: {scan_res['reason']}")

    # 2. Content Filter
    content_res = fileter.check_content(prompt)
    if content_res["blocked"]:
        raise ValueError(f"Content Violation: {content_res['categories']}")

    return prompt
