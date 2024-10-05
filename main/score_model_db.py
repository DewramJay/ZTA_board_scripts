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
    INSERT INTO weights (ml_weight, ea_weight, cr_weight, st_weight)
    VALUES (0, 0, 0, 0)
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



# Close the connection
conn.close()
