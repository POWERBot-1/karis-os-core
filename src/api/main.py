import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from src.config import config
from src.domain.models import (
    AssetType,
    EventCategory,
    EventPayload,
    IdentityModel,
    IdentityType,
    LedgerEntryModel,
    OrderItemModel,
    OrderModel,
    OrderStatus,
    ProduceBatchModel,
    WalletModel,
    WalletType,
)
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.core.rule_engine import rule_engine  # Ensure Rule Engine is booted
from src.core.treasury_engine import treasury_engine
from src.verticals.karis_farm.service import karis_farm_service

# Import modular routers
from src.security.gateway_middleware import EnterpriseSecurityMiddleware
from src.api.routers import (
    logistics,
    eatery,
    retail_pos,
    healthcare,
    mobility,
    finance,
    ai_agents,
    exchange,
    simulators,
    admin,
    auth,
    ai_rag,
    financial,
    audit,
    sales_force,
    loyalty,
    workflows,
    verticals,
    innovation_2_0,
    whatsapp,
    cqrs,
    governance,
    predictive,
    dlq,
    observability,
    disaster_recovery,
    emergency_ambulance,
    pos_ai,
    erp_sync,
    crm_ai,
    future_industries,
    fraud_ai,
    sla,
    omnichannel,
    insurance_iot,
    policy_keys,
    privacy_gdpr,
    chaos,
    warehouse_route,
    sdk_bi_cicd,
    offline_sync,
    marketplace,
    regulatory,
    hardware_hsm,
    loyalty_tier,
    ha_failover,
    mobile_passkey,
    ledger_recon,
    k8s_autoscale,
    escrow_dispute,
    supply_bottleneck,
    tax_holiday,
    power_bot_x,
    energy_grid,
    payment_link,
    expansion_suite,
    whitelabel,
    karis_loop,
    karis_academy,
    karisfx,
    cosmox,
    borderx,
)

app = FastAPI(
    title=f"{config.PLATFORM_NAME} Enterprise API Gateway & Portal",
    version=config.PLATFORM_VERSION,
    description="Unified Enterprise & Digital Economy Platform API Gateway. Enforces Section 1 to Section 58 & Rules 1 to 10 strictly including Karis Academy, KARISFX Global Financial Ecosystem, COSMOX AI Universal Marketplace, and KARIS BorderX East African Customs & Border Trade Clearing Engine."
)

# Attach rate-limiting, CORS, correlation ID, and security headers middleware
app.add_middleware(EnterpriseSecurityMiddleware)

# Register modular routers
app.include_router(simulators.router)
app.include_router(observability.router)
app.include_router(disaster_recovery.router)
app.include_router(emergency_ambulance.router)
app.include_router(pos_ai.router)
app.include_router(erp_sync.router)
app.include_router(crm_ai.router)
app.include_router(future_industries.router)
app.include_router(fraud_ai.router)
app.include_router(sla.router)
app.include_router(omnichannel.router)
app.include_router(insurance_iot.router)
app.include_router(policy_keys.router)
app.include_router(privacy_gdpr.router)
app.include_router(chaos.router)
app.include_router(warehouse_route.router)
app.include_router(sdk_bi_cicd.router)
app.include_router(offline_sync.router)
app.include_router(marketplace.router)
app.include_router(regulatory.router)
app.include_router(hardware_hsm.router)
app.include_router(loyalty_tier.router)
app.include_router(ha_failover.router)
app.include_router(mobile_passkey.router)
app.include_router(ledger_recon.router)
app.include_router(k8s_autoscale.router)
app.include_router(escrow_dispute.router)
app.include_router(supply_bottleneck.router)
app.include_router(tax_holiday.router)
app.include_router(power_bot_x.router)
app.include_router(energy_grid.router)
app.include_router(payment_link.router)
app.include_router(expansion_suite.router)
app.include_router(whitelabel.router)
app.include_router(karis_loop.router)
app.include_router(karis_academy.router)
app.include_router(karisfx.router)
app.include_router(cosmox.router)
app.include_router(borderx.router)
app.include_router(auth.router)
app.include_router(audit.router)
app.include_router(ai_rag.router)
app.include_router(financial.router)
app.include_router(admin.router)
app.include_router(workflows.router)
app.include_router(verticals.router)
app.include_router(sales_force.router)
app.include_router(loyalty.router)
app.include_router(innovation_2_0.router)
app.include_router(whatsapp.router)
app.include_router(cqrs.router)
app.include_router(governance.router)
app.include_router(predictive.router)
app.include_router(dlq.router)
app.include_router(logistics.router)
app.include_router(eatery.router)
app.include_router(retail_pos.router)
app.include_router(healthcare.router)
app.include_router(mobility.router)
app.include_router(finance.router)
app.include_router(ai_agents.router)
app.include_router(exchange.router)

# In-memory identity registry for API demonstration
identities_db: Dict[str, IdentityModel] = {}
orders_db: Dict[str, OrderModel] = {}

# --- Request/Response Schemas ---
class CreateIdentityRequest(BaseModel):
    identity_type: IdentityType
    global_identifier: str
    full_name: str
    phone_number: str

class CreateWalletRequest(BaseModel):
    identity_id: str
    organization_id: str
    wallet_type: WalletType
    asset_type: AssetType
    initial_balance: float = 0.0

class CreateOrderRequest(BaseModel):
    organization_id: str
    customer_identity_id: str
    supplier_identity_id: str
    items: List[OrderItemModel]

