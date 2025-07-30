from integrations.slack.slack_notify import send_slack_message
from unittest.mock import patch, MagicMock

def test_slack_error_handling():
    # Mock the requests.post call to return an error response
    with patch('requests.post') as mock_post:
        # Create a mock error response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ok": False,
            "error": "channel_not_found"
        }
        mock_response.text = '{"ok":false,"error":"channel_not_found"}'
        mock_post.return_value = mock_response
        
        try:
            send_slack_message("Dit zou moeten falen (ongeldige channel)", "INVALID_CHANNEL_ID", use_api=True)
        except Exception as e:
            assert "channel_not_found" in str(e)
        else:
            assert False, "Geen fout opgetreden bij ongeldig kanaal" 