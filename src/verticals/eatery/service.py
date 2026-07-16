import uuid
from typing import Dict, List, Optional
from src.domain.models import EateryKdsOrderModel, EventCategory, EventPayload
from src.core.event_bus import event_bus

class EateryKdsService:
    """
    KARIS OS™ Eatery & Food Services Service.
    Enforces Section 29 (Eatery & Food Services Vertical).
    Manages Digital Menu, Ingredient Inventory, and Kitchen Display System (KDS) Queue state transitions.
    """
    def __init__(self):
        self.eateries: Dict[str, Dict] = {}
        self.menu_items: Dict[str, Dict] = {}
        self.kds_orders: Dict[str, EateryKdsOrderModel] = {}

    def register_eatery(
        self,
        organization_id: str,
        eatery_name: str,
        business_type: str = "CLOUD_KITCHEN",
        address: str = "Machakos Eatery Hub"
    ) -> Dict:
        eatery = {
            "eatery_id": str(uuid.uuid4()),
            "organization_id": organization_id,
            "eatery_name": eatery_name,
            "business_type": business_type,
            "address": address
        }
        self.eateries[eatery["eatery_id"]] = eatery
        return eatery

    def add_menu_item(
        self,
        eatery_id: str,
        sku: str,
        name: str,
        price_kes: float,
        preparation_time_mins: int = 20
    ) -> Dict:
        item = {
            "item_id": str(uuid.uuid4()),
            "eatery_id": eatery_id,
            "sku": sku,
            "name": name,
            "price_kes": price_kes,
            "preparation_time_mins": preparation_time_mins
        }
        self.menu_items[item["item_id"]] = item
        return item

    def submit_to_kds(
        self,
        eatery_id: str,
        order_id: str,
        table_number: str = "DELIVERY_ORDER"
    ) -> EateryKdsOrderModel:
        kds_order = EateryKdsOrderModel(
            kds_id=str(uuid.uuid4()),
            eatery_id=eatery_id,
            order_id=order_id,
            table_number=table_number,
            preparation_state="PREPARING"
        )
        self.kds_orders[kds_order.kds_id] = kds_order

        ev = EventPayload(
            event_type="EATERY_ORDER_RECEIVED",
            event_category=EventCategory.COMMERCE,
            actor_identity_id="KDS_SYSTEM",
            organization_id=self.eateries.get(eatery_id, {}).get("organization_id", "ORG_DEFAULT"),
            correlation_id=kds_order.kds_id,
            source_module="EATERY_KDS_ENGINE",
            payload=kds_order.model_dump(mode="json")
        )
        event_bus.publish(ev)
        return kds_order

    def flag_meal_ready(self, kds_id: str, chef_identity_id: str) -> EateryKdsOrderModel:
        if kds_id not in self.kds_orders:
            raise KeyError(f"KDS Order ID {kds_id} not found.")

        kds_order = self.kds_orders[kds_id]
        kds_order.preparation_state = "READY_FOR_PICKUP"
        kds_order.chef_identity_id = chef_identity_id

        ev = EventPayload(
            event_type="EATERY_MEAL_READY",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=chef_identity_id,
            organization_id=self.eateries.get(kds_order.eatery_id, {}).get("organization_id", "ORG_DEFAULT"),
            correlation_id=kds_order.kds_id,
            source_module="EATERY_KDS_ENGINE",
            payload=kds_order.model_dump(mode="json")
        )
        event_bus.publish(ev)
        return kds_order

eatery_service = EateryKdsService()
