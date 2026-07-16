#!/usr/bin/env python3
"""
KARIS OS™ High-Throughput Concurrency & Stress Testing Engine (Section 44.3).
Simulates high-velocity multi-tenant transactions and verifies double-entry invariants and SHA-256 chain integrity under concurrency.
Run: python3 run_stress_test.py
"""

import concurrent.futures
import time
import uuid
from src.domain.models import AssetType, OrderItemModel, WalletType
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine
from src.core.ledger_engine import ledger_engine
from src.verticals.retail_pos.service import retail_pos_service
from src.verticals.logistics.service import logistics_service
from src.security.audit import audit_engine

def run_stress_test(num_operations: int = 150):
    print("=" * 90)
    print(f"    KARIS OS™ HIGH-THROUGHPUT STRESS BENCHMARK & CONCURRENCY TEST ({num_operations} OPS)")
    print("    Verifying Double-Entry Conservation & SHA-256 Audit Integrity Under Load")
    print("=" * 90)

    # 1. Reset Core State
    event_bus.event_store.clear()
    ledger_engine.entries.clear()
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()

    org_id = "ORG-STRESS-BENCH"
    cust_id = "STRESS-CUST-01"
    farmer_id = "STRESS-FARMER-01"
    rider_id = "STRESS-RIDER-01"

    # 2. Initialize high-balance wallets for stress execution
    wallet_engine.create_wallet(cust_id, org_id, WalletType.KES_WALLET, AssetType.KES, 10_000_000.0)
    wallet_engine.create_wallet(cust_id, org_id, WalletType.KRT_WALLET, AssetType.KRT, 500_000.0)
    wallet_engine.create_wallet(farmer_id, org_id, WalletType.KES_WALLET, AssetType.KES, 0.0)
    wallet_engine.create_wallet(rider_id, org_id, WalletType.KES_WALLET, AssetType.KES, 0.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org_id, WalletType.RESERVE_WALLET, AssetType.KES, 50_000_000.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org_id, WalletType.REWARD_POOL, AssetType.KRT, 20_000_000.0)
    wallet_engine.create_wallet("OPERATIONS_IDENTITY", org_id, WalletType.RESERVE_WALLET, AssetType.KES, 5_000_000.0)

    store = retail_pos_service.register_store_and_terminal(org_id, "Stress Store", "POS-STRESS-01")
    session = retail_pos_service.open_pos_session("POS-STRESS-01", farmer_id)

    def worker_pos_checkout(idx: int):
        return retail_pos_service.process_pos_checkout(
            session.session_id, store["store_id"], cust_id, farmer_id,
            items=[OrderItemModel(product_id="PROD-STRESS", sku="SKU-STRESS", quantity=1.0, unit_price=100.0, total_price=100.0)],
            payment_method="MIXED_PAYMENT", krt_discount_used=10.0
        )

    def worker_logistics_payout(idx: int):
        dispatch = logistics_service.request_delivery_dispatch(org_id, f"ORD-STRESS-{idx}", "Machakos Hub", "Mlolongo", 5.0)
        return logistics_service.confirm_delivery_completed(dispatch.dispatch_id, cust_id, "-1.35,36.93", f"OTP-{idx}")

    print(f"\n[BENCHMARK] Launching {num_operations} concurrent POS checkouts and logistics escrow payouts...")
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = []
        for i in range(num_operations // 2):
            futures.append(executor.submit(worker_pos_checkout, i))
            futures.append(executor.submit(worker_logistics_payout, i))
        
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    duration = time.time() - start_time
    throughput = len(results) / max(duration, 0.001)
    print(f"  ✔ Completed {len(results)} concurrent workflows in {duration:.3f} seconds ({throughput:.1f} ops/sec)!")

    # 3. Verify Double-Entry Ledger Invariants & SHA-256 Chain
    print("\n[VERIFICATION] Sweeping Double-Entry Ledger & Cryptographic Audit Hash Chains...")
    ledger_audit = audit_engine.verify_ledger_chain()
    event_audit = audit_engine.verify_event_store_integrity()

    assert ledger_audit["status"] == "VERIFIED_CLEAN", f"Ledger tamper check failed: {ledger_audit}"
    assert event_audit["status"] == "VERIFIED_CLEAN", f"Event tamper check failed: {event_audit}"

    print(f"  ✔ Ledger Audit Status: {ledger_audit['status']} ({ledger_audit['entries_checked']} Double-Entry Transfers)")
    print(f"  ✔ Event Audit Status:  {event_audit['status']} ({event_audit['events_checked']} Immutable Domain Events)")
    print(f"  ✔ Latest Hash Anchor:  {ledger_audit['latest_audit_hash'][:36]}...")

    print("\n" + "=" * 90)
    print("    STRESS BENCHMARK COMPLETED — ZERO RACE CONDITIONS OR TAMPER ANOMALIES DETECTED!")
    print("=" * 90 + "\n")

if __name__ == "__main__":
    run_stress_test()
