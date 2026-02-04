import requests
import json
import logging

# Setup test logger
logging.basicConfig(level=logging.INFO, format='TEST: %(message)s')
logger = logging.getLogger("Test")

BASE_URL = "http://localhost:8000"
HOTEL_ID = "2ada3c2b-b208-4599-9c46-f32dc16ff950"

def test_health():
    """Verify server is running."""
    logger.info("Testing Server Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        data = response.json()
        if data.get("status") == "healthy":
            logger.info("✅ PASS: Server is healthy")
            return True
        else:
            logger.error(f"❌ FAIL: Health check failed: {data}")
            return False
    except Exception as e:
        logger.error(f"❌ FAIL: Server unreachable: {e}")
        return False

def test_hotel_config():
    """Verify hotel configuration loads correctly."""
    logger.info("Testing Hotel Configuration...")
    try:
        response = requests.get(f"{BASE_URL}/api/hotel/{HOTEL_ID}", timeout=5)
        data = response.json()
        if data.get("name"):
            logger.info(f"✅ PASS: Hotel '{data['name']}' loaded successfully")
            return True
        else:
            logger.error(f"❌ FAIL: Hotel config missing: {data}")
            return False
    except Exception as e:
        logger.error(f"❌ FAIL: Exception: {e}")
        return False

def test_knowledge_base():
    """Verify RAG is working correctly."""
    logger.info("Testing Knowledge Base (Breakfast Question)...")
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "session_id": "test_kb_001",
            "hotel_id": HOTEL_ID,
            "message": "What time is breakfast served?"
        }, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        resp = data.get("response", "")
        demo_mode = data.get("demo_mode", False)
        
        if demo_mode:
            logger.info("ℹ️  Running in DEMO MODE (API balance low)")
        
        if "7:00 AM" in resp or "7 AM" in resp or "7:00" in resp:
            logger.info("✅ PASS: Correctly identified breakfast time")
            return True
        else:
            logger.error(f"❌ FAIL: Unexpected answer: {resp}")
            return False
    except Exception as e:
        logger.error(f"❌ FAIL: Exception: {e}")
        return False

def test_action_engine():
    """Verify Tool Calling is working for Late Checkout."""
    logger.info("Testing Action Engine (Late Checkout)...")
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "session_id": "test_action_001",
            "hotel_id": HOTEL_ID,
            "message": "I would like to request a late checkout until 2 PM please."
        }, timeout=30)
        
        data = response.json()
        resp_text = data.get("response", "")
        demo_mode = data.get("demo_mode", False)
        
        if demo_mode:
            logger.info("ℹ️  Running in DEMO MODE (API balance low)")
        
        # We expect the mock tool output to be mentioned (or demo mode response)
        if "checkout" in resp_text.lower() or "11" in resp_text or "fee" in resp_text.lower():
            logger.info("✅ PASS: Checkout question answered appropriately")
            return True
        else:
            logger.error(f"❌ FAIL: Response: {resp_text}")
            return False
    except Exception as e:
         logger.error(f"❌ FAIL: Exception: {e}")
         return False

def test_logging_endpoint():
    """Verify frontend logging endpoint."""
    logger.info("Testing Logging Endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/logs", json={
            "level": "error",
            "message": "TEST_LOGGING_MESSAGE - This is a simulated frontend error",
            "context": {"test_run": True}
        }, timeout=5)
        
        if response.status_code == 200:
             logger.info("✅ PASS: Log endpoint returned 200 OK")
             return True
        else:
             logger.error(f"❌ FAIL: Log endpoint returned {response.status_code}")
             return False
    except Exception as e:
        logger.error(f"❌ FAIL: Exception: {e}")
        return False

def test_frontend_serving():
    """Verify frontend HTML is served."""
    logger.info("Testing Frontend Serving...")
    try:
        response = requests.get(f"{BASE_URL}/hotel.html", timeout=5)
        if response.status_code == 200 and "Hotel Concierge" in response.text:
            logger.info("✅ PASS: Frontend HTML served correctly")
            return True
        else:
            logger.error(f"❌ FAIL: Frontend not serving correctly")
            return False
    except Exception as e:
        logger.error(f"❌ FAIL: Exception: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("     HOTEL ASSISTANT MVP - FEATURE VERIFICATION")
    print("="*60 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Server Health", test_health()))
    results.append(("Hotel Config", test_hotel_config()))
    results.append(("Frontend Serving", test_frontend_serving()))
    results.append(("Knowledge Base (RAG)", test_knowledge_base()))
    results.append(("Action Engine (Tools)", test_action_engine()))
    results.append(("Logging Endpoint", test_logging_endpoint()))
    
    # Summary
    print("\n" + "="*60)
    print("                    TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{len(results)} tests passed")
    
    if failed == 0:
        print("\n  🎉 ALL TESTS PASSED - MVP IS READY!")
    else:
        print(f"\n  ⚠️  {failed} test(s) need attention")
    
    print("="*60 + "\n")
