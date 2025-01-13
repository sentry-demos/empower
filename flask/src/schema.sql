-- Ensure products table has proper constraints
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ensure inventory table has proper constraints and is linked to products
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    productId INTEGER NOT NULL REFERENCES products(id),
    count INTEGER NOT NULL DEFAULT 0 CHECK (count >= 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_product UNIQUE (productId)
);

-- Create trigger to auto-create inventory records for new products
CREATE OR REPLACE FUNCTION create_inventory_for_product()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO inventory (productId, count)
    VALUES (NEW.id, 0)
    ON CONFLICT (productId) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to products table
DROP TRIGGER IF EXISTS ensure_inventory_exists ON products;
CREATE TRIGGER ensure_inventory_exists
    AFTER INSERT ON products
    FOR EACH ROW
    EXECUTE FUNCTION create_inventory_for_product();

-- Create function to fix missing inventory records
CREATE OR REPLACE FUNCTION fix_missing_inventory()
RETURNS void AS $$
BEGIN
    INSERT INTO inventory (productId, count)
    SELECT id, 0
    FROM products p
    WHERE NOT EXISTS (
        SELECT 1 FROM inventory i WHERE i.productId = p.id
    );
END;
$$ LANGUAGE plpgsql;