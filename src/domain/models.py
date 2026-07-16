import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# --- Enums ---
class IdentityType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS = "BUSINESS"
    COOPERATIVE = "COOPERATIVE"
    AI_AGENT = "AI_AGENT"
    PLATFORM_ADMINISTRATOR = "PLATFORM_ADMINISTRATOR"

class WalletType(str, Enum):
    KES_WALLET = "KES_WALLET"
    KRT_WALLET = "KRT_WALLET"
    CREDIT_WALLET = "CREDIT_WALLET"
    LOYALTY_WALLET = "LOYALTY_WALLET"
    INVESTMENT_WALLET = "INVESTMENT_WALLET"
    SETTLEMENT_WALLET = "SETTLEMENT_WALLET"
    RESERVE_WALLET = "RESERVE_WALLET"
    REWARD_POOL = "REWARD_POOL"

class AssetType(str, Enum):
    KES = "KES"
    KRT = "KRT"
    LOYALTY = "LOYALTY"
    CREDIT = "CREDIT"
    INVESTMENT = "INVESTMENT"

class EventCategory(str, Enum):
    IDENTITY = "IDENTITY"
    COMMERCE = "COMMERCE"
    PAYMENT = "PAYMENT"
    WALLET = "WALLET"
    CURRENCY = "CURRENCY"
    DELIVERY = "DELIVERY"
    AGRICULTURE = "AGRICULTURE"
    TREASURY = "TREASURY"
    HEALTHCARE = "HEALTHCARE"
    MOBILITY = "MOBILITY"
    GOVERNANCE = "GOVERNANCE"
    POWER_BOT_X = "POWER_BOT_X"
    PREDICTION = "PREDICTION"
    ENERGY = "ENERGY"
    PHARMA = "PHARMA"
    PROP_SHARE = "PROP_SHARE"
    EDU_PAY = "EDU_PAY"
    SOCIAL = "SOCIAL"

class OrderStatus(str, Enum):
    ORDER_CREATED = "ORDER_CREATED"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    STOCK_RESERVED = "STOCK_RESERVED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"

# --- Domain Models ---
class IdentityModel(BaseModel):
    identity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_type: IdentityType
    global_identifier: str
    full_name: str
    phone_number: str
    verification_status: str = "VERIFIED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrganizationModel(BaseModel):
    organization_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    code: str
    vertical_type: str
    currency: str = "KES"
    status: str = "ACTIVE"

class WalletModel(BaseModel):
    wallet_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    organization_id: str
    wallet_type: WalletType
    asset_type: AssetType
    balance: float = 0.0
    locked_balance: float = 0.0
    status: str = "ACTIVE"

