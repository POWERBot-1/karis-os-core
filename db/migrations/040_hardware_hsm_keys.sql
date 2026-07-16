-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 040: Mobile NFC / Biometric Smart Terminal HSM Encryption Keys (Section 41.4 & 38.4)
-- ============================================================================

-- 1. HARDWARE SECURITY MODULE (HSM) MASTER KEYS
CREATE TABLE IF NOT EXISTS hardware_security_module_keys (
    hsm_key_id TEXT PRIMARY KEY,
    key_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'HSM-KEY-MACHAKOS-01'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    device_terminal_code VARCHAR(100) NOT NULL, -- e.g., 'POS-MLO-01', 'SMART-TERMINAL-KAMAU'
    encryption_algorithm VARCHAR(50) NOT NULL DEFAULT 'AES_256_GCM_HARDWARE' CHECK (
        encryption_algorithm IN ('AES_256_GCM_HARDWARE', 'RSA_4096_HSM', 'ECC_SEC P256R1_SECURE_ENCLAVE')
    ),
    public_certificate_pem TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE_SECURE' CHECK (status IN ('ACTIVE_SECURE', 'REVOKED_COMPROMISED', 'ROTATED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. NFC / BIOMETRIC ONE-TIME PAYMENT CRYPTOGRAMS
CREATE TABLE IF NOT EXISTS nfc_biometric_payment_tokens (
    token_id TEXT PRIMARY KEY,
    nfc_cryptogram VARCHAR(255) UNIQUE NOT NULL, -- e.g., 'NFC-TOKEN-2026-89A1B2C3D4'
    identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    wallet_id TEXT NOT NULL REFERENCES wallets(wallet_id),
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    authorized_amount_kes NUMERIC(15, 2) NOT NULL CHECK (authorized_amount_kes > 0),
    biometric_verification_method VARCHAR(50) NOT NULL CHECK (
        biometric_verification_method IN ('FACE_ID_VERIFIED', 'FINGERPRINT_MATCHED', 'BIOMETRIC_PASSKEY')
    ),
    target_terminal_code VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ISSUED_PENDING_SCAN' CHECK (
        status IN ('ISSUED_PENDING_SCAN', 'SCANNED_SETTLED_VIA_LEDGER', 'EXPIRED_TIMEOUT', 'REJECTED_REPLAY_ATTEMPT')
    ),
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    settled_at TIMESTAMP
);

CREATE INDEX idx_hsm_keys_terminal ON hardware_security_module_keys(device_terminal_code, status);
CREATE INDEX idx_nfc_tokens_status_expiry ON nfc_biometric_payment_tokens(nfc_cryptogram, status, expires_at);