class ConfirmPaymentRequest(BaseModel):
    order_id: str
    payer_identity_id: str
    payment_method: str = "M_PESA"
    external_reference: str = "QG37XXXXXXXX"
    amount_kes: float

class RegisterFarmRequest(BaseModel):
    farmer_identity_id: str
    organization_id: str
    farm_name: str
    region_county: str
    total_acreage: float
    cooperative_identity_id: Optional[str] = None

class LogHarvestRequest(BaseModel):
    farm_id: str
    crop_type: str
    quantity_kg: float
    quality_grade: str = "GRADE_A"
    unit_cost_kes: float

# --- Core Endpoints ---
@app.post("/api/v1/identities", response_model=IdentityModel, status_code=status.HTTP_201_CREATED)
def create_identity(req: CreateIdentityRequest):
    identity = IdentityModel(
        identity_type=req.identity_type,
        global_identifier=req.global_identifier,
        full_name=req.full_name,
        phone_number=req.phone_number
    )
    identities_db[identity.identity_id] = identity

    event = EventPayload(
        event_type="USER_CREATED",
        event_category=EventCategory.IDENTITY,
        actor_identity_id=identity.identity_id,
        organization_id="SYSTEM_CORE",
        correlation_id=identity.identity_id,
        source_module="API_GATEWAY",
        payload=identity.model_dump(mode="json")
    )
    event_bus.publish(event)
    return identity

@app.post("/api/v1/wallets", response_model=WalletModel, status_code=status.HTTP_201_CREATED)
def create_wallet(req: CreateWalletRequest):
    return wallet_engine.create_wallet(
        identity_id=req.identity_id,
        organization_id=req.organization_id,
        wallet_type=req.wallet_type,
        asset_type=req.asset_type,
        initial_balance=req.initial_balance
    )

@app.get("/api/v1/wallets/{wallet_id}", response_model=WalletModel)
def get_wallet(wallet_id: str):
    wallet = wallet_engine.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@app.post("/api/v1/orders", response_model=OrderModel, status_code=status.HTTP_201_CREATED)
def create_order(req: CreateOrderRequest):
    total_kes = sum(item.total_price for item in req.items)
    order = OrderModel(
        order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
        organization_id=req.organization_id,
        customer_identity_id=req.customer_identity_id,
        supplier_identity_id=req.supplier_identity_id,
        total_kes_amount=total_kes,
        items=req.items
    )
    orders_db[order.order_id] = order

    event = EventPayload(
        event_type="COMMERCE_ORDER_CREATED",
        event_category=EventCategory.COMMERCE,
        actor_identity_id=req.customer_identity_id,
        organization_id=req.organization_id,
        correlation_id=order.correlation_id,
        source_module="COMMERCE_ENGINE",
        payload=order.model_dump(mode="json")
    )
    event_bus.publish(event)
    return order

@app.post("/api/v1/payments", status_code=status.HTTP_200_OK)
def confirm_payment(req: ConfirmPaymentRequest):
    if req.order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[req.order_id]
    order.paid_kes_amount += req.amount_kes
    if order.paid_kes_amount >= order.total_kes_amount:
        order.order_status = OrderStatus.PAYMENT_CONFIRMED

    event = EventPayload(
        event_type="PAYMENT_CONFIRMED",
        event_category=EventCategory.PAYMENT,
        actor_identity_id=req.payer_identity_id,
        organization_id=order.organization_id,
        correlation_id=order.correlation_id,
        source_module="PAYMENT_ENGINE",
        payload={
            "payment_id": str(uuid.uuid4()),
            "order_id": order.order_id,
            "payer_identity_id": req.payer_identity_id,
            "supplier_identity_id": order.supplier_identity_id,
            "payment_method": req.payment_method,
            "external_reference": req.external_reference,
            "amount_kes": req.amount_kes,
            "status": "PAYMENT_CONFIRMED"
        }
    )
    event_bus.publish(event)
    return {"status": "SUCCESS", "message": "Payment confirmed and settlement dispatched to Universal Ledger."}

@app.post("/api/v1/farm/register", status_code=status.HTTP_201_CREATED)
def register_farm(req: RegisterFarmRequest):
    return karis_farm_service.register_farm(
        farmer_identity_id=req.farmer_identity_id,
        organization_id=req.organization_id,
        farm_name=req.farm_name,
        region_county=req.region_county,
        total_acreage=req.total_acreage,
        cooperative_identity_id=req.cooperative_identity_id
    )

@app.post("/api/v1/farm/harvest", response_model=ProduceBatchModel, status_code=status.HTTP_201_CREATED)
def log_harvest(req: LogHarvestRequest):
    try:
        return karis_farm_service.log_harvest(
            farm_id=req.farm_id,
            crop_type=req.crop_type,
            quantity_kg=req.quantity_kg,
            quality_grade=req.quality_grade,
            unit_cost_kes=req.unit_cost_kes
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/v1/farm/traceability/{qr_code}")
def get_traceability(qr_code: str):
    record = karis_farm_service.get_traceability_by_qr(qr_code)
    if not record:
        raise HTTPException(status_code=404, detail="Traceability record not found for this QR code")
    return record

@app.get("/api/v1/treasury/health/{organization_id}")
def get_treasury_health(organization_id: str):
    return treasury_engine.get_treasury_health(organization_id)

@app.get("/api/v1/ledger/entries", response_model=List[LedgerEntryModel])
def get_ledger_entries():
    return ledger_engine.get_entries()

@app.get("/api/v1/events", response_model=List[EventPayload])
def get_event_store():
    return event_bus.get_event_store()
