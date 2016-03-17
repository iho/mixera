DROP DATABASE aiopg_db;
DROP USER aiopg_user;
CREATE USER aiopg_user WITH ENCRYPTED PASSWORD 'password' CREATEDB;
CREATE DATABASE  aiopg_db WITH ENCODING 'UTF-8' OWNER "aiopg_user";
GRANT ALL PRIVILEGES ON DATABASE aiopg_db TO aiopg_user;