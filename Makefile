setup_db: 
	sudo -u postgres psql -f setup_db.sql
	sudo -u postgres psql  -d aiopg_db -c "CREATE EXTENSION pgcrypto;"          

cli:
	pgcli postgresql+psycopg2://aiopg_user:password@127.0.0.1:5432/aiopg_db
