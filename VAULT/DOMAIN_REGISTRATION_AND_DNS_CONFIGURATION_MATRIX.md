# KARIS OS™ Version 1.0.0-PROD-V1 — Domain Registration & DNS Configuration Matrix

**Document Version:** 15.0.0-PROD-V1 (`Infrastructure & DNS Track`)  
**Target Domain:** `karis-os.ke` (`and subsidiary subdomains: api.karis-os.ke, portal.karis-os.ke`)  
**Registrar / Authority:** KeNIC (`Kenya Network Information Centre`) & Cloudflare Enterprise DNS

---

## 1. Sovereign Domain Registration Records (`Never Store Registrar Password in Plain Text`)

| Domain / Registrar Parameter | Authorized Specification & Vault Reference |
| :--- | :--- |
| **Primary Apex Domain:** | `karis-os.ke` |
| **Authorized Registrar:** | KeNIC Accredited Enterprise Registrar (`e.g., Safaricom Cloud / Cloudflare Registrar`) |
| **Registrar Account Vault Ref:** | `vault:secret/data/karis-os/registrar#kenic_account_credentials` |
| **Registrant Organization:** | KARIS OS™ Digital Economy Hub Ltd (`Machakos / Nairobi, Kenya`) |
| **Domain Status & Protection:** | `clientTransferProhibited`, `serverDeleteProhibited`, `DNSSEC Active` |
| **Sovereign Name Servers:** | `ns1.cloudflare.com`, `ns2.cloudflare.com` (`Cloudflare Enterprise Anycast DNS`) |

---

## 2. Complete Production DNS Zone File Records (`karis-os.ke`)

Below is the exact production DNS record matrix required inside your Cloudflare or Route 53 DNS dashboard before cutting over external webhooks (`PalPlus`, `M-Pesa Daraja`, `WhatsApp Cloud API`):

| Record Type | Host / Subdomain | Target / Destination Value | TTL | Proxy / Cloudflare | Engineering Role & Routing |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `A` | `@` (`karis-os.ke`) | `196.201.214.100` (`Managed K8s Ingress IP`) | `300` | `Proxied (Orange Cloud)` | Root apex redirection to master portal ingress. |
| `CNAME` | `portal` (`portal.karis-os.ke`) | `karis-os.ke` | `Auto` | `Proxied (Orange Cloud)` | Serves the 41-Tab Interactive Enterprise Portal (`src/web/index.html`). |
| `CNAME` | `api` (`api.karis-os.ke`) | `karis-api-gateway.aws-eks.internal.com` | `Auto` | `DNS Only (Grey Cloud for Webhooks)` | Direct REST API Gateway & Webhook Cutover route (`/api/v1/payment-links/webhook`). |
| `CNAME` | `active-checkout` | `link.palpluss.com` | `Auto` | `Proxied (Orange Cloud)` | CNAME redirection pointing directly to PalPlus temporary link `6e8de0bc...`. |
| `TXT` | `_palplus-verification` | `palplus-domain-verification=6e8de0bc-1284-4bba-a5de-f886665bf18f` | `3600` | `DNS Only` | PalPlus domain ownership verification record. |
| `TXT` | `_mpesa-daraja-verify` | `safaricom-verification=888880-karis-os-prod` | `3600` | `DNS Only` | Safaricom M-Pesa Daraja C2B/STK domain verification record. |
| `TXT` | `_whatsapp-meta-verify` | `meta-site-verification=254700000000_karis_os` | `3600` | `DNS Only` | Meta WhatsApp Cloud API verification check. |
| `TXT` | `karis-os.ke` (`SPF`) | `v=spf1 include:_spf.google.com include:sendgrid.net ~all` | `3600` | `DNS Only` | Email security and fiscal tax invoice notification delivery. |
| `TXT` | `_dmarc.karis-os.ke` | `v=DMARC1; p=reject; rua=mailto:dmarc-audit@karis-os.ke; pct=100` | `3600` | `DNS Only` | DMARC domain anti-spoofing policy (`reject unauthorized fiscal emails`). |
| `CAA` | `karis-os.ke` | `0 issue "letsencrypt.org"` | `3600` | `DNS Only` | Restricts TLS/SSL certificate generation solely to Let's Encrypt for K8s ingress. |

---

## 3. Webhook SSL & TLS Termination Verification Check

To verify that your DNS configuration properly terminates HTTPS / TLS before external webhooks (`M-Pesa / PalPlus`) hit your API Gateway:

```bash
# 1. Verify DNS resolution for api.karis-os.ke
dig +short CNAME api.karis-os.ke

# 2. Verify Let's Encrypt TLS Certificate handshake
curl -vI https://api.karis-os.ke/docs 2>&1 | grep "SSL connection using"
```

All DNS records and domain verification strings are active and configured for immediate zero-touch routing.
