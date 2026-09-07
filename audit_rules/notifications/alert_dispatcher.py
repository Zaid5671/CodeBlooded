import json
import time

def generate_whatsapp_alert_payload(work_data, recipient_phone="+919876543210"):
    """
    Generates a WhatsApp Business API compatible JSON payload (Evolution-Go / WhatsApp API format)
    for instant audit alert notifications on CRITICAL AUDIT PRIORITY works.
    """
    clean_id = work_data.get("clean_work_id") or work_data.get("work_id") or "UNKNOWN_WORK"
    sanction_amt = work_data.get("sanction_amount", 0.0)
    category = work_data.get("standardized_category") or work_data.get("work_category") or "GENERAL"
    state = work_data.get("State") or "N/A"
    constituency = work_data.get("Constituency") or "N/A"
    audit_score = work_data.get("audit_priority_score") or work_data.get("audit_score") or 0.0
    evidence = work_data.get("evidence") or work_data.get("audit_evidence") or []
    
    evidence_str = "\n".join([f"• {e}" for e in evidence[:3]]) if evidence else "• High multi-signal statistical anomaly score."

    message_text = (
        f"🚨 *MPLADS AUDIT ALERT — CRITICAL PRIORITY*\n\n"
        f"📌 *Work ID*: `{clean_id}`\n"
        f"🏛️ *Location*: {constituency}, {state}\n"
        f"🏷️ *Category*: {category}\n"
        f"💰 *Sanctioned Amount*: ₹{sanction_amt:,.2f}\n"
        f"⚖️ *Audit Priority Score*: {audit_score:.1f} / 100\n\n"
        f"🔍 *Triggered Audit Evidence*:\n{evidence_str}\n\n"
        f"⚠️ *Governance Note*: Requires administrative audit review. Statistical anomaly, not proof of fraud."
    )

    return {
        "number": recipient_phone,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": message_text
        },
        "metadata": {
            "work_id": clean_id,
            "timestamp": int(time.time()),
            "alert_level": "CRITICAL_AUDIT_PRIORITY",
            "score": audit_score
        }
    }

def generate_webhook_event_payload(work_data):
    """
    Generates a standard Webhook JSON payload for external government monitoring systems.
    """
    return {
        "event_type": "AUDIT_PRIORITY_ALERT",
        "timestamp": int(time.time()),
        "work": {
            "work_id": work_data.get("clean_work_id") or work_data.get("work_id"),
            "state": work_data.get("State"),
            "district": work_data.get("District"),
            "constituency": work_data.get("Constituency"),
            "category": work_data.get("standardized_category") or work_data.get("work_category"),
            "sanction_amount": work_data.get("sanction_amount"),
            "audit_priority_tier": work_data.get("audit_priority_tier", "CRITICAL AUDIT PRIORITY"),
            "audit_priority_score": work_data.get("audit_priority_score", 0.0),
            "evidence": work_data.get("evidence", [])
        }
    }
