#!/usr/bin/env python3
"""
Simple Test voor Notification Service
Basis functionaliteit test zonder externe dependencies
"""

import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def mock_external_dependencies():
    """Mock alle externe dependencies."""
    # Mock externe dependencies
    sys.modules['sendgrid'] = MagicMock()
    sys.modules['twilio'] = MagicMock()
    sys.modules['aiohttp'] = MagicMock()
    sys.modules['jinja2'] = MagicMock()
    sys.modules['sqlalchemy'] = MagicMock()
    sys.modules['sqlalchemy.orm'] = MagicMock()
    sys.modules['sqlalchemy.ext.asyncio'] = MagicMock()
    sys.modules['sqlalchemy.exc'] = MagicMock()
    sys.modules['sqlalchemy.sql'] = MagicMock()
    sys.modules['sqlalchemy.sql.functions'] = MagicMock()
    sys.modules['sqlalchemy.sql.expression'] = MagicMock()
    sys.modules['sqlalchemy.sql.operators'] = MagicMock()
    sys.modules['sqlalchemy.sql.schema'] = MagicMock()
    sys.modules['sqlalchemy.sql.ddl'] = MagicMock()
    sys.modules['sqlalchemy.sql.elements'] = MagicMock()
    sys.modules['sqlalchemy.sql.selectable'] = MagicMock()
    sys.modules['sqlalchemy.sql.dml'] = MagicMock()
    sys.modules['sqlalchemy.sql.type_api'] = MagicMock()
    sys.modules['sqlalchemy.sql.sqltypes'] = MagicMock()
    sys.modules['psycopg2'] = MagicMock()

def test_imports():
    """Test of alle modules kunnen worden geïmporteerd."""
    try:
        # Mock externe dependencies
        mock_external_dependencies()
        
        # Test imports
        from src.core.database import DatabaseService
        from src.core.template import TemplateService
        from src.core.email import EmailService
        from src.core.sms import SMSService
        from src.core.slack import SlackService
        from src.core.webhook import WebhookService
        from src.core.delivery import DeliveryService
        from src.core.analytics import AnalyticsService
        
        print("✅ Alle core services kunnen worden geïmporteerd")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_database_service():
    """Test DatabaseService basis functionaliteit."""
    try:
        # Mock externe dependencies
        mock_external_dependencies()
        
        from src.core.database import DatabaseService
        
        # Test service instantiation
        db_service = DatabaseService("test-database-url")
        assert db_service is not None
        assert hasattr(db_service, 'initialize')
        assert hasattr(db_service, 'close')
        assert hasattr(db_service, 'get_session')
        
        print("✅ DatabaseService basis functionaliteit werkt")
        return True
        
    except Exception as e:
        print(f"❌ DatabaseService test failed: {str(e)}")
        return False

def test_template_service():
    """Test TemplateService basis functionaliteit."""
    try:
        # Mock externe dependencies
        mock_external_dependencies()
        
        from src.core.template import TemplateService
        from src.core.database import DatabaseService
        
        # Test service instantiation
        db_service = MagicMock()
        template_service = TemplateService(db_service)
        assert template_service is not None
        assert hasattr(template_service, 'render_template')
        assert hasattr(template_service, 'validate_template')
        
        print("✅ TemplateService basis functionaliteit werkt")
        return True
        
    except Exception as e:
        print(f"❌ TemplateService test failed: {str(e)}")
        return False

def test_delivery_service():
    """Test DeliveryService basis functionaliteit."""
    try:
        # Mock externe dependencies
        mock_external_dependencies()
        
        from src.core.delivery import DeliveryService, DeliveryRequest
        from src.core.database import DatabaseService
        
        # Test service instantiation
        db_service = MagicMock()
        delivery_service = DeliveryService(db_service)
        assert delivery_service is not None
        assert hasattr(delivery_service, 'deliver_notification')
        assert hasattr(delivery_service, 'deliver_bulk_notifications')
        
        # Test DeliveryRequest model
        request = DeliveryRequest(
            template_id="test-template",
            channel="email",
            recipient="test@example.com",
            context={"name": "John"}
        )
        assert request.template_id == "test-template"
        assert request.channel == "email"
        assert request.recipient == "test@example.com"
        assert request.context["name"] == "John"
        
        print("✅ DeliveryService basis functionaliteit werkt")
        return True
        
    except Exception as e:
        print(f"❌ DeliveryService test failed: {str(e)}")
        return False

def test_analytics_service():
    """Test AnalyticsService basis functionaliteit."""
    try:
        # Mock externe dependencies
        mock_external_dependencies()
        
        from src.core.analytics import AnalyticsService, AnalyticsRequest
        from src.core.database import DatabaseService
        
        # Test service instantiation
        db_service = MagicMock()
        analytics_service = AnalyticsService(db_service)
        assert analytics_service is not None
        assert hasattr(analytics_service, 'get_performance_metrics')
        assert hasattr(analytics_service, 'get_channel_performance')
        
        # Test AnalyticsRequest model
        from datetime import datetime
        request = AnalyticsRequest(
            start_date=datetime.now(),
            end_date=datetime.now(),
            metrics=["delivery_rate", "success_rate"]
        )
        assert request.start_date is not None
        assert request.end_date is not None
        assert len(request.metrics) == 2
        
        print("✅ AnalyticsService basis functionaliteit werkt")
        return True
        
    except Exception as e:
        print(f"❌ AnalyticsService test failed: {str(e)}")
        return False

def test_main_app():
    """Test main FastAPI app."""
    try:
        # Mock externe dependencies
        mock_external_dependencies()
        
        from src.main import app
        
        # Test app instantiation
        assert app is not None
        assert hasattr(app, 'routes')
        
        # Test health endpoints
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test health check
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # Test readiness check
        response = client.get("/health/ready")
        assert response.status_code == 200
        
        # Test liveness check
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
        
        print("✅ Main FastAPI app werkt correct")
        return True
        
    except Exception as e:
        print(f"❌ Main app test failed: {str(e)}")
        return False

def main():
    """Run alle tests."""
    print("🧪 Notification Service Simple Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Database Service", test_database_service),
        ("Template Service", test_template_service),
        ("Delivery Service", test_delivery_service),
        ("Analytics Service", test_analytics_service),
        ("Main App", test_main_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Alle tests geslaagd!")
        return True
    else:
        print("⚠️  Sommige tests gefaald")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 