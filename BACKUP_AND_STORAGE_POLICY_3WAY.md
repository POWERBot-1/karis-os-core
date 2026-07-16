# KARIS OS™ Version 1.0.0-PROD-V1 — 3-Way Encrypted Backup & Cold Storage Policy

**Document Version:** 15.0.0-PROD-V1 (`SRE & Disaster Recovery Track`)  
**Target Audience:** Site Reliability Engineers (`SRE`), Database Administrators & C-Suite Risk Officers (`CRO`)  
**Enforces:** Section 37.5 (`PITR Snapshots`), Section 44.4 (`Cryptographic Checksums`), and 3-Way Storage Mandate

---

## 1. The 3-Way Encrypted Storage Mandate

To guarantee that no ransomware attack, regional data center fire, or local hard drive failure ever compromises the **Universal Double-Entry Ledger (`Rule 9`)** or multi-tenant wallet balances (`Rule 5`), KARIS OS™ enforces a mandatory **3-Way Encrypted Storage Rule**:

Every Point-in-Time Recovery (`PITR`) snapshot (`/backups/PITR-SNAP-*.json`) must be immediately encrypted using `OpenSSL AES-256-GCM` (`or GPG / Age`) and simultaneously synchronized across exactly **3 geographically isolated locations**:

```
+---------------------------------------------------------------------------------------------------+
|               POINT-IN-TIME RECOVERY PITR SNAPSHOT (`/backups/PITR-SNAP-*.json`)                  |
|               Sealed with SHA-256 Checksum & Encrypted via AES-256-GCM (`*.json.enc`)             |
+---------------------------------------------------------------------------------------------------+
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌────────────────────────────────┐  ┌────────────────────────────────┐  ┌────────────────────────────────┐
│ 1. PRIMARY COMPUTER LOCAL DISK │  │ 2. EXTERNAL SSD / HARD DRIVE   │  │ 3. SECURE CLOUD COLD BACKUP    │
│  `~/karis_os_encrypted_backups/`│ │ `/media/usb/karis_os_vault/`   │  │ `s3://karis-os-cold-vault/`    │
│  • Instant SRE local restore   │  │  • Fireproof physical safe     │  │  • KMS envelope encryption     │
│  • Local development fallback  │  │  • Air-gapped offline storage  │  │  • Multi-region bucket replication│
└────────────────────────────────┘  └────────────────────────────────┘  └────────────────────────────────┘
```

---

## 2. Automated 3-Way Encrypted Backup Script (`scripts/automate_3way_encrypted_backup.py`)

Our automated Python backup runner executes all 3 steps cleanly:
1. Calls `DisasterRecoveryEngine.create_point_in_time_snapshot()` to dump exact tables, balances, and SHA-256 audit anchors (`last_hash`).
2. Encrypts the snapshot file to `/backups/PITR-SNAP-*.json.enc` using your `PITR_MASTER_ENCRYPTION_KEY` environment variable.
3. Automatically copies and verifies SHA-256 checksums across:
   * **Location 1 (Primary Computer):** `~/karis_os_encrypted_backups/`
   * **Location 2 (External SSD Safe):** `/media/usb/karis_os_vault_backups/` (`or custom external path`)
   * **Location 3 (Secure Cloud Vault):** `s3://karis-os-cold-vault-africa-nairobi/encrypted/` (`via aws s3 cp --sse aws:kms`)

### **To Execute the 3-Way Backup Right Now:**
```bash
cd /home/user/karis-os-core
export PITR_MASTER_ENCRYPTION_KEY="SuperSecretMasterBackupKey2026_KarisOS_EastAfrica"
PYTHONPATH=. python3 scripts/automate_3way_encrypted_backup.py --dest-local ~/karis_local_backups --dest-ssd /tmp/simulated_external_ssd --dest-cloud /tmp/simulated_cloud_vault
```
