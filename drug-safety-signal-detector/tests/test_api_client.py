from unittest.mock import MagicMock, patch
import requests
from src.api_client import fetch_events


@patch("src.api_client.requests.get")
def test_fetch_events_success(mock_get):
    """Vérifie l'extraction correcte lorsque l'API renvoie des résultats valides."""
    # Simulation d'une réponse 200 avec payload FAERS standard
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "safetyreportid": "US-FDA-1001",
                "patient": {
                    "drug": [{"medicinalproduct": "ASPIRIN", "drugcharacterization": "1"}],
                    "reaction": [{"reactionmeddrapt": "Headache"}],
                },
            }
        ]
    }
    mock_get.return_value = mock_response

    events = fetch_events(drug_name="ASPIRIN", limit=1)

    assert len(events) == 1
    assert events[0]["safetyreportid"] == "US-FDA-1001"
    mock_get.assert_called_once()


@patch("src.api_client.requests.get")
def test_fetch_events_404_not_found(mock_get):
    """Vérifie que l'absence de résultats (code 404 openFDA) renvoie une liste vide sans crasher."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    events = fetch_events(drug_name="SUBSTANCE_INCONNUE_XYZ", limit=10)

    assert events == []
    mock_get.assert_called_once()


@patch("src.api_client.requests.get")
def test_fetch_events_network_timeout(mock_get):
    """Vérifie la robustesse en cas de panne réseau ou de dépassement de délai d'attente."""
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

    events = fetch_events(drug_name="ASPIRIN", limit=10)

    assert events == []
    mock_get.assert_called_once()