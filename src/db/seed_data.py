#!/usr/bin/env python3
"""
KARIS OS™ Production Database Seeding Engine.
Populates realistic East African (Machakos / Mlolongo / Nairobi) organizations, identities,
multi-asset wallets, flagship KARIS FARM traceability batches, and declarative business rules.
Run: python3 -m src.db.seed_data --seed
"""

import sys
import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from src.db.database import engine
from src.domain.models import AssetType, WalletType
from src.core.wallet_engine import wallet_engine
from src.verticals.karis_farm.service import karis_farm_service
from src.verticals.retail_pos.service import retail_pos_service
from src.verticals.eatery.service import eatery_service
from src.verticals.logistics.service import logistics_service
from src.verticals.healthcare.service import healthcare_service
from src.verticals.mobility.service import mobility_service
from src.verticals.finance_invest.service import finance_investment_service

def seed_database():
    print("=" * 80)
    print("      KARIS OS™ PRODUCTION DATABASE SEEDING ENGINE")
    print("      Seeding East African Multi-Tenant Ecosystem & Flagship KARIS FARM™")
    print("=" * 80)

    with engine.connect() as conn:
        # Check if already seeded
        res = conn.execute(text("SELECT COUNT(*) FROM identities;")).scalar()
        if res and res > 0:
            print("  [NOTE] Database already contains identity records. Clearing before fresh seed...")
            # For clean simulation seeding, clear transactional records if needed or append safely
            conn.execute(text("DELETE FROM identities;"))
            conn.execute(text("DELETE FROM organizations;"))
            conn.commit()

        print("  [1/7] Seeding Global Identities (Section 7: Single Identity Principle)...")
        identities = [
            ("268e1e85-a0b3-445d-827b-98e327af3bee", "INDIVIDUAL", "ID-KE-28491029", "John Kamau (Machakos Farmer)", "+254711000001", "john.kamau@karis.ke"),
            ("8b6ff564-ce30-489e-8a02-75004ccd5516", "COOPERATIVE", "COOP-KE-MACHAKOS-01", "Machakos Farmers Cooperative", "+254711000002", "info@machakoscoop.ke"),
            ("7f8013a9-310c-4f16-9031-295274a26944", "INDIVIDUAL", "ID-KE-31920192", "Amina Wanjiku (Supermarket Customer)", "+254711000003", "amina.w@gmail.com"),
            ("da11cf88-5121-49b0-9a3b-28f0d8a11a2b", "INDIVIDUAL", "ID-KE-RIDER-01", "David Ochieng (Logistics Rider & Driver)", "+254711000004", "david.o@karislogistics.ke"),
            ("6d17b5bc-b136-43ad-87c8-90e28717dc44", "INDIVIDUAL", "ID-KE-DOC-01", "Dr. Omondi (Machakos County Specialist)", "+254711000005", "omondi@machakoshealth.ke"),
            ("11111111-1111-1111-1111-111111111111", "PLATFORM_ADMINISTRATOR", "ID-KE-ADMIN-01", "KARIS Platform Administrator", "+254700000000", "admin@karis-os.ke")
        ]
        for id_id, i_type, g_id, name, phone, email in identities:
            conn.execute(text("""
                INSERT INTO identities (identity_id, identity_type, global_identifier, full_name, phone_number, email, verification_status)
                VALUES (:id_id, :i_type, :g_id, :name, :phone, :email, 'VERIFIED')
            """), {"id_id": id_id, "i_type": i_type, "g_id": g_id, "name": name, "phone": phone, "email": email})
        conn.commit()
        print("    ✔ Seeded 6 Global Identities.")

        print("  [2/7] Seeding Multi-Tenant Organizations (Section 7.3)...")
        organizations = [
            ("a0000000-0000-0000-0000-000000000001", "KARIS FARM™ Machakos Hub", "ORG-KARIS-FARM", "AGRICULTURE", "P051234567A"),
            ("b0000000-0000-0000-0000-000000000002", "KARIS Supermarket Mlolongo", "ORG-KARIS-RETAIL", "RETAIL", "P051234567B"),
            ("c0000000-0000-0000-0000-000000000003", "Machakos Cloud Kitchen & Eatery", "ORG-KARIS-EATERY", "FOOD_SERVICES", "P051234567C"),
            ("d0000000-0000-0000-0000-000000000004", "Machakos County Medical Hub", "ORG-KARIS-HEALTH", "HEALTHCARE", "P051234567D"),
            ("e0000000-0000-0000-0000-000000000005", "KARIS Mobility & Logistics Fleet", "ORG-KARIS-MOBILITY", "LOGISTICS", "P051234567E")
        ]
        for o_id, name, code, v_type, tax in organizations:
            conn.execute(text("""
                INSERT INTO organizations (organization_id, name, code, vertical_type, tax_identifier, country_code, currency, status)
                VALUES (:o_id, :name, :code, :v_type, :tax, 'KE', 'KES', 'ACTIVE')
            """), {"o_id": o_id, "name": name, "code": code, "v_type": v_type, "tax": tax})
        conn.commit()
        print("    ✔ Seeded 5 Multi-Tenant Organizations across 5 enterprise verticals.")

        print("  [3/7] Seeding Multi-Asset Wallets & Treasury Reserves (Section 5 & 12)...")
        # Customer Wallets
        wallet_engine.create_wallet("7f8013a9-310c-4f16-9031-295274a26944", "ORG-KARIS-RETAIL", WalletType.KES_WALLET, AssetType.KES, 100000.0)
        wallet_engine.create_wallet("7f8013a9-310c-4f16-9031-295274a26944", "ORG-KARIS-RETAIL", WalletType.KRT_WALLET, AssetType.KRT, 1000.0)
        # Farmer Wallets
        wallet_engine.create_wallet("268e1e85-a0b3-445d-827b-98e327af3bee", "ORG-KARIS-FARM", WalletType.KES_WALLET, AssetType.KES, 25000.0)
        wallet_engine.create_wallet("268e1e85-a0b3-445d-827b-98e327af3bee", "ORG-KARIS-FARM", WalletType.KRT_WALLET, AssetType.KRT, 250.0)
        # Rider Wallets
        wallet_engine.create_wallet("da11cf88-5121-49b0-9a3b-28f0d8a11a2b", "ORG-KARIS-MOBILITY", WalletType.KES_WALLET, AssetType.KES, 5000.0)
        # Treasury Backing Wallets
        wallet_engine.create_wallet("TREASURY_IDENTITY", "ORG-KARIS-RETAIL", WalletType.RESERVE_WALLET, AssetType.KES, 10_000_000.0)
        wallet_engine.create_wallet("TREASURY_IDENTITY", "ORG-KARIS-RETAIL", WalletType.REWARD_POOL, AssetType.KRT, 5_000_000.0)
        wallet_engine.create_wallet("OPERATIONS_IDENTITY", "ORG-KARIS-RETAIL", WalletType.RESERVE_WALLET, AssetType.KES, 500_000.0)
        print("    ✔ Seeded KES, KRT, and Treasury Liquidity backing wallets.")

        print("  [4/7] Seeding Flagship KARIS FARM™ Produce Traceability Lineage (Section 28)...")
        farm = karis_farm_service.register_farm("268e1e85-a0b3-445d-827b-98e327af3bee", "ORG-KARIS-FARM", "Kamau Orchards - Machakos", "Machakos County", 15.0, "8b6ff564-ce30-489e-8a02-75004ccd5516")
        batch = karis_farm_service.log_harvest(farm["farm_id"], "HASS_AVOCADO", 1000.0, "GRADE_A", 150.0)
        print(f"    ✔ Seeded Harvest Batch: {batch.batch_number} | QR: {batch.traceability_qr_code}")

        print("  [5/7] Seeding Retail POS, Eatery KDS, and Delivery Zones (Sections 20, 21, 29, 30)...")
        store = retail_pos_service.register_store_and_terminal("ORG-KARIS-RETAIL", "Machakos Supermarket Mlolongo", "POS-MLO-01", "SUPERMARKET")
        eatery = eatery_service.register_eatery("ORG-KARIS-EATERY", "Machakos Cloud Kitchen", "CLOUD_KITCHEN", "Machakos Hub")
        eatery_service.add_menu_item(eatery["eatery_id"], "SKU-MEAL-AVO", "Gourmet Avocado Smoothie & Meal", 450.0, 15)
        logistics_service.register_rider("da11cf88-5121-49b0-9a3b-28f0d8a11a2b", "ORG-KARIS-MOBILITY", "MOTORCYCLE", "KMDE-123A", "ZONE-MACHAKOS-MLOLONGO")
        print("    ✔ Seeded Stores, POS Terminals, Menus, and Riders.")

        print("  [6/7] Seeding Healthcare Facilities & Mobility Fleet (Sections 32, 33)...")
        healthcare_service.register_facility("ORG-KARIS-HEALTH", "Machakos County Medical Hub", "COUNTY_HOSPITAL")
        healthcare_service.register_patient("7f8013a9-310c-4f16-9031-295274a26944", "B+")
        mobility_service.register_driver("da11cf88-5121-49b0-9a3b-28f0d8a11a2b", "ORG-KARIS-MOBILITY", "LIC-9901", "Bajaj TukTuk RE", "KTUK-001", "TUKTUK")
        print("    ✔ Seeded Clinics, Patients, and Mobility TukTuk Fleet.")

        print("  [7/7] Seeding Investment Capital Pools & Declarative Rules (Rule 7 & Section 25)...")
        pool = finance_investment_service.create_investment_pool("POOL-AGRI-2026", "Machakos Agriculture Growth Fund", "AGRICULTURE_GROWTH_FUND", 10_000_000.0, 14.5)
        finance_investment_service.deposit_capital(pool.pool_id, "8b6ff564-ce30-489e-8a02-75004ccd5516", "ORG-KARIS-FARM", 1_000_000.0)
        
        # Insert declarative rules into business_rules table
        conn.execute(text("""
            INSERT OR IGNORE INTO business_rules (rule_id, organization_id, rule_code, rule_name, description, trigger_event_type, conditions, actions, priority, is_active)
            VALUES (
                'r1111111-1111-1111-1111-111111111111', 'a0000000-0000-0000-0000-000000000001',
                'AUTOMATED_SETTLEMENT_ON_DELIVERY', 'Automated Settlement & KRT Reward',
                'Credits supplier KES wallet and awards 5% KRT loyalty tokens upon confirmed payment.',
                'PAYMENT_CONFIRMED', '[{"field":"status","op":"equals","value":"PAYMENT_CONFIRMED"}]',
                '[{"action":"CREDIT_SUPPLIER_WALLET"},{"action":"MINT_KRT_REWARD_5PCT"}]', 100, 1
            )
        """))
        conn.commit()
        print("    ✔ Seeded Investment Pools and Declarative Business Rules.")

    print("\n  ✔ ALL SEED DATA SUCCESSFULLY PERSISTED TO PRODUCTION DATABASE!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    seed_database()
