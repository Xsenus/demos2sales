-- 01_recreate_demo_calc_database_v6_5.sql
-- Выполнять из базы postgres. Запрос должен идти отдельно, с autocommit.

DROP DATABASE IF EXISTS demo_calc WITH (FORCE);
CREATE DATABASE demo_calc
    WITH ENCODING 'UTF8'
    TEMPLATE template0;
