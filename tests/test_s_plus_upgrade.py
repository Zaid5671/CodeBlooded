import unittest
import json
import pandas as pd
from audit_rules.notifications.alert_dispatcher import generate_whatsapp_alert_payload, generate_webhook_event_payload

class TestSPlusUpgradeSuite(unittest.TestCase):

    def test_01_whatsapp_alert_payload_structure(self):
        work_sample = {
            "clean_work_id": "WS/MP620/2024-2025/133166",
            "State": "UTTAR PRADESH",
            "Constituency": "JAUNPUR",
            "standardized_category": "ROAD",
            "sanction_amount": 1500000.0,
            "audit_priority_score": 88.5,
            "evidence": ["Sanction amount is 2.4x higher than peer median."]
        }
        wa = generate_whatsapp_alert_payload(work_sample, "+919876543210")
        self.assertEqual(wa["number"], "+919876543210")
        self.assertIn("WS/MP620/2024-2025/133166", wa["textMessage"]["text"])
        self.assertIn("UTTAR PRADESH", wa["textMessage"]["text"])

    def test_02_webhook_alert_payload_structure(self):
        work_sample = {
            "clean_work_id": "WS/MP620/2024-2025/133166",
            "State": "UTTAR PRADESH",
            "District": "JAUNPUR",
            "sanction_amount": 1500000.0,
            "audit_priority_score": 88.5
        }
        wh = generate_webhook_event_payload(work_sample)
        self.assertEqual(wh["event_type"], "AUDIT_PRIORITY_ALERT")
        self.assertEqual(wh["work"]["work_id"], "WS/MP620/2024-2025/133166")
        self.assertEqual(wh["work"]["sanction_amount"], 1500000.0)

if __name__ == '__main__':
    unittest.main()
