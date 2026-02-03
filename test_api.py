#!/usr/bin/env python
"""Test Z.AI API integration"""
import os
import sys
import requests

os.environ["ZHIPUAI_API_KEY"] = "507b2d0bb71945aab07c0e22bc666d4a.RiY1d2GYmM0Eodp3"

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Import Flask app
from index import app

def test_chat():
    """Test the chat endpoint"""
    with app.test_client() as client:
        response = client.post('/api/chat', json={
            'message': 'Say hello',
            'session_id': 'test123'
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        if response.status_code == 200:
            print("\n✅ Chat endpoint working!")
        else:
            print(f"\n❌ Error: {response.status_code}")

if __name__ == "__main__":
    test_chat()
