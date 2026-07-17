// ============================================================================
// KARIS OS™ TypeScript / Node Client SDK (Generated via Section 46.2 Engine)
// Enforces strong interface definitions matching Draft-07 JSON Event Schemas
// ============================================================================

export interface OrderItem {
  product_id: string;
  sku: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export class KarisOsClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(baseUrl = "http://localhost:8000", apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.headers = { "Content-Type": "application/json" };
    if (apiKey) this.headers["Authorization"] = `Bearer ${apiKey}`;
  }

  async createOrder(customerId: string, supplierId: string, items: OrderItem[], orgId = "ORG-KARIS-RETAIL") {
    const res = await fetch(`${this.baseUrl}/api/v1/orders`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ organization_id: orgId, customer_identity_id: customerId, supplier_identity_id: supplierId, items })
    });
    return res.json();
  }

  async submitPrediction(userId: string, fixtureId: string, outcome: string, stakeKrt: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/power-bot-x/predict`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ user_id: userId, fixture_id: fixtureId, predicted_outcome: outcome, stake_krt: stakeKrt })
    });
    return res.json();
  }

  async logEnergyTelemetry(installationId: string, kwhGenerated: number, feedInKwh: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/energy-grid/telemetry`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ installation_id: installationId, kwh_generated_today: kwhGenerated, kwh_consumed_today: 0, microgrid_feed_in_kwh: feedInKwh })
    });
    return res.json();
  }

  async getActivePaymentLink() {
    const res = await fetch(`${this.baseUrl}/api/v1/payment-links/active-temporary`, { headers: this.headers });
    return res.json();
  }

  async createCheckoutPackage(orderId: string, amountKes: number, payerId: string) {
    const res = await fetch(`${this.baseUrl}/api/v1/payment-links/checkout-package`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ order_id: orderId, amount_kes: amountKes, payer_identity_id: payerId })
    });
    return res.json();
  }

  async paySolarPayg(installationId: string, payerId: string, amountKrt: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/energy-grid/payg`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ installation_id: installationId, payer_user_id: payerId, amount_krt: amountKrt })
    });
    return res.json();
  }

  async logPharmaTelemetry(batchId: string, tempC: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/expansion-suite/pharma/telemetry`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ batch_id: batchId, temperature_celsius: tempC })
    });
    return res.json();
  }

  async distributePropDividends(syndicationId: string, poolKrt: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/expansion-suite/prop-share/distribute-dividends`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ syndication_id: syndicationId, total_rental_pool_krt: poolKrt })
    });
    return res.json();
  }

  async payTuition(planId: string, payerId: string, amountKes: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/expansion-suite/edu-pay/installments`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ plan_id: planId, payer_id: payerId, amount_kes: amountKes })
    });
    return res.json();
  }

  async tipLoopCreator(tipperId: string, creatorId: string, postId: string, amountKrt: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/karis-loop/tip`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ tipper_identity_id: tipperId, creator_identity_id: creatorId, post_id: postId, amount_krt: amountKrt })
    });
    return res.json();
  }

  async checkoutLoopProduct(buyerId: string, postId: string, prodId: string, amount: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/karis-loop/shoppable-checkout`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ buyer_identity_id: buyerId, post_id: postId, linked_product_id: prodId, amount_kes_or_krt: amount })
    });
    return res.json();
  }

  async recordStudentMastery(studentId: string, instId: string, conceptId: string, score: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/karis-academy/mastery`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ student_identity_id: studentId, institution_id: instId, concept_id: conceptId, mastery_score_pct: score })
    });
    return res.json();
  }

  async disburseAcademyScholarship(studentId: string, instId: string, amountKrt: number) {
    const res = await fetch(`${this.baseUrl}/api/v1/karis-academy/scholarship`, {
      method: "POST", headers: this.headers,
      body: JSON.stringify({ student_identity_id: studentId, institution_id: instId, amount_krt: amountKrt })
    });
    return res.json();
  }
}
