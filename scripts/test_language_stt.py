#!/usr/bin/env python3
"""
Test STT (Speech-to-Text) accuracy across multiple languages.

Uses browser TTS to generate audio samples, then tests Chutes STT transcription.
Compares original text with transcription to estimate accuracy.
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")
API_BASE = "http://localhost:8088"

# Test phrases for each language
TEST_PHRASES = {
    "en": [
        "Hello, I would like to order room service.",
        "What time is breakfast?",
        "Can you help me with the WiFi password?",
    ],
    "ru": [
        "Здравствуйте, я хотел бы заказать обслуживание в номер.",
        "Во сколько завтрак?",
        "Не могли бы вы помочь мне с паролем WiFi?",
    ],
    "zh": [
        "你好，我想点客房服务。",
        "早餐几点开始？",
        "你能帮我设置WiFi密码吗？",
    ],
    "ja": [
        "こんにちは、ルームサービスを注文したいです。",
        "朝食は何時ですか？",
        "WiFiパスワードを教えていただけますか？",
    ],
    "ko": [
        "안녕하세요, 룸서비스를 주문하고 싶습니다.",
        "아침 식사는 몇 시입니까?",
        "WiFi 비밀번호를 도와주시겠습니까?",
    ],
    "es": [
        "Hola, me gustaría pedir servicio de habitaciones.",
        "¿A qué hora es el desayuno?",
        "¿Puede ayudarme con la contraseña WiFi?",
    ],
    "fr": [
        "Bonjour, je voudrais commander le service de chambre.",
        "À quelle heure est le petit déjeuner?",
        "Pouvez-vous m'aider avec le mot de passe WiFi?",
    ],
    "de": [
        "Hallo, ich möchte Zimmerservice bestellen.",
        "Um wie viel Uhr ist das Frühstück?",
        "Können Sie mir mit dem WLAN-Passwort helfen?",
    ],
    "ar": [
        "مرحبا، أود طلب خدمة الغرف.",
        "ما هو وقت الإفطار؟",
        "هل يمكنك مساعدتي في كلمة مرور WiFi؟",
    ],
}


def generate_audio_from_text(text: str, language: str) -> str | None:
    """
    Generate audio using our TTS endpoint.
    Returns base64 audio or None on failure.
    """
    try:
        resp = requests.post(
            f"{API_BASE}/api/tts",
            json={"text": text, "language": language},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("audio_base64")
        else:
            print(f"  ⚠️  TTS failed: {resp.status_code}")
            return None
    except Exception as e:
        print(f"  ⚠️  TTS error: {e}")
        return None


def transcribe_audio(audio_b64: str, language: str) -> str | None:
    """
    Transcribe audio using our STT endpoint.
    Returns transcription text or None on failure.
    """
    try:
        resp = requests.post(
            f"{API_BASE}/api/transcribe",
            json={"audio_base64": audio_b64, "language": language},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("text", "")
        else:
            print(f"  ⚠️  STT failed: {resp.status_code}")
            return None
    except Exception as e:
        print(f"  ⚠️  STT error: {e}")
        return None


def calculate_similarity(original: str, transcribed: str) -> float:
    """
    Simple character-based similarity metric.
    Returns 0.0 to 1.0 (1.0 = exact match).
    """
    from difflib import SequenceMatcher
    return SequenceMatcher(None, original.lower(), transcribed.lower()).ratio()


def test_language(lang_code: str, phrases: list[str]) -> dict:
    """
    Test STT for a single language.
    Returns results dict with accuracy stats.
    """
    print(f"\n{'='*60}")
    print(f"Testing: {lang_code.upper()}")
    print(f"{'='*60}")
    
    results = []
    
    for i, original_text in enumerate(phrases, 1):
        print(f"\n[{i}/{len(phrases)}] Original: {original_text}")
        
        # Generate audio from text using TTS
        audio_b64 = generate_audio_from_text(original_text, lang_code)
        if not audio_b64:
            print("  ❌ TTS failed, skipping")
            results.append({
                "original": original_text,
                "transcribed": None,
                "similarity": 0.0,
                "status": "tts_failed"
            })
            continue
        
        # Transcribe audio back to text using STT
        transcribed = transcribe_audio(audio_b64, lang_code)
        if not transcribed:
            print("  ❌ STT failed")
            results.append({
                "original": original_text,
                "transcribed": None,
                "similarity": 0.0,
                "status": "stt_failed"
            })
            continue
        
        # Calculate similarity
        similarity = calculate_similarity(original_text, transcribed)
        status = "✅" if similarity > 0.8 else "⚠️" if similarity > 0.6 else "❌"
        
        print(f"  Transcribed: {transcribed}")
        print(f"  {status} Similarity: {similarity:.1%}")
        
        results.append({
            "original": original_text,
            "transcribed": transcribed,
            "similarity": similarity,
            "status": "ok"
        })
    
    # Calculate stats
    valid_results = [r for r in results if r["status"] == "ok"]
    if valid_results:
        avg_similarity = sum(r["similarity"] for r in valid_results) / len(valid_results)
    else:
        avg_similarity = 0.0
    
    return {
        "language": lang_code,
        "total_tests": len(phrases),
        "successful": len(valid_results),
        "failed": len(phrases) - len(valid_results),
        "avg_similarity": avg_similarity,
        "results": results
    }


def main():
    """Run STT validation tests for all languages."""
    if not CHUTES_API_KEY:
        print("❌ CHUTES_API_KEY not set")
        return 1
    
    print("🎤 STT Language Validation Test")
    print(f"API Base: {API_BASE}")
    print(f"Testing {len(TEST_PHRASES)} languages with {sum(len(p) for p in TEST_PHRASES.values())} total phrases")
    
    # Check if API is running
    try:
        resp = requests.get(f"{API_BASE}/api/health", timeout=5)
        if resp.status_code != 200:
            print(f"❌ API not responding (status {resp.status_code})")
            return 1
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        print("💡 Start API with: python api/index.py")
        return 1
    
    all_results = []
    
    # Test each language
    for lang_code, phrases in TEST_PHRASES.items():
        result = test_language(lang_code, phrases)
        all_results.append(result)
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")
    
    summary_table = []
    for r in all_results:
        status = "✅" if r["avg_similarity"] > 0.85 else "⚠️" if r["avg_similarity"] > 0.70 else "❌"
        summary_table.append({
            "Language": r["language"].upper(),
            "Tests": f"{r['successful']}/{r['total_tests']}",
            "Avg Similarity": f"{r['avg_similarity']:.1%}",
            "Status": status
        })
    
    # Print as table
    headers = ["Language", "Tests", "Avg Similarity", "Status"]
    col_widths = [max(len(str(row[h])) for row in summary_table + [{"Language": h, "Tests": h, "Avg Similarity": h, "Status": h}]) for h in headers]
    
    # Header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Rows
    for row in summary_table:
        print(" | ".join(str(row[h]).ljust(w) for h, w in zip(headers, col_widths)))
    
    # Save detailed results to JSON
    output_file = Path(__file__).parent.parent / "test_results_stt.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Recommendations
    print("\n📊 RECOMMENDATIONS:")
    for r in all_results:
        if r["avg_similarity"] > 0.85:
            print(f"  ✅ {r['language'].upper()}: Production ready")
        elif r["avg_similarity"] > 0.70:
            print(f"  ⚠️  {r['language'].upper()}: Usable with caution")
        else:
            print(f"  ❌ {r['language'].upper()}: Not recommended")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
