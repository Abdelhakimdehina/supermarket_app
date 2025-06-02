-- Sample products
INSERT INTO products (name, description, price, stock, category, barcode, is_active, created_at, updated_at)
VALUES 
    ('Coca Cola 2L', 'Refreshing cola drink', 2.99, 50, 'Beverages', '123456789', 1, DATETIME('now'), DATETIME('now')),
    ('White Bread', 'Fresh baked white bread', 1.99, 30, 'Bread/Bakery', '234567890', 1, DATETIME('now'), DATETIME('now')),
    ('Tomato Soup', 'Canned tomato soup', 1.49, 100, 'Canned/Jarred Goods', '345678901', 1, DATETIME('now'), DATETIME('now')),
    ('Milk 1L', 'Fresh whole milk', 3.49, 40, 'Dairy', '456789012', 1, DATETIME('now'), DATETIME('now')),
    ('Sugar 1kg', 'White granulated sugar', 2.49, 80, 'Dry/Baking Goods', '567890123', 1, DATETIME('now'), DATETIME('now')),
    ('Ice Cream', 'Vanilla ice cream', 4.99, 25, 'Frozen Foods', '678901234', 1, DATETIME('now'), DATETIME('now')),
    ('Chicken Breast', 'Fresh chicken breast', 7.99, 20, 'Meat', '789012345', 1, DATETIME('now'), DATETIME('now')),
    ('Bananas', 'Fresh bananas per kg', 1.99, 60, 'Produce', '890123456', 1, DATETIME('now'), DATETIME('now')),
    ('Dish Soap', 'Liquid dish soap', 3.99, 45, 'Cleaners', '901234567', 1, DATETIME('now'), DATETIME('now')),
    ('Toilet Paper', '12 rolls pack', 8.99, 35, 'Paper Goods', '012345678', 1, DATETIME('now'), DATETIME('now')),
    ('Toothpaste', 'Mint toothpaste', 2.99, 55, 'Personal Care', '123456780', 1, DATETIME('now'), DATETIME('now')),
    ('Batteries', 'AA batteries 4-pack', 5.99, 40, 'Other', '234567801', 1, DATETIME('now'), DATETIME('now')); 