import csv
import subprocess

CSV_FILE = 'migration.csv'

# Note the '-i' instead of '-it', and '-q' to quiet the psql startup text
DOCKER_CMD = [
    'docker', 'exec', '-i', 'thingsboard-thingsboard-1',
    'psql', '-U', 'thingsboard', '-d', 'thingsboard', '-q'
]

def run_migration():
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                device_name = row['device_name'].strip()
                old_key = row['old_key'].strip()
                new_key = row['new_key'].strip()

                print(f"Processing: {device_name} | '{old_key}' -> '{new_key}'")

                # The PL/pgSQL block handles the lookup and update logic in one transaction
                sql_query = f"""
                DO $$
                DECLARE
                    v_device_id uuid;
                    v_old_key_id integer;
                    v_new_key_id integer;
                BEGIN
                    -- 1. Get the target Device ID
                    SELECT id INTO v_device_id FROM device WHERE name = '{device_name}';
                    IF v_device_id IS NULL THEN
                        RAISE EXCEPTION 'Device "%" not found.', '{device_name}';
                    END IF;

                    -- 2. Get the Old Key ID
                    SELECT key_id INTO v_old_key_id FROM key_dictionary WHERE key = '{old_key}';
                    IF v_old_key_id IS NULL THEN
                        RAISE EXCEPTION 'Old key "%" not found in dictionary.', '{old_key}';
                    END IF;

                    -- 3. Get the New Key ID (if it already exists globally)
                    SELECT key_id INTO v_new_key_id FROM key_dictionary WHERE key = '{new_key}';

                    -- 4. If the New Key does not exist yet, create it safely
                    IF v_new_key_id IS NULL THEN
                        INSERT INTO key_dictionary (key) VALUES ('{new_key}') RETURNING key_id INTO v_new_key_id;
                    END IF;

                    -- 5. Update historical data specifically for this device
                    UPDATE ts_kv
                    SET key = v_new_key_id
                    WHERE key = v_old_key_id AND entity_id = v_device_id;

                    -- 6. Clean up the latest cache for this device
                    DELETE FROM ts_kv_latest
                    WHERE key = v_old_key_id AND entity_id = v_device_id;

                END $$;
                """

                # Execute the Docker command and pipe the SQL block to psql
                result = subprocess.run(
                    DOCKER_CMD,
                    input=sql_query,
                    text=True,
                    capture_output=True
                )

                # Check for errors
                if result.returncode != 0:
                    print(f"  [ERROR] {result.stderr.strip()}")
                else:
                    print("  [SUCCESS] Data merged successfully.")

    except FileNotFoundError:
        print(f"Error: Could not find the file '{CSV_FILE}'.")
    except KeyError as e:
        print(f"Error: CSV is missing required column: {e}")

if __name__ == "__main__":
    print("Starting ThingsBoard telemetry migration...")
    run_migration()
    print("Migration complete. Do not forget to restart your ThingsBoard container!")