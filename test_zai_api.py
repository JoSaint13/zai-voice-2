"""Quick test script for ZhipuAI / Z.AI API connectivity."""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ZHIPUAI_API_KEY")
print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}" if API_KEY else "ERROR: No API key found!")

import requests
from zhipuai import ZhipuAI

BASE_URL = "https://open.bigmodel.cn"
client = ZhipuAI(api_key=API_KEY)

# --- Test models ---
MODELS = ["glm-4-flash", "glm-4", "glm-4-plus", "glm-4.7", "glm-3-turbo", "chatglm_turbo", "glm-4-air"]

for model in MODELS:
    print(f"\n{'='*50}")
    print(f"Testing model: {model}")
    print(f"{'='*50}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello in 5 words"}],
            max_tokens=20,
        )
        print(f"✅ SUCCESS: {response.choices[0].message.content}")
        print(f"   Tokens: {response.usage.total_tokens}")
    except Exception as e:
        err = str(e)[:150]
        print(f"❌ FAILED: {err}")

# --- Test 3: ASR endpoint availability ---
print("\n" + "="*50)
print("TEST 3: ASR endpoint (audio transcription) — ping only")
print("="*50)
try:
    r = requests.post(
        f"{BASE_URL}/paas/v4/audio/transcriptions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        data={"model": "glm-asr-2512", "stream": "false"},
        files={"file": ("test.wav", b"\x00" * 100, "audio/wav")},
        timeout=15,
    )
    print(f"   HTTP Status: {r.status_code}")
    if r.status_code == 200:
        print(f"✅ ASR endpoint responded OK")
    else:
        # 400 = bad audio but endpoint is reachable; 401/403 = auth issue
        body = r.text[:200]
        if r.status_code == 400:
            print(f"✅ ASR endpoint reachable (400 = bad test audio, expected)")
        elif r.status_code in (401, 403):
            print(f"❌ Auth error: {body}")
        else:
            print(f"⚠️  Response: {body}")
except Exception as e:
    print(f"❌ FAILED: {type(e).__name__}: {e}")

print("\n" + "="*50)
print("Done!")
