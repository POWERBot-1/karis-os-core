-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 011: Eatery, Food Services & Kitchen Display System (KDS)
-- Enforces: Section 29 (Eatery & Food Services Vertical)
-- ============================================================================

-- 1. RESTAURANTS & CLOUD KITCHENS
CREATE TABLE IF NOT EXISTS eateries (
    eatery_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    eatery_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'EAT-MACHAKOS-KITCHEN-01'
    eatery_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100) NOT NULL CHECK (business_type IN (
        'RESTAURANT', 'CAFE', 'CLOUD_KITCHEN', 'HOTEL_KITCHEN', 'BAKERY', 'FAST_FOOD'
    )),
    address TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. DIGITAL RECIPES & INGREDIENT INVENTORY DEDUCTION
CREATE TABLE IF NOT EXISTS kitchen_ingredients (
    ingredient_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    eatery_id UUID NOT NULL REFERENCES eateries(eatery_id) ON DELETE CASCADE,
    ingredient_name VARCHAR(255) NOT NULL, -- e.g., 'Avocado Paste', 'Maize Flour', 'Beef Fillet'
    unit VARCHAR(50) NOT NULL, -- e.g., 'KG', 'LITER', 'PORTION'
    quantity_available NUMERIC(15, 4) NOT NULL CHECK (quantity_available >= 0),
    reorder_level NUMERIC(15, 4) DEFAULT 5.00 NOT NULL,
    unit_cost_kes NUMERIC(15, 2) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS meal_recipes (
    recipe_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meal_product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    ingredient_id UUID NOT NULL REFERENCES kitchen_ingredients(ingredient_id),
    quantity_required NUMERIC(15, 4) NOT NULL CHECK (quantity_required > 0),
    UNIQUE(meal_product_id, ingredient_id)
);

-- 3. KITCHEN DISPLAY SYSTEM (KDS) QUEUE TABLE
CREATE TABLE IF NOT EXISTS kds_orders (
    kds_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    eatery_id UUID NOT NULL REFERENCES eateries(eatery_id) ON DELETE CASCADE,
    order_id UUID NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    table_number VARCHAR(50), -- Or 'DELIVERY_ORDER' / 'TAKEAWAY'
    preparation_state VARCHAR(50) NOT NULL DEFAULT 'RECEIVED' CHECK (preparation_state IN (
        'RECEIVED', 'PREPARING', 'READY_FOR_PICKUP', 'PICKED_UP', 'DELIVERED', 'CANCELLED'
    )),
    priority_level INT DEFAULT 1 NOT NULL, -- Higher = higher priority
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    preparation_started_at TIMESTAMP WITH TIME ZONE,
    ready_at TIMESTAMP WITH TIME ZONE,
    chef_identity_id UUID REFERENCES identities(identity_id)
);

CREATE INDEX idx_kds_orders_eatery_state ON kds_orders(eatery_id, preparation_state);
