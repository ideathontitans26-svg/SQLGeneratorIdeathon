"""Add sample data to HackthonTest.db"""
import sqlite3

path = r"C:\Users\divya.bajaj_jadeglob\Downloads\DB.Browser.for.SQLite-v3.13.1-win32\HackthonTest.db"
conn = sqlite3.connect(path)
c = conn.cursor()

# 1. CUSTOMERS
c.executemany("""
    INSERT INTO CUSTOMERS (customer_id, customer_no, customer_name, status, addr_line1, city, state, country, postal_code, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    (1, "C001", "Acme Corp", "active", "123 Main St", "New York", "NY", "USA", "10001", "2024-01-15"),
    (2, "C002", "Tech Solutions Inc", "active", "456 Oak Ave", "San Francisco", "CA", "USA", "94102", "2024-02-20"),
    (3, "C003", "Global Traders", "active", "789 Commerce Rd", "Chicago", "IL", "USA", "60601", "2024-03-10"),
    (4, "C004", "Sunrise Foods", "inactive", "321 Market St", "Boston", "MA", "USA", "02101", "2024-04-05"),
    (5, "C005", "Mega Mart", "active", "555 Retail Blvd", "Houston", "TX", "USA", "77001", "2024-05-12"),
])

# 2. ADDRESSES
c.executemany("""
    INSERT INTO ADDRESSES (address_id, customer_id, addr_line1, addr_line2, city, state, country, postal_code, is_default)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    (1, 1, "123 Main St", "Suite 100", "New York", 36, 1, 10001, 1),
    (2, 2, "456 Oak Ave", None, "San Francisco", 5, 1, 94102, 1),
    (3, 3, "789 Commerce Rd", "Floor 2", "Chicago", 17, 1, 60601, 1),
])

# 3. product_id (Products table)
c.executemany("""
    INSERT INTO "product_id" (product_id, sku, product_name, brand, uom, category_code, active_flag, cost_price, selling_price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    (1, "SKU-001", "Widget A", "BrandX", "EA", "ELEC", 1, 10.50, 19.99),
    (2, "SKU-002", "Gadget B", "BrandY", "EA", "ELEC", 1, 25.00, 49.99),
    (3, "SKU-003", "Tool Set", "BrandZ", "SET", "TOOLS", 1, 45.00, 89.99),
    (4, "SKU-004", "Office Chair", "BrandX", "EA", "FURN", 1, 80.00, 149.99),
    (5, "SKU-005", "Desk Lamp", "BrandY", "EA", "FURN", 1, 15.00, 29.99),
])

# 4. ORDERS
c.executemany("""
    INSERT INTO ORDERS (order_id, order_no, customer_no, customer_id, order_date, order_status, order_type, order_domain, country)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    (1, "ORD-001", "C001", 1, "2024-06-01", "shipped", "sales", "B2B", "USA"),
    (2, "ORD-002", "C002", 2, "2024-06-05", "pending", "sales", "B2B", "USA"),
    (3, "ORD-003", "C001", 1, "2024-06-10", "shipped", "sales", "B2B", "USA"),
    (4, "ORD-004", "C003", 3, "2024-06-15", "cancelled", "sales", "B2C", "USA"),
    (5, "ORD-005", "C005", 5, "2024-06-20", "pending", "sales", "B2B", "USA"),
])

# 5. ORDER_LINES
c.executemany("""
    INSERT INTO ORDER_LINES (order_line_id, order_id, order_no, order_date, order_type, line_no, sku, uom, ordered_qty, unit_price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    (1, 1, "ORD-001", "2024-06-01", "sales", 1, "SKU-001", "EA", 10, 19.99),
    (2, 1, "ORD-001", "2024-06-01", "sales", 2, "SKU-002", "EA", 5, 49.99),
    (3, 2, "ORD-002", "2024-06-05", "sales", 1, "SKU-003", "SET", 2, 89.99),
    (4, 3, "ORD-003", "2024-06-10", "sales", 1, "SKU-004", "EA", 3, 149.99),
    (5, 5, "ORD-005", "2024-06-20", "sales", 1, "SKU-005", "EA", 20, 29.99),
])

# 6. SHIPMENTS
c.executemany("""
    INSERT INTO SHIPMENTS (shipment_id, shipment_no, order_no, shipment_date, ship_to_city, ship_to_state, ship_to_cntry)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    (1, "SHP-001", "ORD-001", "2024-06-03", "New York", "NY", "USA"),
    (2, "SHP-002", "ORD-003", "2024-06-12", "New York", "NY", "USA"),
])

# 7. SHIPMENT_LINES
c.executemany("""
    INSERT INTO SHIPMENT_LINES (shipment_line_id, shipment_no, sku, line_no, shipped_qty)
    VALUES (?, ?, ?, ?, ?)
""", [
    (1, "SHP-001", "SKU-001", 1, 10),
    (2, "SHP-001", "SKU-002", 2, 5),
    (3, "SHP-002", "SKU-004", 1, 3),
])

conn.commit()
print("Sample data added successfully!")
conn.close()
