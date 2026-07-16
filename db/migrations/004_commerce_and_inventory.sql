-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 004: Commerce, Marketplace, Inventory & Order Management Engine
-- Enforces: Section 14 (Commerce), Section 15 (Inventory), Section 16 (Orders), Section 17 (Payments)
-- Rule: Inventory belongs to supplier until settlement. No state change without event.
-- ============================================================================

-- 1. PRODUCTS & SKUS TABLE
CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    supplier_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    sku VARCHAR(100) UNIQUE NOT NULL,
    barcode VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    product_type VARCHAR(50) NOT NULL CHECK (product_type IN (
        'PHYSICAL_GOODS', 'FARM_PRODUCE', 'GROCERIES', 'MEDICAL_SUPPLIES',
        'RESTAURANT_MEAL', 'RETAIL_PRODUCT', 'DIGITAL_PRODUCT', 'SERVICE'
    )),
    category VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL, -- e.g., 'KG', 'CRATE', 'ITEM', 'HOUR', 'MEAL'
    unit_price NUMERIC(15, 4) NOT NULL CHECK (unit_price >= 0),
    currency VARCHAR(10) DEFAULT 'KES' NOT NULL,
    tax_rate NUMERIC(5, 2) DEFAULT 0.00 NOT NULL,
    krt_eligibility BOOLEAN DEFAULT TRUE NOT NULL,
    loyalty_eligibility BOOLEAN DEFAULT TRUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'OUT_OF_STOCK', 'DISCONTINUED')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. INVENTORY BATCHES TABLE
-- Tracks supplier ownership, batches, expiry dates, and agricultural traceability.
CREATE TABLE IF NOT EXISTS inventory_batches (
    batch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    supplier_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    batch_number VARCHAR(100) NOT NULL,
    quantity_available NUMERIC(15, 4) NOT NULL CHECK (quantity_available >= 0),
    quantity_reserved NUMERIC(15, 4) DEFAULT 0.0000 NOT NULL CHECK (quantity_reserved >= 0),
    unit_cost NUMERIC(15, 4) NOT NULL,
    quality_grade VARCHAR(50), -- e.g., 'GRADE_A', 'GRADE_B', 'EXPORT_GRADE'
    harvest_or_production_date DATE,
    expiry_date DATE,
    location_code VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'RESERVED', 'EXPIRED', 'WRITTEN_OFF')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(product_id, batch_number)
);

-- 3. INVENTORY AUDIT EVENTS
CREATE TABLE IF NOT EXISTS inventory_events_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES event_store(event_id),
    batch_id UUID NOT NULL REFERENCES inventory_batches(batch_id),
    operation_type VARCHAR(50) NOT NULL CHECK (operation_type IN (
        'INVENTORY_CREATED', 'STOCK_RECEIVED', 'STOCK_RESERVED', 'STOCK_RELEASED',
        'STOCK_TRANSFERRED', 'STOCK_ADJUSTED', 'STOCK_EXPIRED', 'STOCK_SOLD', 'STOCK_RETURNED'
    )),
    quantity_change NUMERIC(15, 4) NOT NULL,
    previous_quantity NUMERIC(15, 4) NOT NULL,
    new_quantity NUMERIC(15, 4) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. ORDERS TABLE
CREATE TABLE IF NOT EXISTS orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    customer_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    supplier_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    order_number VARCHAR(100) UNIQUE NOT NULL,
    order_status VARCHAR(50) NOT NULL DEFAULT 'ORDER_CREATED' CHECK (order_status IN (
        'ORDER_CREATED', 'ORDER_VALIDATED', 'PAYMENT_PENDING', 'PAYMENT_CONFIRMED',
        'STOCK_RESERVED', 'READY_FOR_FULFILLMENT', 'ASSIGNED_TO_DELIVERY',
        'IN_TRANSIT', 'DELIVERED', 'SETTLED', 'CLOSED', 'CANCELLED'
    )),
    delivery_method VARCHAR(50) NOT NULL CHECK (delivery_method IN ('DELIVERY_RIDER', 'SCHEDULED_PICKUP', 'IN_STORE')),
    payment_status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (payment_status IN ('PENDING', 'PAID_PARTIAL', 'PAID_FULL', 'REFUNDED')),
    total_kes_amount NUMERIC(15, 4) NOT NULL CHECK (total_kes_amount >= 0),
    paid_kes_amount NUMERIC(15, 4) DEFAULT 0.0000 NOT NULL,
    paid_krt_amount NUMERIC(15, 4) DEFAULT 0.0000 NOT NULL,
    krt_kes_exchange_rate NUMERIC(15, 4) DEFAULT 1.0000 NOT NULL,
    delivery_fee_kes NUMERIC(15, 4) DEFAULT 0.0000 NOT NULL,
    tax_amount_kes NUMERIC(15, 4) DEFAULT 0.0000 NOT NULL,
    correlation_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. ORDER ITEMS TABLE
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id),
    batch_id UUID REFERENCES inventory_batches(batch_id),
    quantity NUMERIC(15, 4) NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(15, 4) NOT NULL,
    total_price NUMERIC(15, 4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 6. PAYMENTS TABLE (Mixed payment tracking: KES + KRT)
CREATE TABLE IF NOT EXISTS payments (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE RESTRICT,
    payer_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN (
        'M_PESA', 'BANK_TRANSFER', 'CARD', 'CASH', 'KES_WALLET', 'KRT_WALLET', 'CREDIT_WALLET', 'MIXED_PAYMENT'
    )),
    external_reference VARCHAR(100), -- e.g., M-Pesa Transaction Code (QG37XXXXXXXX)
    amount_kes NUMERIC(15, 4) NOT NULL CHECK (amount_kes >= 0),
    amount_krt NUMERIC(15, 4) DEFAULT 0.0000 NOT NULL CHECK (amount_krt >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'PAYMENT_INITIATED' CHECK (status IN (
        'PAYMENT_INITIATED', 'PAYMENT_CONFIRMED', 'PAYMENT_FAILED', 'PAYMENT_REFUNDED'
    )),
    event_id UUID NOT NULL REFERENCES event_store(event_id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_supplier ON products(supplier_identity_id);
CREATE INDEX idx_inventory_batches_product ON inventory_batches(product_id, status);
CREATE INDEX idx_orders_customer ON orders(customer_identity_id, order_status);
CREATE INDEX idx_payments_order ON payments(order_id, status);
