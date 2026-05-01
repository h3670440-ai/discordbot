#!/usr/bin/env python3
"""
Test script to verify Vanity API is working correctly
"""
import requests
import json

API_URL = "https://worker-production-31dc.up.railway.app"

def test_health():
    """Test if server is online"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_database():
    """Test database connectivity"""
    print("\nTesting database endpoint...")
    try:
        response = requests.get(f"{API_URL}/test", timeout=10)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data.get("status") == "ok"
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_check(key, hwid="test-hwid-123"):
    """Test key verification"""
    print(f"\nTesting check endpoint with key: {key}")
    try:
        response = requests.get(
            f"{API_URL}/check",
            params={"key": key, "hwid": hwid},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("VANITY API TEST SUITE")
    print("=" * 60)
    
    # Test 1: Health Check
    health_ok = test_health()
    
    # Test 2: Database
    db_ok = test_database()
    
    # Test 3: Key Check (you'll need to provide a real key)
    print("\n" + "=" * 60)
    test_key = input("Enter a key to test (or press Enter to skip): ").strip()
    if test_key:
        test_check(test_key)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Health Check: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"Database:     {'✓ PASS' if db_ok else '✗ FAIL'}")
    print("=" * 60)
    
    if health_ok and db_ok:
        print("\n✓ API is working correctly!")
    else:
        print("\n✗ API has issues. Check Railway logs for details.")
