import sqlite3
import pymongo

print("Connecting to MongoDB Atlas...")
client = pymongo.MongoClient('mongodb+srv://an2k52012_db_user:Anhoang.912@cluster0.hrrmitg.mongodb.net/?retryWrites=true&w=majority')
mongo_db = client['ecommerce_db']

sqlite_conn = sqlite3.connect('db.sqlite3')
sqlite_conn.row_factory = sqlite3.Row
cur = sqlite_conn.cursor()

# Get all tables from SQLite
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in cur.fetchall()]

for table in tables:
    cur.execute(f"SELECT * FROM \"{table}\"")
    rows = cur.fetchall()
    if rows:
        docs = []
        for r in rows:
            doc = dict(r)
            if 'id' in doc:
                doc['_id'] = doc['id']
            elif 'session_key' in doc:
                doc['_id'] = doc['session_key']
            docs.append(doc)
        
        col = mongo_db[table]
        # Clear existing and insert
        col.delete_many({})
        col.insert_many(docs)
        print(f"Synced {len(docs)} documents to collection: {table}")
    else:
        print(f"Table {table} is empty, skipping.")

print("\n--- MongoDB Atlas Sync Completed Successfully! ---")
for col_name in mongo_db.list_collection_names():
    print(f"  Collection '{col_name}': {mongo_db[col_name].count_documents({})} documents")
