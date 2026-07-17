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
    FX_WALLET = "FX_WALLET"
    USD_WALLET = "USD_WALLET"
    EUR_WALLET = "EUR_WALLET"
    GBP_WALLET = "GBP_WALLET"
    STABLECOIN_WALLET = "STABLECOIN_WALLET"
    REWARDS_WALLET = "REWARDS_WALLET"
    STAKING_POOL = "STAKING_POOL"
    TREASURY_WALLET = "TREASURY_WALLET"
    MERCHANT_WALLET = "MERCHANT_WALLET"
    DRIVER_WALLET = "DRIVER_WALLET"
    ESCROW_WALLET = "ESCROW_WALLET"
    UGX_WALLET = "UGX_WALLET"
    TZS_WALLET = "TZS_WALLET"
    RWF_WALLET = "RWF_WALLET"
    BIF_WALLET = "BIF_WALLET"
    SSP_WALLET = "SSP_WALLET"

class AssetType(str, Enum):
    KES = "KES"
    KRT = "KRT"
    LOYALTY = "LOYALTY"
    CREDIT = "CREDIT"
    INVESTMENT = "INVESTMENT"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    USDT = "USDT"
    USDC = "USDC"
    FX_ASSET = "FX_ASSET"
    STOCKS = "STOCKS"
    COMMODITIES = "COMMODITIES"
    BONDS = "BONDS"
    REWARDS = "REWARDS"
    KRT_REWARDS = "KRT_REWARDS"
    UGX = "UGX"
    TZS = "TZS"
    RWF = "RWF"
    BIF = "BIF"
    SSP = "SSP"

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
    EDUCATION = "EDUCATION"
    FINANCIAL_MARKETS = "FINANCIAL_MARKETS"
    FX_TRADING = "FX_TRADING"
    STAKING = "STAKING"
    REWARDS = "REWARDS"
    GOVERNANCE_VOTING = "GOVERNANCE_VOTING"
    COSMOX_MARKETPLACE = "COSMOX_MARKETPLACE"
    COSMOX_LOGISTICS = "COSMOX_LOGISTICS"
    COSMOX_TOKENOMICS = "COSMOX_TOKENOMICS"
    BORDERX_CUSTOMS = "BORDERX_CUSTOMS"
    BORDERX_LOGISTICS = "BORDERX_LOGISTICS"
    BORDERX_FINANCE = "BORDERX_FINANCE"

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

