from app.services.risk_engine import calculate_risk

def test_behavior_first_critical_override():
    result = calculate_risk(
        behavioral=100,
        linguistic=70,
        structural=20,
        technical=0,
        red_flags=[
            {"message": "Sensitive identity or financial information is requested."},
            {"message": "A payment, fee, deposit, or paid verification is requested."},
        ],
    )
    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] >= 85
