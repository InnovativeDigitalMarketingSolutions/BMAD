
#!/usr/bin/env python3
"""
Test script for robust message bus implementation
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from bmad.agents.core.communication.message_bus import publish, get_events, get_statistics

def test_robust_message_bus():
    """Test the robust message bus implementation."""
    
    print("🧪 Testing robust message bus implementation...")
    
    # Test publishing events
    test_events = [
        ("test_event_1", {"message": "Test event 1"}),
        ("test_event_2", {"message": "Test event 2"}),
        ("test_event_3", {"message": "Test event 3"})
    ]
    
    for event_type, data in test_events:
        success = publish(event_type, data)
        if success:
            print(f"✅ Published event: {event_type}")
        else:
            print(f"❌ Failed to publish event: {event_type}")
    
    # Test getting events
    events = get_events()
    print(f"📊 Retrieved {len(events)} events")
    
    # Test statistics
    stats = get_statistics()
    print(f"📈 Statistics: {stats}")
    
    print("✅ Robust message bus test completed")

if __name__ == "__main__":
    test_robust_message_bus()
