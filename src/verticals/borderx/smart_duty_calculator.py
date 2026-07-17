"""
KARIS OS™ :: BorderX Smart Duty Calculator (`Section 58.3`).
Calculates exact customs duty breakdown: import duty, export duty, VAT, excise,
railway levy, IDF, RDL, port charges, clearing fees, agent fees, and inspection fees.
Applies KRT clearing fee discounts when paying via KRT Digital Utility Token.
"""

from typing import Dict, Any

class BorderXSmartDutyCalculator:
    """
    Computes precise East African regional duty and fee assessments.
    """
    def __init__(self):
        self.usd_to_kes_rate = 130.0
        self.krt_to_kes_rate = 1.0  # 1 KRT = 1 KES default parity

    def calculate_duty(
        self,
        cif_value_usd: float,
        duty_pct: float = 25.0,
        vat_pct: float = 16.0,
        excise_pct: float = 0.0,
        railway_levy_pct: float = 1.5,
        idf_pct: float = 2.5,
        rdl_pct: float = 1.5,
        port_charges_kes: float = 15000.0,
        clearing_fees_kes: float = 12000.0,
        agent_fees_kes: float = 10000.0,
        inspection_fees_kes: float = 3500.0,
        pay_fees_in_krt: bool = True,
        krt_staking_discount_pct: float = 0.0
    ) -> Dict[str, Any]:
        """
        Computes full duty breakdown in KES and converted KRT equivalent.
        """
        cif_kes = round(cif_value_usd * self.usd_to_kes_rate, 4)

        import_duty_kes = round(cif_kes * (duty_pct / 100.0), 4)
        excise_kes = round((cif_kes + import_duty_kes) * (excise_pct / 100.0), 4)
        vat_kes = round((cif_kes + import_duty_kes + excise_kes) * (vat_pct / 100.0), 4)

        railway_levy_kes = round(cif_kes * (railway_levy_pct / 100.0), 4)
        idf_kes = round(cif_kes * (idf_pct / 100.0), 4)
        rdl_kes = round(cif_kes * (rdl_pct / 100.0), 4)

        # Apply KRT discount on clearing fees and agent fees (up to 50% off + any active staking discount)
        total_discount_pct = min(50.0, 25.0 + krt_staking_discount_pct) if pay_fees_in_krt else 0.0

        if pay_fees_in_krt:
            final_clearing_fees = round(clearing_fees_kes * (1.0 - (total_discount_pct / 100.0)), 4)
            final_agent_fees = round(agent_fees_kes * (1.0 - (total_discount_pct / 100.0)), 4)
        else:
            final_clearing_fees = clearing_fees_kes
            final_agent_fees = agent_fees_kes

        total_statutory_taxes_kes = round(import_duty_kes + excise_kes + vat_kes + railway_levy_kes + idf_kes + rdl_kes, 4)
        total_logistics_fees_kes = round(port_charges_kes + final_clearing_fees + final_agent_fees + inspection_fees_kes, 4)
        total_amount_kes = round(total_statutory_taxes_kes + total_logistics_fees_kes, 4)
        total_amount_krt = round(total_amount_kes / self.krt_to_kes_rate, 4)

        return {
            "cif_value_usd": cif_value_usd,
            "cif_value_kes": cif_kes,
            "import_duty_kes": import_duty_kes,
            "export_duty_kes": 0.0,
            "vat_kes": vat_kes,
            "excise_kes": excise_kes,
            "railway_levy_kes": railway_levy_kes,
            "idf_kes": idf_kes,
            "rdl_kes": rdl_kes,
            "port_charges_kes": port_charges_kes,
            "clearing_fees_kes": final_clearing_fees,
            "agent_fees_kes": final_agent_fees,
            "inspection_fees_kes": inspection_fees_kes,
            "total_statutory_taxes_kes": total_statutory_taxes_kes,
            "total_logistics_fees_kes": total_logistics_fees_kes,
            "total_amount_kes": total_amount_kes,
            "total_amount_krt": total_amount_krt,
            "pay_fees_in_krt": pay_fees_in_krt,
            "krt_fee_discount_pct": total_discount_pct
        }
