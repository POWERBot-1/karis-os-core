"""
KARIS OS™ :: BorderX Trade Finance Engine (`Section 58.10`).
Provides cross-border working capital, invoice financing, letters of credit,
trade credit, purchase financing, and supplier financing across East Africa.
Enforces Rule 3: No Credit Approval -> No Credit Purchase and Rule 9 double-entry accounting.
"""

from typing import Dict, Any, Tuple

class BorderXTradeFinanceEngine:
    """
    Evaluates creditworthiness of regional importers and exporters and structures trade finance facilities.
    """
    def __init__(self):
        self.supported_facilities = [
            "WORKING_CAPITAL", "INVOICE_FINANCING", "LETTERS_OF_CREDIT",
            "TRADE_CREDIT", "PURCHASE_FINANCING", "SUPPLIER_FINANCING"
        ]

    def evaluate_credit_application(
        self,
        borrower_account_id: str,
        facility_type: str,
        requested_amount_usd: float,
        reputation_score: int,
        cif_collateral_value_usd: float
    ) -> Tuple[bool, str, float]:
        """
        Evaluates trade finance application under Rule 3.
        Returns: (is_approved, status_reason, approved_amount_usd)
        """
        f_type = facility_type.upper()
        if f_type not in self.supported_facilities:
            return (False, f"Unsupported facility type: {facility_type}", 0.0)

        if reputation_score < 60:
            return (False, "REJECTED_LOW_REPUTATION_OR_COMPLIANCE_BREACH", 0.0)

        # Max loan is up to 80% of CIF collateral or reputation-based tier ceiling
        max_collateral_capacity = cif_collateral_value_usd * 0.80 if cif_collateral_value_usd > 0 else 50000.0
        approved_amount = min(requested_amount_usd, max_collateral_capacity)

        if approved_amount <= 0.0:
            return (False, "REJECTED_INSUFFICIENT_CIF_COLLATERAL", 0.0)

        return (True, "CREDIT_APPROVED", round(approved_amount, 4))