# --- SECTION 55: KARIS ACADEMY™ EDUCATIONAL ECOSYSTEM MODELS ---
class KarisAcademyInstitutionModel(BaseModel):
    institution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    institution_type: str = "TECHNICAL_UNIVERSITY"
    curriculum_framework: str = "KENYA_CBC_COMPETENCY_BASED"
    admin_identity_id: str
    enrolled_count: int = 1
    tuition_krt_pool: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisAcademyConceptNodeModel(BaseModel):
    concept_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    institution_id: str
    title: str
    category_domain: str = "COMPUTER_SCIENCE_AI"
    prerequisite_concept_ids_json: str = "[]"
    mastery_threshold_pct: float = 85.0
    krt_reward_on_mastery: float = 250.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisAcademyLessonQuizModel(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concept_id: str
    institution_id: str
    creator_identity_id: str
    item_type: str = "LESSON_NOTE_AND_QUIZ"
    title: str
    content_payload_json: str
    version_number: int = 1
    ai_generated_status: str = "DRAFT_PENDING_EDUCATOR_APPROVAL"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisAcademyStudentRecordModel(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_identity_id: str
    institution_id: str
    concept_id: str
    mastery_score_pct: float = 95.0
    completion_status: str = "MASTERY_CERTIFIED"
    krt_edu_reward_earned: float = 250.0
    reconciled_ledger_hash: str = ""
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisAcademyScholarshipModel(BaseModel):
    disbursement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    institution_id: str
    student_identity_id: str
    amount_krt: float
    disbursement_type: str = "LIVING_STIPEND_AND_TUITION"
    reconciled_ledger_hash: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Section 56 / Vertical 21: KARISFX™ Global Financial Ecosystem & KRT Economy Models ---
class KarisFXAccountModel(BaseModel):
    account_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    account_number: str
    account_tier: str = "STANDARD"
    kyc_status: str = "VERIFIED_TIER_3"
    krt_wallet_id: str
    kes_wallet_id: str
    usd_wallet_id: str
    eur_wallet_id: str
    gbp_wallet_id: str
    stablecoin_wallet_id: str
    rewards_wallet_id: str
    treasury_account_ref: str
    reputation_score: int = 100
    mfa_enabled: bool = True
    device_trust_score: float = 99.50
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXTradeOrderModel(BaseModel):
    trade_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    asset_class: str
    symbol: str
    side: str
    order_type: str = "MARKET"
    requested_units: float
    execution_price: float
    total_value_usd: float
    leverage: float = 1.00
    base_fee_krt: float
    fee_discount_pct: float = 0.00
    final_fee_krt: float
    status: str = "EXECUTED_SETTLED"
    ledger_entry_id: str = ""
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXStakingPositionModel(BaseModel):
    staking_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    staking_tier: str
    staked_amount_krt: float
    lockup_duration_days: int
    apy_pct: float
    fee_discount_pct: float
    ai_premium_unlocked: bool = True
    governance_voting_power: float
    status: str = "ACTIVE"
    staked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    unlocks_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXRewardHistoryModel(BaseModel):
    reward_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    activity_type: str
    reward_amount_krt: float
    anti_abuse_status: str = "VERIFIED_CLEAN"
    verification_hash: str
    awarded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXMarketplaceItemModel(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_account_id: str
    item_type: str
    title: str
    description: str
    price_krt: float
    historical_win_rate_pct: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    total_subscribers: int = 0
    status: str = "PUBLISHED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXMarketplacePurchaseModel(BaseModel):
    purchase_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_id: str
    buyer_account_id: str
    price_paid_krt: float
    creator_payout_krt: float
    treasury_fee_krt: float
    ledger_entry_id: str
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXGovernanceProposalModel(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_account_id: str
    category: str
    title: str
    description: str
    ai_impact_summary: str
    status: str = "ACTIVE_VOTING"
    votes_for_krt: float = 0.0000
    votes_against_krt: float = 0.0000
    quorum_required_krt: float = 100000.0000
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    voting_ends_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXGovernanceVoteModel(BaseModel):
    vote_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    voter_account_id: str
    vote_choice: str
    voting_power_krt: float
    voted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXSocialCopyLinkModel(BaseModel):
    copy_link_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    follower_account_id: str
    master_trader_account_id: str
    allocation_krt: float
    copy_ratio: float = 1.00
    max_drawdown_stop_pct: float = 15.00
    total_pnl_krt: float = 0.0000
    status: str = "ACTIVE"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXDeveloperAppModel(BaseModel):
    app_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    developer_account_id: str
    app_name: str
    app_type: str
    api_key_hash: str
    monetization_fee_krt_per_call: float = 1.0000
    total_calls_served: int = 0
    total_krt_earned: float = 0.0000
    status: str = "ACTIVE"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KarisFXComplianceLogModel(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    event_type: str
    transaction_amount_usd: float
    aml_risk_score: float
    jurisdiction_code: str = "KE-EAC"
    cbk_fiu_flagged: bool = False
    audit_notes: str
    logged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Section 57 / Vertical 22: COSMOX™ Universal AI Marketplace & KRT Economy Models ---
class CosmoxAccountModel(BaseModel):
    account_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    account_number: str
    account_type: str = "BUYER"  # BUYER, MERCHANT, DRIVER, DEVELOPER
    kyc_status: str = "VERIFIED_TIER_3"
    fiat_wallet_id: str
    krt_wallet_id: str
    rewards_wallet_id: str
    escrow_wallet_id: str
    merchant_wallet_id: str
    driver_wallet_id: str
    reputation_score: int = 100
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxProductModel(BaseModel):
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_account_id: str
    product_name: str
    category: str = "PHYSICAL_GOODS"
    base_price_krt: float
    base_price_fiat: float
    currency: str = "KES"
    inventory_count: int = 100
    ai_dynamic_pricing_enabled: bool = True
    current_price_krt: float
    status: str = "ACTIVE"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxOrderModel(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    buyer_account_id: str
    seller_account_id: str
    product_id: str
    quantity: int = 1
    unit_price_krt: float
    total_price_krt: float
    seller_payout_krt: float
    platform_commission_krt: float
    cashback_reward_krt: float = 0.0
    payment_method: str = "KRT_WALLET"
    escrow_status: str = "ESCROWED_PENDING_DELIVERY"  # ESCROWED_PENDING_DELIVERY, RELEASED_SETTLED, REFUNDED
    ledger_entry_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxDeliveryModel(BaseModel):
    delivery_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    driver_account_id: str
    origin_address: str
    destination_address: str
    distance_km: float = 5.0
    ai_optimized_route: str
    driver_payout_fiat: float
    driver_bonus_krt: float
    status: str = "ASSIGNED_IN_TRANSIT"  # ASSIGNED_IN_TRANSIT, DELIVERY_CONFIRMED, ESCROW_RELEASED
    escrow_ledger_hash: str = ""
    dispatched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: Optional[datetime] = None

class CosmoxReferralModel(BaseModel):
    referral_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referrer_account_id: str
    referred_account_id: str
    referral_type: str = "INDIVIDUAL"  # INDIVIDUAL, MERCHANT, DELIVERY_PARTNER
    reward_krt: float
    status: str = "PENDING_QUALIFICATION"  # PENDING_QUALIFICATION, REWARDED_CLEAN, BLOCKED
    ledger_entry_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxStakingPositionModel(BaseModel):
    staking_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    staking_tier: str = "SILVER"
    staked_amount_krt: float
    lockup_duration_days: int = 90
    apy_pct: float
    fee_discount_pct: float
    voting_power_krt: float
    status: str = "ACTIVE"
    staked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    unlocks_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxDigitalServiceModel(BaseModel):
    service_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    developer_account_id: str
    title: str
    service_type: str = "AI_TOOL"  # AI_TOOL, SOFTWARE, API, COURSE, DIGITAL_PRODUCT
    api_endpoint_url: str
    price_krt_per_access: float = 10.0
    total_subscribers: int = 0
    total_krt_earned: float = 0.0
    status: str = "PUBLISHED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxVestingScheduleModel(BaseModel):
    vesting_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    beneficiary_account_id: str
    vesting_type: str = "ECOSYSTEM_INCENTIVE_GRANT"
    total_krt_allocated: float
    released_krt: float = 0.0
    duration_months: int = 12
    status: str = "ACTIVE_VESTING"
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_release_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxProposalModel(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_account_id: str
    category: str = "MARKETPLACE_POLICY"
    title: str
    description: str
    ai_impact_summary: str
    status: str = "ACTIVE_VOTING"
    votes_for_krt: float = 0.0
    votes_against_krt: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    voting_ends_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxVoteModel(BaseModel):
    vote_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    voter_account_id: str
    vote_choice: str
    voting_power_krt: float
    voted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CosmoxMultisigRequestModel(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requester_account_id: str
    amount_krt: float
    purpose: str
    ai_risk_score: float = 15.0
    required_approvals: int = 2
    current_approvals: int = 0
    approver_ids_json: str = "[]"
    status: str = "PENDING_MULTISIG"  # PENDING_MULTISIG, APPROVED_DISBURSED, REJECTED
    ledger_entry_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Section 58 / Vertical 23: KARIS BorderX™ East African Customs & Trade Clearing Models ---
class BorderXAccountModel(BaseModel):
    account_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    account_number: str
    entity_type: str = "IMPORTER"  # IMPORTER, EXPORTER, CLEARING_AGENT, TRANSPORTER, FREIGHT_COMPANY, SHIPPING_LINE, CUSTOMS_OFFICER
    kyc_status: str = "VERIFIED_TIER_3"
    kes_wallet_id: str
    ugx_wallet_id: str
    tzs_wallet_id: str
    rwf_wallet_id: str
    bif_wallet_id: str
    ssp_wallet_id: str
    usd_wallet_id: str
    eur_wallet_id: str
    krt_wallet_id: str
    customs_account_ref: str
    reputation_score: int = 100
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BorderXDeclarationModel(BaseModel):
    declaration_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trader_account_id: str
    agent_account_id: str
    declaration_type: str = "IMPORTS"
    origin_country_code: str = "CN"
    destination_country_code: str = "KE"
    border_post_code: str = "BUSIA_EAC"
    hs_code: str
    commodity_description: str
    cif_value_usd: float
    cif_value_kes: float
    total_duty_assessed_kes: float
    total_duty_assessed_krt: float
    customs_risk_score: float = 15.0
    status: str = "DECLARATION_FILED"
    ledger_entry_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BorderXDutyPaymentModel(BaseModel):
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    declaration_id: str
    trader_account_id: str
    import_duty_kes: float = 0.0
    export_duty_kes: float = 0.0
    vat_kes: float = 0.0
    excise_kes: float = 0.0
    railway_levy_kes: float = 0.0
    idf_kes: float = 0.0
    rdl_kes: float = 0.0
    port_charges_kes: float = 0.0
    clearing_fees_kes: float = 0.0
    agent_fees_kes: float = 0.0
    inspection_fees_kes: float = 0.0
    total_amount_kes: float
    total_amount_krt: float
    krt_fee_discount_pct: float = 0.0
    settlement_currency: str = "KRT"
    ledger_entry_id: str
    settled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BorderXShipmentModel(BaseModel):
    shipment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    declaration_id: str
    transporter_account_id: str
    transport_mode: str = "TRUCKS"
    container_number: str
    seal_number: str
    seal_verification_status: str = "SEAL_INTACT_VERIFIED"
    current_border_post: str = "BUSIA_EAC"
    gps_coordinates: str = "0.4608° N, 34.0911° E"
    ai_predicted_waiting_hours: float = 1.5
    congestion_status: str = "MODERATE_CONGESTION"
    ai_recommended_alternate_border: str = "MALABA_EAC"
    status: str = "IN_TRANSIT_TO_BORDER"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BorderXInspectionModel(BaseModel):
    inspection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    declaration_id: str
    customs_officer_account_id: str
    border_post: str
    reason: str
    ai_risk_flag_summary: str
    inspection_status: str = "SCHEDULED_PENDING_INSPECTION"
    officer_notes: str = ""
    scheduled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class BorderXTradeFinanceModel(BaseModel):
    facility_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    borrower_account_id: str
    facility_type: str = "WORKING_CAPITAL"
    principal_amount_usd: float
    principal_amount_krt: float
    interest_rate_pct: float = 8.5
    tenor_days: int = 90
    credit_approval_status: str = "CREDIT_APPROVED"
    disbursement_ledger_id: str = ""
    repayment_ledger_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BorderXMarketplaceListingModel(BaseModel):
    listing_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider_account_id: str
    listing_type: str = "TRUCK_AVAILABLE"
    origin_corridor: str
    destination_corridor: str
    capacity_tons: float = 28.0
    price_krt: float
    status: str = "AVAILABLE"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BorderXWarehouseItemModel(BaseModel):
    warehouse_item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    warehouse_account_id: str
    declaration_id: str
    warehouse_type: str = "BONDED_WAREHOUSE"
    container_number: str
    seal_number: str
    storage_fee_daily_krt: float = 50.0
    release_order_status: str = "BONDED_IN_CUSTODY"
    stored_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    released_at: Optional[datetime] = None

class BorderXDigitalDocumentModel(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    declaration_id: str
    document_type: str
    document_title: str
    payload_json: str
    sha256_verification_hash: str
    digital_signature: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BorderXRiskLogModel(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trader_account_id: str
    declaration_id: str = ""
    fraud_type: str
    detected_value_usd: float = 0.0
    ai_risk_score: float
    status: str = "FLAGGED_HIGH_RISK_BLOCKED"
    audit_notes: str
    logged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BorderXTradeStatisticModel(BaseModel):
    stat_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region_corridor: str = "EAC_NORTHERN_CORRIDOR"
    total_declarations_processed: int = 0
    total_cif_value_usd: float = 0.0
    total_duty_collected_kes: float = 0.0
    total_duty_collected_krt: float = 0.0
    avg_border_waiting_hours: float = 1.85
    top_commodity_hs_code: str = "8517.13.00"
    stat_period_date: str = "2026-07-17"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



