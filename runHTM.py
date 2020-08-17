import psycopg2

conn = psycopg2.connect(host="ec2-34-233-226-84.compute-1.amazonaws.com", dbname="d77knu57t1q9j9", user="jsnmfiqtcggjyu", password="368e05099543272efb167e9fa3173338be43c1e787666ed2478f51ef050707b9")
conn.autocommit = True
cursor = conn.cursor()

cursor.execute("SELECT file_name FROM database.scrape WHERE accession_number='0000021076-02-000019'")
text_filing = cursor.fetchone()[0]