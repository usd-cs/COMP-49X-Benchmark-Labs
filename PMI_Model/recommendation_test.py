import pytest
from recommendation import Recommendation, InvalidPMI

def test_create_recommendations():
    # verify it gets correct index range 
    assert Recommendation(10).json_data["PMI Value"] == '1-20'
    
    # verify an invalid PMI raises an exception
    with pytest.raises(InvalidPMI):
        Recommendation(101)

def test_get_range():
    assert Recommendation(10).get_range() == '1-20'
    assert Recommendation(30).get_range() == '20-40'
    assert Recommendation(50).get_range() == '40-60'
    assert Recommendation(70).get_range() == '60-80'
    assert Recommendation(90).get_range() == '80-100'


def test_get_risk_level():
    assert Recommendation(10).get_risk_level() == "Very Low Risk"
    assert Recommendation(30).get_risk_level() == "Low Risk"
    assert Recommendation(50).get_risk_level() == "Moderate Risk"
    assert Recommendation(70).get_risk_level() == "High Risk"
    assert Recommendation(90).get_risk_level() == "Extremely High Risk"

def test_get_strategy():
    assert Recommendation(10).get_strategy() == "Preventative Minimal"
    assert Recommendation(30).get_strategy() == "Light Preventative"
    assert Recommendation(50).get_strategy() == "Standard Protective"
    assert Recommendation(70).get_strategy() == "Intensive Management"
    assert Recommendation(90).get_strategy() == "Emergency Intervention"
    
def test_get_name():
    assert Recommendation(10).get_name() == "Sulfur-based fungicide"
    assert Recommendation(30).get_name() == "Myclobutanil"
    assert Recommendation(50).get_name() == "Propiconazole + Sulfur"
    assert Recommendation(70).get_name() == "Azoxystrobin + Tebuconazole"
    assert Recommendation(90).get_name() == "Combination Treatment: 1. Trifloxystrobin 2. Myclobutanil 3. Sulfur-based fungicide"

def get_application_rate():
    assert Recommendation(10).get_application_rate() == "5-10 lbs/acre"
    assert Recommendation(30).get_application_rate() == "4-6 fl oz/acre"
    assert Recommendation(50).get_application_rate() == "Propiconazole: 8-12 fl oz/acre, Sulfur: 10 lbs/acre"
    assert Recommendation(70).get_application_rate() == "Azoxystrobin: 6-8 fl oz/acre, Tebuconazole: 4-6 fl oz/acre"
    assert Recommendation(90).get_application_rate() == "Trifloxystrobin: 4-5 fl oz/acre, Myclobutanil: 6-8 fl oz/acre, Sulfur: 10-15 lbs/acre"


def test_get_frequency():
    assert Recommendation(10).get_frequency() == "Single application at early green tip"
    assert Recommendation(30).get_frequency() == "2 applications: green tip and tight cluster"
    assert Recommendation(50).get_frequency() == "3 applications: green tip, tight cluster, and first cover"
    assert Recommendation(70).get_frequency() == "4-5 applications: green tip through second cover"
    assert Recommendation(90).get_frequency() == "5-6 applications with 7-10 day intervals"

def test_get_additional_notes():
    additional_notes = Recommendation(10).get_additional_notes()
    assert "Monitor orchard closely" in additional_notes
    assert "Focus on cultural controls" in additional_notes
    assert "Minimal chemical intervention" in additional_notes

def test_get_purchase_links():
    purchase_links = Recommendation(70).get_purchase_links()
    assert purchase_links["Azoxystrobin"] == "https://chemicalwarehouse.com/products/azoxystrobin-2sc-ag-and-t-o"
    assert purchase_links["Tebuconazole"] == "https://www.atozlawnsupply.com/products/tebuconazole-3-6-select"

def test_get_full_info():
    full_info = Recommendation(10).get_full_info()
    assert 'PMI Value:' in full_info
    assert 'Risk Level:' in full_info
    assert 'Fungicide Strategy:' in full_info
    assert 'Application Rate:' in full_info
    assert 'Spray Frequency/Stage:' in full_info
    assert 'Additional Notes:' in full_info
    assert "Monitor orchard closely" in full_info