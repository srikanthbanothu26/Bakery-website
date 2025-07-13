import psycopg2

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="defaultdb",
    user="avnadmin",
    password="AVNS_d3-sc5JeWUnKJAgPjx7",
    host="pg-185fedd6-banothusrikanth267-d588.f.aivencloud.com",
    port="26621",
    sslmode="require"
)

with conn:
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO "Home_state" (name, code, country_id) 
        SELECT
            hs.name,
            hs.code,
            c.id
        FROM "Home_states" hs
        JOIN "Home_countries" c ON hs.country_id = c.id
        ON CONFLICT (name) DO UPDATE 
        SET code = EXCLUDED.code,
            country_id = EXCLUDED.country_id;
        """
        cursor.execute(insert_query)
        print("✅ States inserted/updated successfully into Home_state.")

conn.close()
