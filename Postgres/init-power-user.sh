#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
    CREATE EXTENSION IF NOT EXISTS vector;

    DO
    \$do\$
    BEGIN
       IF NOT EXISTS (
          SELECT FROM pg_catalog.pg_roles
          WHERE  rolname = '$POWER_USER') THEN

          CREATE ROLE "$POWER_USER" LOGIN PASSWORD '$POWER_USER_PASSWORD';
       END IF;
    END
    \$do\$;

    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POWER_USER";
    GRANT ALL ON SCHEMA public TO "$POWER_USER";
EOSQL
