-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 043: Mobile Super App Passkeys & Push Notification Lifecycle (Section 41.2 & 26.5)
-- ============================================================================

-- 1. FIDO2 / WEBAUTHN MOBILE PASSKEY CREDENTIALS
CREATE TABLE IF NOT EXISTS mobile_passkey_credentials (
    passkey_id TEXT PRIMARY KEY,
    credential_id VARCHAR(255) UNIQUE NOT NULL, -- e.g., 'PASSKEY-CRED-2026-89A1B2C3'
    identity_id TEXT NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    device_platform VARCHAR(50) NOT NULL CHECK (device_platform IN ('IOS_APPLE_SECURE_ENCLAVE', 'ANDROID_KEYSTORE_TEE', 'DESKTOP_BIOMETRIC')),
    public_key_x509_pem TEXT NOT NULL,
    sign_count BIGINT DEFAULT 0 NOT NULL,
    last_verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. APNS / FCM MOBILE PUSH NOTIFICATION DEVICE REGISTRY
CREATE TABLE IF NOT EXISTS mobile_push_notification_devices (
    device_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    push_device_token VARCHAR(255) UNIQUE NOT NULL, -- e.g., 'FCM-TOKEN-KAMAU-01'
    device_platform VARCHAR(50) NOT NULL CHECK (device_platform IN ('ANDROID_FCM', 'IOS_APNS')),
    device_model VARCHAR(100) NOT NULL, -- e.g., 'iPhone 15 Pro', 'Samsung Galaxy S24'
    app_role_active VARCHAR(50) NOT NULL DEFAULT 'CUSTOMER' CHECK (
        app_role_active IN ('CUSTOMER', 'FARMER', 'SUPPLIER', 'RIDER', 'DOCTOR', 'ADMINISTRATOR')
    ),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_mobile_passkeys_identity ON mobile_passkey_credentials(identity_id, device_platform);
CREATE INDEX idx_mobile_push_tokens_role ON mobile_push_notification_devices(identity_id, app_role_active, is_active);
