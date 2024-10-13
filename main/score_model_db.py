import sqlite3
import json

# Initialize the database connection
conn = sqlite3.connect('score_model.db')

cursor = conn.cursor()

# Step 1: Create a new table with the desired schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ml_weight REAL,
        ea_weight REAL,
        cr_weight REAL,
        st_weight REAL 
    )
''')

# Commit the changes
conn.commit()

cursor.execute('''
    DROP TABLE IF EXISTS trust_score;
''')

# Commit the changes
conn.commit()



cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS cyber_risk_weight (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    init_weight REAL,
    scaling_factor REAL,
    anom_count REAL
)
''')



conn.commit()

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS trust_score (
    mac_address TEXT PRIMARY KEY,
    ml REAL,
    ea REAL,
    cr REAL,
    st REAL,
    total REAL
)
''')



conn.commit()




# Close the connection
conn.close()
