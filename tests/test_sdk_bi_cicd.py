import pytest
from src.integrations.sdk_generator import sdk_generator_engine
from src.observability.bi_aggregation import bi_executive_engine
from src.observability.cicd_quality_gate import cicd_quality_gate_engine

def test_enterprise_api_sdk_client_generator():
    org = "ORG-KARIS-RETAIL"
    dev_id = "DEV-CLIENT-01"

    # 1. Python SDK
    py_sdk = sdk_generator_engine.generate_python_sdk_package(org, dev_id)
    assert py_sdk["sdk_language"] == "PYTHON_ASYNC_SYNC"
    assert py_sdk["package_filename"] == "karis_os_client.py"
    assert "class KarisOsClient:" in py_sdk["generated_code_preview"]

    # 2. TypeScript SDK
    ts_sdk = sdk_generator_engine.generate_typescript_sdk_package(org, dev_id)
    assert ts_sdk["sdk_language"] == "TYPESCRIPT_NODE_BROWSER"
    assert ts_sdk["package_filename"] == "karis-os-sdk.ts"
    assert "export class KarisOsClient" in ts_sdk["generated_code_preview"]

def test_unified_bi_executive_dashboard_aggregation():
    org = "ORG-KARIS-RETAIL"
    report = bi_executive_engine.generate_unified_bi_executive_report(org)
    assert report["status"] == "COMPLETED"
    assert "dashboards" in report
    assert "EXECUTIVE_SUMMARY" in report["dashboards"]
    assert "COMMERCE_RETAIL_POS" in report["dashboards"]
    assert "DELIVERY_LOGISTICS" in report["dashboards"]
    assert "FINANCE_TREASURY_LENDING" in report["dashboards"]
    assert "HEALTHCARE_EMR_CHV" in report["dashboards"]

def test_cicd_automated_deployment_quality_gate():
    org = "ORG-KARIS-RETAIL"
    # 1. Passing Quality Gate
    passed_gate = cicd_quality_gate_engine.evaluate_cicd_release_quality_gate(
        commit_hash="A8F291B0C4D5E6F7", branch_name="main",
        pytest_pass_pct=100.0, stress_ops_sec=2380.0, security_vulns=0, organization_id=org
    )
    assert passed_gate["gate_decision"] == "CICD_GATE_PASSED_AUTHORIZED"
    assert "authorized" in passed_gate["evaluation_summary"].lower()

    # 2. Failing Quality Gate (Pytest failure)
    failed_gate = cicd_quality_gate_engine.evaluate_cicd_release_quality_gate(
        commit_hash="FAIL-HASH-99", branch_name="main",
        pytest_pass_pct=95.0, stress_ops_sec=2380.0, security_vulns=0, organization_id=org
    )
    assert failed_gate["gate_decision"] == "CICD_GATE_FAILED_REJECTED"
    assert "breached" in failed_gate["evaluation_summary"].lower()
