CREATE TABLE "myschema"."orders" (
    "order_id" INT8 PRIMARY KEY,
    "total_amount" DECIMAL(12, 2),
    "user_id" INTEGER
);

COMMENT ON COLUMN "myschema"."orders"."order_id" IS '订单全局唯一标识';
COMMENT ON COLUMN myschema.orders.total_amount IS '总金额(元)';
COMMENT ON COLUMN orders.user_id IS '用户ID';