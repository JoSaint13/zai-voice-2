"""
Chat provider for skills — calls Chutes.ai via requests.
Shared by all skills instead of the ZhipuAI SDK.
"""

import os
import re
import logging
import requests

logger = logging.getLogger(__name__)

CHUTES_API_KEY = os.getenv('CHUTES_API_KEY', '')

# Default model and slug for skills
DEFAULT_MODEL = 'deepseek-ai/DeepSeek-V3-0324'
DEFAULT_SLUG = 'chutes-deepseek-ai-deepseek-v3-0324-tee'


def skill_chat(messages, model_id=None, slug=None, temperature=0.7, max_tokens=1024):
    """
    Chat completion via Chutes.ai for skill execution.
    Returns the assistant message text. Raises on error.
    """
    mid = model_id or DEFAULT_MODEL
    s = slug or DEFAULT_SLUG
    url = f"https://{s}.chutes.ai/v1/chat/completions"

    if not CHUTES_API_KEY:
        raise ValueError("No CHUTES_API_KEY configured")

    headers = {
        'Authorization': f'Bearer {CHUTES_API_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        'model': mid,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }

    logger.info(f"[skill_chat] {mid} — {len(messages)} msgs")

    r = requests.post(url, headers=headers, json=payload, timeout=(5, 60))

    if r.status_code != 200:
        try:
            body = r.json()
            msg = body.get("error", {}).get("message", r.text[:200])
        except Exception:
            msg = r.text[:200]
        raise RuntimeError(f"[Chutes] HTTP {r.status_code}: {msg}")

    data = r.json()
    msg_obj = data['choices'][0]['message']
    content = msg_obj.get('content') or msg_obj.get('reasoning_content') or ''

    # Strip <think>...</think> blocks from reasoning models
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

    return content
