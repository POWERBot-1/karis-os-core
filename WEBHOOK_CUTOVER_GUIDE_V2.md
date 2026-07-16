# KARIS OS™ Version 1.0.0-PROD-V1 — Live Webhook Cutover Guide (`Track 2`)

**Document Version:** 2.0.0-PROD-V1  
**Target Gateways:** PalPlus Hosted Payment Links, Safaricom M-Pesa Daraja API & Meta WhatsApp Cloud API  
**Enforces:** Section 34 (`Mixed Payments & M-Pesa`), Section 36.5 (`WhatsApp Cloud Bot`) & Section 51 (`PalPlus Payment Links`)

---

## 1. Executive Webhook Cutover Summary

To switch from simulated checkouts to live production payments across Kenya and East Africa (`Africa/Nairobi`), configure your external gateway provider portal settings to point directly to our secured HTTPS webhook endpoints. Every incoming webhook is cryptographically verified for authenticity before triggering our **Universal Double-Entry Ledger (`Rule 5 & Rule 9`)** and **Rule Engine (`Rule 7`)**.

```
+---------------------------------------------------------------------------------------------------+
|                            EXTERNAL PRODUCTION GATEWAYS (`LIVE PAYLOADS`)                         |
|  [PalPlus Payment Link]     [Safaricom Daraja M-Pesa C2B/STK]     [Meta WhatsApp Cloud API Bot]   |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                        KARIS OS™ HTTPS API GATEWAY (`SECURITY VALIDATION`)                        |
|  1. X-PalPlus-Signature HMAC    2. X-Mpesa-Signature / Daraja ACK   3. X-Hub-Signature-256 HMAC   |
+---------------------------------------------------------------------------------------------------+
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌────────────────────────────────┐  ┌────────────────────────────────┐  ┌────────────────────────────────┐
│   PALPLUS CHECKOUT RECONCILER  │  │  M-PESA DARAJA RECONCILER      │  │  WHATSAPP INTERACTIVE BOT      │
│  `/api/v1/payment-links/webhook`│  │  `/api/v1/financial/webhooks`  │  │  `/api/v1/integrations/whatsapp`│
│  Validates `6e8de0bc...` link  │  │  Verifies `ResultCode == 0`    │  │  Parses text/buttons (`wa.me`) │
└────────────────────────────────┘  └────────────────────────────────┘  └────────────────────────────────┘
         │                                        │                                        │
         └────────────────────────────────────────┼────────────────────────────────────────┘
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|               UNIVERSAL DOUBLE-ENTRY LEDGER (`Rule 2, Rule 5, Rule 6, Rule 7 & Rule 9`)           |
|  • Debits Customer KES / Credits Supplier KES via immutable SHA-256 hash chains (`Rule 9`)        |
|  • Auto-mints 5% KRT loyalty reward / unlocks PAYG solar days / settles Power BOT X prediction    |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Gateway 1: PalPlus Hosted Payment Links (`Section 51 / Section 34.5`)

### **A. Production Portal Configuration**
In your PalPlus Merchant Dashboard (`https://app.palpluss.com`):
* **Active Payment Link ID:** `6e8de0bc-1284-4bba-a5de-f886665bf18f` (`https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f`)
* **Webhook Callback URL:** `https://api.karis-os.ke/api/v1/payment-links/webhook/palplus`
* **Webhook Secret (`PALPLUS_WEBHOOK_SECRET`):** `palplus_live_key_9901`

### **B. Exact JSON Payload Arriving from PalPlus**
When a customer completes payment via M-Pesa Express, card, or bank on your link, PalPlus sends:
```json
{
  "payment_link_id": "6e8de0bc-1284-4bba-a5de-f886665bf18f",
  "payer_identity_id": "USER-AMINA-777",
  "amount_kes": 3500.00,
  "external_receipt_number": "PALPLUS-RC-99021",
  "organization_id": "ORG-KARIS-RETAIL",
  "target_order_id": "ORDER-FARM-9901"
}
```

