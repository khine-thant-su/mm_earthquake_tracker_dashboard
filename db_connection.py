import psycopg2
from config import DB_CONFIG

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_quake_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS quake_info (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP,
        magnitude NUMERIC NOT NULL,
        longitude NUMERIC NOT NULL,
        latitude NUMERIC NOT NULL,
        depth NUMERIC NOT NULL,
        place TEXT NOT NULL
    );
    
    SET timezone = "Asia/Yangon";
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ quake_info table created successfully.")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_quake_table()


