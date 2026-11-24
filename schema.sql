DROP TABLE IF EXISTS returns, order_items, orders, region_targets, regional_managers, products, customers CASCADE;
CREATE TABLE customers(customer_id text PRIMARY KEY,name text,email text,segment text,city text,state text);
CREATE TABLE products(product_id text PRIMARY KEY,category text,sub_category text,product_name text,unit_cost numeric,list_price numeric);
CREATE TABLE orders(order_id text PRIMARY KEY,customer_id text REFERENCES customers,order_date date,ship_date date,ship_mode text,region text,state text,status text);
CREATE TABLE order_items(line_id int PRIMARY KEY,order_id text REFERENCES orders,product_id text REFERENCES products,quantity int,discount numeric,sales numeric,profit numeric);
CREATE TABLE returns(order_id text,returned_date date,reason text);
CREATE TABLE regional_managers(region text,manager text);
CREATE TABLE region_targets(year int,region text,sales_target bigint);
