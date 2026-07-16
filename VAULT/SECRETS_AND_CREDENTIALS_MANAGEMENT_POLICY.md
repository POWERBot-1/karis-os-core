# KARIS OS™ Version 1.0.0-PROD-V1 — Enterprise Configuration Secrets & Credentials Vault Policy

**Document Version:** 15.0.0-PROD-V1 (`Governance & Vault Track`)  
**Target Audience:** DevOps Engineers, Security Officers (`CISO`) & Database Administrators  
**Enforces:** Section 38 (`Enterprise Security & Encryption`) and Section 40 (`Cloud Infrastructure & DevOps`)

---

## 1. Absolute Zero Plain-Text Secrets Mandate

Under **KARIS OS™ Invariant Security Policy (`Section 38.2`)**, **NO configuration secret, API key, database password, or private TLS key shall ever be stored in plain text inside source code repositories, `.env` files committed to Git, or container build layers (`Dockerfile`)**.

All secrets must be dynamically injected at runtime via enterprise secret managers:
* **Production Cloud Kubernetes (`EKS / GKE / AKS`):** HashiCorp Vault, AWS Secrets Manager, or Kubernetes Encrypted Secrets (`ExternalSecrets Operator`).
* **Staging & Local Edge Hubs:** Encrypted 1Password / Bitwarden CLI vaults injected via `op run --env-file=.env.template -- docker-compose up -d`.

---

## 2. Master Secrets Vault Mapping Template (`NEVER COMMIT REAL VALUES TO GIT`)

Below is the exact enterprise schema structure required inside your secrets vault (`HashiCorp Vault path: secret/data/karis-os/production`):

```json
{
  "PLATFORM_METADATA": {
    "PLATFORM_NAME": "KARIS OS™",
    "PLATFORM_VERSION": "1.0.0-PROD-V1",
    "DEFAULT_CURRENCY": "KES",
    "DEFAULT_COUNTRY": "KE"
  },
  "DATABASE_CREDENTIALS": {
    "POSTGRES_DB": "karis_os_prod",
    "POSTGRES_USER": "karis_admin",
    "POSTGRES_PASSWORD_ENCRYPTED_VAULT_REF": "vault:secret/data/karis-os/db#password",
    "DATABASE_URL_VAULT_REF": "postgresql://karis_admin:${POSTGRES_PASSWORD}@rds-cluster.aws.internal:5432/karis_os_prod",
    "REDIS_URL_VAULT_REF": "redis://elasticache.aws.internal:6379/0"
  },
  "CRYPTOGRAPHIC_AUTH_AND_HSM_KEYS": {
    "JWT_SECRET_KEY_VAULT_REF": "vault:secret/data/karis-os/auth#jwt_secret",
    "HSM_MASTER_KEY_AES_256_GCM": "vault:secret/data/karis-os/hsm#master_key",
    "FIDO2_RP_ID": "portal.karis-os.ke"
  },
  "EXTERNAL_PAYMENT_AND_MESSAGING_GATEWAYS": {
    "PALPLUS_PAYMENT_LINK_ID": "6e8de0bc-1284-4bba-a5de-f886665bf18f",
    "PALPLUS_WEBHOOK_SECRET_VAULT_REF": "vault:secret/data/karis-os/palplus#webhook_secret",
    "MPESA_CONSUMER_KEY_VAULT_REF": "vault:secret/data/karis-os/mpesa#consumer_key",
    "MPESA_CONSUMER_SECRET_VAULT_REF": "vault:secret/data/karis-os/mpesa#consumer_secret",
    "MPESA_SHORTCODE_PAYBILL": "888880",
    "WHATSAPP_APP_SECRET_VAULT_REF": "vault:secret/data/karis-os/whatsapp#app_secret",
    "WHATSAPP_VERIFY_TOKEN": "karis_wa_verify_token_2026"
  },
  "REGULATORY_AND_TAX_STAMP_CREDENTIALS": {
    "KRA_ETIMS_CERTIFICATE_PEM_VAULT_REF": "vault:secret/data/karis-os/kra#etims_cert_pem",
    "CBK_AML_FIU_TRANSMISSION_KEY_REF": "vault:secret/data/karis-os/cbk#fiu_transmission_key"
  }
}
```

---

## 3. Runtime Injection Protocol for Kubernetes (`ExternalSecrets Manifest`)

When deploying via `k8s/deployment.yaml`, attach this `ExternalSecret` manifest to pull secrets directly from AWS Secrets Manager or HashiCorp Vault into memory without writing to disk:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: karis-os-vault-secrets
  namespace: karis-os-prod
spec:
  refreshInterval: "1h"
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: karis-os-secrets
    creationPolicy: Owner
  data:
  - secretKey: DATABASE_URL
    remoteRef:
      key: karis-os/production
      property: DATABASE_URL
  - secretKey: JWT_SECRET_KEY
    remoteRef:
      key: karis-os/production
      property: JWT_SECRET_KEY
  - secretKey: PALPLUS_WEBHOOK_SECRET
    remoteRef:
      key: karis-os/production
      property: PALPLUS_WEBHOOK_SECRET
  - secretKey: MPESA_CONSUMER_SECRET
    remoteRef:
      key: karis-os/production
      property: MPESA_CONSUMER_SECRET
```

This ensures zero plain-text credential exposure across the entire lifecycle of your platform!
