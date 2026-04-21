
-- 01_recreate_demo_calc_database_v6.2.sql
-- Выполнять из базы postgres. В SQL-приложении этот запрос должен идти отдельно, с autocommit.

DROP DATABASE IF EXISTS demo_calc WITH (FORCE);
CREATE DATABASE demo_calc
    WITH ENCODING 'UTF8'
    TEMPLATE template0;