class EventPayload(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_category: EventCategory
    actor_identity_id: str
    organization_id: str
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_module: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cryptographic_hash: Optional[str] = None

class LedgerEntryModel(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str
    asset_type: AssetType
    debit_wallet_id: str
    credit_wallet_id: str
    amount: float
    currency: str
    organization_id: str
    event_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    audit_hash: str

class OrderItemModel(BaseModel):
    product_id: str
    sku: str
    quantity: float
    unit_price: float
    total_price: float

class OrderModel(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str
    organization_id: str
    customer_identity_id: str
    supplier_identity_id: str
    order_status: OrderStatus = OrderStatus.ORDER_CREATED
    delivery_method: str = "DELIVERY_RIDER"
    total_kes_amount: float
    paid_kes_amount: float = 0.0
    paid_krt_amount: float = 0.0
    items: List[OrderItemModel]
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ProduceBatchModel(BaseModel):
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    organization_id: str
    supplier_identity_id: str
    batch_number: str
    quantity_available: float
    unit_cost: float
    quality_grade: str = "GRADE_A"
    traceability_qr_code: str

# --- Expanded Vertical & Engine Models ---
class LogisticsDispatchModel(BaseModel):
    dispatch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    order_id: str
    rider_identity_id: Optional[str] = None
    pickup_address: str
    dropoff_address: str
    distance_km: float
    delivery_fee_kes: float
    escrow_payout_kes: float
    dispatch_status: str = "ORDER_READY"
    ai_dispatch_score: Optional[float] = None

class EateryKdsOrderModel(BaseModel):
    kds_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eatery_id: str
    order_id: str
    table_number: str = "TAKEAWAY"
    preparation_state: str = "RECEIVED"
    chef_identity_id: Optional[str] = None
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RetailPosSessionModel(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    terminal_code: str
    cashier_identity_id: str
    opening_cash_kes: float
    status: str = "OPEN"

class HealthcareAppointmentModel(BaseModel):
    appointment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_id: str
    patient_id: str
    doctor_identity_id: str
    appointment_type: str = "TELEMEDICINE"
    scheduled_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "APPOINTMENT_BOOKED"
    consultation_fee_kes: float

class HealthcarePrescriptionModel(BaseModel):
    prescription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    emr_note_id: str
    patient_id: str
    doctor_identity_id: str
    medication_product_id: str
    quantity_prescribed: float
    status: str = "ISSUED"

class MobilityTripModel(BaseModel):
    trip_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trip_code: str
    organization_id: str
    passenger_identity_id: str
    driver_id: Optional[str] = None
    pickup_location_text: str
    dropoff_location_text: str
    estimated_distance_km: float
    total_fare_kes: float
    driver_payout_kes: float
    trip_status: str = "RIDE_REQUESTED"

class InvestmentPoolModel(BaseModel):
    pool_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pool_code: str
    pool_name: str
    pool_category: str
    target_capital_kes: float
    total_capital_raised_kes: float = 0.0
    expected_annual_roi_pct: float
    status: str = "OPEN_FOR_INVESTMENT"

class AIRiskEvaluationModel(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_identity_id: str
    context_type: str  # e.g., 'CREDIT_APPLICATION', 'TRANSACTION_MONITORING', 'DISPATCH_OPTIMIZATION'
    risk_score: float  # 0.0 to 100.0 (lower is safer)
    confidence_pct: float
    recommendation: str  # e.g., 'APPROVE', 'REJECT', 'ESCALATE_TO_HUMAN'
    ai_model_version: str = "KARIS-AI-RISK-V2.4"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- POWER BOT X: Autonomous AI Prediction Economy Models ---
class PowerBotFixtureModel(BaseModel):
    fixture_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    category: str
    start_time_utc: datetime
    status: str = "UPCOMING"
    odds_or_confidence: Optional[str] = None
    form_analysis_json: Optional[str] = None
    settlement_outcome: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PowerBotPredictionModel(BaseModel):
    prediction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    fixture_id: str
    predicted_outcome: str
    stake_krt: float
    status: str = "PENDING_SETTLEMENT"
    potential_payout_krt: float
    actual_payout_krt: float = 0.0
    reputation_earned: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PowerBotLeagueModel(BaseModel):
    league_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    league_type: str = "PRIVATE"
    county: Optional[str] = None
    creator_user_id: str
    member_count: int = 1
    prize_pool_krt: float = 0.0
    status: str = "ACTIVE"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PowerBotLeagueMemberModel(BaseModel):
    membership_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    league_id: str
    user_id: str
    reputation_score: int = 100
    total_predictions: int = 0
    win_rate: float = 0.0
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PowerBotReputationProfileModel(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    fair_participation_score: int = 100
    account_longevity_days: int = 1
    verified_identity_bonus: int = 50
    community_engagement_score: int = 50
    referral_count: int = 0
    merchant_activity_score: int = 0
    total_reputation_points: int = 200
    tier: str = "SCOUT"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PowerBotAgentCampaignModel(BaseModel):
    campaign_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_user_id: str
    content_type: str
    target_channel: str = "WHATSAPP_STATUS"
    local_language: str = "EN_SWAHILI_SHENG"
    media_payload_json: str
    predicted_conversion_rate: float = 15.5
    actual_conversions: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PowerBotDigitalTwinSnapshotModel(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    treasury_health_score: float = 98.5
    krt_circulation_total: float = 0.0
    active_predictions_count: int = 0
    agent_network_size: int = 0
    merchant_krt_velocity: float = 0.0
    fraud_alert_level: str = "NORMAL"
    policy_simulation_parameters_json: Optional[str] = None
    ai_policy_recommendations_json: Optional[str] = None
    admin_approval_status: str = "PENDING_RBAC_APPROVAL"

# --- VERTICAL 15: KARIS ENERGY & SMART SOLAR GRID™ (Section 50) Models ---
class EnergySolarInstallationModel(BaseModel):
    installation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_user_id: str
    organization_id: str
    device_serial_number: str
    device_type: str = "SOLAR_IRRIGATION_PUMP"
    gps_location: str = "(-1.3850, 36.9400)"
    rated_capacity_watts: float = 1500.0
    payg_status: str = "ACTIVE_UNLOCKED"
    daily_token_rate_krt: float = 50.0
    battery_charge_pct: float = 100.0
    total_kwh_generated: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnergySmartMeterTelemetryModel(BaseModel):
    telemetry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    installation_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    kwh_generated_today: float = 0.0
    kwh_consumed_today: float = 0.0
    battery_voltage_v: float = 24.5
    soil_moisture_pct: float = 45.0
    microgrid_feed_in_kwh: float = 0.0
    status: str = "NORMAL"

class EnergyPAYGInstallmentModel(BaseModel):
    installment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    installation_id: str
    payer_user_id: str
    amount_krt: float = 0.0
    amount_kes: float = 0.0
    payment_method: str = "KRT_WALLET"
    days_unlocked: int = 1
    status: str = "SETTLED_UNLOCKED"
    settled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnergyMicrogridPeerTransferModel(BaseModel):
    transfer_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_user_id: str
    buyer_user_id: str
    kwh_traded: float
    price_per_kwh_krt: float = 12.5
    total_amount_krt: float
    audit_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- SECTION 51: PALPLUS & HOSTED PAYMENT LINKS MODELS ---
class HostedPaymentLinkModel(BaseModel):
    payment_link_id: str = "6e8de0bc-1284-4bba-a5de-f886665bf18f"
    provider: str = "PALPLUS"
    external_link_url: str = "https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f"
    merchant_organization_id: str = "ORG-KARIS-RETAIL"
    created_by_identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    target_order_id: Optional[str] = None
    amount_kes: float = 0.0
    status: str = "ACTIVE_TEMPORARY_LINK"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class PaymentLinkTransactionModel(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payment_link_id: str = "6e8de0bc-1284-4bba-a5de-f886665bf18f"
    payer_identity_id: str
    amount_kes: float
    payment_method: str = "PALPLUS_MPESA_EXPRESS"
    external_receipt_number: str
    reconciled_ledger_hash: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- SECTION 52: PHARMA-TRACE, PROP-SHARE & EDU-PAY MODELS ---
class PharmaColdChainBatchModel(BaseModel):
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    organization_id: str
    batch_number: str
    qr_traceability_code: str
    storage_min_celsius: float = 2.0
    storage_max_celsius: float = 8.0
    current_temperature_celsius: float = 4.5
    status: str = "SAFE_COLD_CHAIN"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PharmaTemperatureTelemetryModel(BaseModel):
    telemetry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    batch_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    temperature_celsius: float
    humidity_pct: float = 55.0
    gps_location: str = "(-1.3850, 36.9400)"
    status: str = "NORMAL"

class PropShareSyndicationModel(BaseModel):
    syndication_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    property_title: str
    location_county: str = "Machakos County"
    total_shares: int
    share_price_kes: float
    monthly_rental_income_kes: float = 0.0
    status: str = "OPEN_FOR_ALLOCATION"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PropShareAllocationModel(BaseModel):
    allocation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    syndication_id: str
    investor_identity_id: str
    shares_owned: int = 0
    total_invested_kes: float = 0.0
    total_dividends_earned_kes: float = 0.0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EduPayTuitionPlanModel(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_identity_id: str
    institution_organization_id: str
    academic_term: str
    total_tuition_kes: float
    paid_amount_kes: float = 0.0
    remaining_balance_kes: float = 0.0
    status: str = "ACTIVE_INSTALLMENTS"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EduPayTuitionInstallmentModel(BaseModel):
    installment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_id: str
    payer_identity_id: str
    amount_kes: float
    payment_method: str = "MPESA_EXPRESS_PALPLUS"
    external_reference: str
    reconciled_ledger_hash: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- SECTION 54: KARIS LOOP™ SOCIAL INTELLIGENCE MODELS ---
class KarisLoopProfileModel(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_identity_id: str
    organization_id: str
    handle_username: str
    display_name: str
    account_type: str = "CREATOR_USER"
    verified_status: str = "VERIFIED_KYC_TIER_3"
    creator_tier: str = "RISING_CREATOR"
    reputation_score: int = 150
    total_krt_tips_received: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisLoopCommunityModel(BaseModel):
    community_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    community_type: str = "REGIONAL_AGRI_GUILD"
    region_county: str = "Machakos County"
    creator_identity_id: str
    member_count: int = 1
    treasury_krt_pool: float = 0.0
    moderation_mode: str = "AI_ASSISTED_HUMAN_REVIEW"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisLoopPostModel(BaseModel):
    post_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_identity_id: str
    community_id: str
    content_type: str = "SHORT_VIDEO"
    feed_category: str = "FOR_YOU_TRENDING"
    caption_text: str
    media_payload_json: str
    linked_product_id: Optional[str] = None
    shoppable_price_kes: float = 0.0
    likes_count: int = 0
    tips_krt_total: float = 0.0
    ai_moderation_status: str = "APPROVED_CLEAN"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisLoopTipTransactionModel(BaseModel):
    tip_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    tipper_identity_id: str
    creator_identity_id: str
    amount_krt: float
    transaction_type: str = "CREATOR_TIP_KRT"
    reconciled_ledger_hash: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisLoopMessageModel(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_identity_id: str
    receiver_identity_or_group_id: str
    chat_type: str = "DIRECT_MESSAGE"
    message_body: str
    ai_translated_text: Optional[str] = None
    status: str = "DELIVERED"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



