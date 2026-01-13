CREATE TABLE product_stock (
        id SERIAL PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2),
        remark TEXT
    );

    COMMENT ON COLUMN product_stock.id IS '主键ID';
    COMMENT ON COLUMN product_stock.product_name IS '产品名称';
    COMMENT ON COLUMN product_stock.price IS '产品单价(保留两位小数)';
    COMMENT ON COLUMN product_stock.remark IS '备注信息';