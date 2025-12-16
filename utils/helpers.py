from datetime import datetime, timedelta
import pytz

NEPAL_TZ = pytz.timezone("Asia/Kathmandu")

def now_np():
    return datetime.now(NEPAL_TZ)

def today_str():
    return now_np().strftime("%Y-%m-%d")

def is_after_11_am():
    now = now_np()
    return now.hour >= 11

def parse_tasks(content):
    total = 0
    completed = 0
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("-") or stripped.startswith("*"):
            total += 1
            if stripped.startswith("- ~~") or stripped.startswith("* ~~"):
                if stripped.endswith("~~"):
                    completed += 1
    return total, completed

def validate_task_format(content):
    lines = content.splitlines()
    task_lines = [line.strip() for line in lines if line.strip()]
    
    if not task_lines:
        return False, "No tasks found. Tasks must start with '- ' or '* '"
    
    for line in task_lines:
        if not (line.startswith("- ") or line.startswith("* ")):
            return False, f"Invalid format: '{line}'. All tasks must start with '- ' or '* '"
        
        if "~~" in line:
            if not (line.startswith("- ~~") or line.startswith("* ~~")):
                return False, f"Invalid strikethrough format: '{line}'. Use '- ~~Task~~' format"
            if not line.endswith("~~"):
                return False, f"Invalid strikethrough format: '{line}'. Strikethrough must end with '~~'"
    
    return True, ""

def clean_old_leaves(leaves):
    today = now_np().date()
    return [
        d for d in leaves
        if today - datetime.strptime(d, "%Y-%m-%d").date() <= timedelta(days=90)
    ]