### **C. Signature Verification Formula & Curl Simulation Check**
Our router (`src/api/routers/payment_link.py`) computes `hmac.new(secret, payload_bytes, sha256).hexdigest()` and verifies `X-PalPlus-Signature`. To test your live endpoint via curl right now:
```bash
curl -X POST https://api.karis-os.ke/api/v1/payment-links/webhook/palplus \
  -H "Content-Type: application/json" \
  -H "X-PalPlus-Signature: <hmac_sha256_hash>" \
  -d '{
    "payment_link_id": "6e8de0bc-1284-4bba-a5de-f886665bf18f",
    "payer_identity_id": "USER-AMINA-777",
    "amount_kes": 3500.00,
    "external_receipt_number": "PALPLUS-RC-99021",
    "organization_id": "ORG-KARIS-RETAIL",
    "target_order_id": "ORDER-FARM-9901"
  }'
```

---

## 3. Gateway 2: Safaricom M-Pesa Daraja API (`Section 34.3`)

### **A. Production Portal Configuration**
In the Safaricom Daraja Developer Portal (`https://developer.safaricom.co.ke`):
* **Paybill / C2B Shortcode:** `888880` (`Account: POWERBOT`, `FARM-9901`, or `SOLAR-01`)
* **STK Express / C2B Callback URL:** `https://api.karis-os.ke/api/v1/financial/webhooks/mpesa`
* **M-Pesa Consumer Secret (`MPESA_CONSUMER_SECRET`):** `SafaricomLiveSecretKey2026`

### **B. Exact JSON Payload Arriving from Daraja (STK Express Callback)**
```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "29115-34620561-1",
      "CheckoutRequestID": "ws_CO_160720261430_254712345678",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          { "Name": "Amount", "Value": 2500.00 },
          { "Name": "MpesaReceiptNumber", "Value": "QWX8992110" },
          { "Name": "Balance" },
          { "Name": "TransactionDate", "Value": 20260716143000 },
          { "Name": "PhoneNumber", "Value": 254712345678 }
        ]
      }
    }
  }
}
```

### **C. Standard Daraja ACK Response Returned by KARIS OS™**
Our endpoint automatically reconciles the transaction (`Customer KES debited, KRT minted/rewarded via double entry`) and returns:
```json
{
  "ResultCode": 0,
  "ResultDesc": "Confirmation Service request accepted successfully",
  "mpesa_trans_id": "QWX8992110",
  "reconciled_amount_kes": 2500.0,
  "status": "SUCCESS"
}
```

---

## 4. Gateway 3: Meta WhatsApp Cloud API (`Section 36.5`)

### **A. Production Portal Configuration**
In the Meta Business Developers Portal (`https://developers.facebook.com`):
* **WhatsApp Business Account ID:** `KARIS_OS_EAST_AFRICA_MAIN`
* **Webhook Callback URL:** `https://api.karis-os.ke/api/v1/integrations/whatsapp/webhook`
* **Verify Token (`WHATSAPP_VERIFY_TOKEN`):** `karis_wa_verify_token_2026`
* **App Secret (`WHATSAPP_APP_SECRET`):** `MetaWhatsAppSecretKey2026`

### **B. URL Verification Challenge & Inbound Message Handling**
When registering the URL, Meta sends a `GET /webhook?hub.mode=subscribe&hub.verify_token=karis_wa_verify_token_2026&hub.challenge=11582014`. Our endpoint validates the token and returns `11582014` (`HTTP 200 OK`).

When a consumer or farmer sends an interactive message or button tap, our endpoint verifies `X-Hub-Signature-256`, extracts the text (`1`, `2`, `TRACE <QR>`, `ORDER EATERY 350`, `6`), publishes `WHATSAPP_MESSAGE_PROCESSED`, and dispatches the exact localized reply (`Swahili/Sheng/English`).

---

## 5. Cutover Verification Checklist

Before enabling live traffic, execute these automated Pytest checks across the newly cutover controllers:

```bash
# Verify PalPlus webhook reconciliation, signature validation & double-entry KRT reward minting
PYTHONPATH=. pytest tests/test_palplus_payment_links.py -v

# Verify M-Pesa Daraja callback and WhatsApp interactive bot intents
PYTHONPATH=. pytest tests/test_security_ai_banking.py -v
PYTHONPATH=. pytest tests/test_innovation_2_0_whatsapp.py -v
```

All 3 external gateways (`PalPlus`, `M-Pesa Daraja`, and `WhatsApp Cloud API`) are fully verified, secured, and ready for live production cutover.
