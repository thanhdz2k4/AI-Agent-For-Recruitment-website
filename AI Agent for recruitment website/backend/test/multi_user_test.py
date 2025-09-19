#!/usr/bin/env python3
"""
Test multi-user functionality for ChatBot Flask API
"""
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor
import random

BASE_URL = "http://127.0.0.1:5000"

def simulate_user_session(user_id, num_messages=5):
    """Simulate a user session with multiple messages"""
    print(f"🧑‍💼 User {user_id} starting session...")
    
    # Create a session
    session = requests.Session()
    
    messages = [
        "Hello, I'm looking for a job",
        "What skills do I need for software engineering?",
        "How should I prepare for an interview?",
        "Can you help me with my resume?",
        "What's the average salary for this position?"
    ]
    
    user_messages = []
    
    for i in range(num_messages):
        message = random.choice(messages) + f" (User {user_id}, message {i+1})"
        
        try:
            # Send chat message
            response = session.post(
                f"{BASE_URL}/api/chat",
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id', 'unknown')[:8]
                intent = data.get('intent', 'unknown')
                
                user_messages.append({
                    'message': message,
                    'response': data['response'][:100] + "...",
                    'intent': intent,
                    'session_id': session_id
                })
                
                print(f"✅ User {user_id} ({session_id}): {message} -> {intent}")
                
            else:
                print(f"❌ User {user_id}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ User {user_id}: Exception {e}")
            
        # Random delay between messages
        time.sleep(random.uniform(0.5, 2.0))
    
    # Get session info
    try:
        info_response = session.get(f"{BASE_URL}/api/session/info")
        if info_response.status_code == 200:
            info_data = info_response.json()
            print(f"📊 User {user_id} session info: {info_data['history_length']} messages")
    except:
        pass
    
    return user_messages

def test_multi_user():
    """Test multiple users simultaneously"""
    print("🚀 Testing Multi-User ChatBot Functionality")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running or not healthy")
            return
        print("✅ Server is running")
    except:
        print("❌ Cannot connect to server. Make sure Flask app is running!")
        return
    
    # Simulate multiple users
    num_users = 3
    messages_per_user = 3
    
    print(f"\n🧪 Simulating {num_users} users with {messages_per_user} messages each...")
    
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = []
        
        for user_id in range(1, num_users + 1):
            future = executor.submit(simulate_user_session, user_id, messages_per_user)
            futures.append(future)
        
        # Wait for all users to complete
        results = []
        for future in futures:
            result = future.result()
            results.append(result)
    
    print("\n📈 Results Summary:")
    print("-" * 30)
    
    for i, user_result in enumerate(results, 1):
        print(f"User {i}: {len(user_result)} messages sent")
        for msg in user_result:
            print(f"  - {msg['intent']}: {msg['message'][:50]}...")
    
    # Get server session info
    try:
        sessions_response = requests.get(f"{BASE_URL}/api/sessions")
        if sessions_response.status_code == 200:
            sessions_data = sessions_response.json()
            print(f"\n🖥️  Server Sessions: {sessions_data['active_sessions']} active")
            print(f"Cleaned up: {sessions_data['cleaned_up_sessions']} sessions")
            
            for session in sessions_data['sessions']:
                print(f"  - Session {session['session_id']}: {session['history_length']} messages")
        
    except Exception as e:
        print(f"❌ Could not get server session info: {e}")
    
    print("\n✅ Multi-user test completed!")

if __name__ == "__main__":
    test_multi_user()