import os
from email.parser import Parser
from email.utils import parsedate_to_datetime
import mysql.connector
import datetime
import time
import re
import csv
import itertools

rootdir = "./enron_with_categories"

# Function to parse an email file, extract fields 
def email_analyse(inputfile, dictionary_email_list, to_email_dict):
    with open(inputfile, "r") as f:
        data = f.read()
 
    email = Parser().parsestr(data)
    email_to = email['to'] if email['to'] else ''
    email_cc = email['cc'] if email['cc'] else ''
    email_bcc = email['bcc'] if email['bcc'] else ''
    direct = 0
    if email_to or email_cc or email_bcc:
        email_to = email_to.replace("\n", "").replace("\t", "").replace(" ", "").split(",") if email_to else []
        email_cc = email_cc.replace("\n", "").replace("\t", "").replace(" ", "").split(",") if email_cc else []
        email_bcc = email_bcc.replace("\n", "").replace("\t", "").replace(" ", "").split(",") if email_bcc else []
        
        if len(email_to) == 1 and len(email_cc) == 0 and len(email_bcc) == 0:
        	direct = 1
        combined_list = list(itertools.chain(email_to, email_cc, email_bcc))
        for email_to_1 in combined_list:
            received_emails.append({"msg_id": email['Message-ID'], 
                                  "recipient": email_to_1, 
                                 "date": str(parsedate_to_datetime(email['date'])).split(" ")[0],
                                 "direct": direct})
        
    clean_subject = email['subject']
    if email['subject']:
        subject_list = re.split('RE: |FW: |FWD: ',str(email['subject']))
        if len(subject_list) > 1:
            clean_subject = subject_list[1]

    dictionary = {"msg_id": email['Message-ID'], 
                  "date": parsedate_to_datetime(email['date']), 
                  "to_ppl": str(email_to), 
                  "direct": direct,
                  "from_ppl": email['from'], 
                  "cc_ppl": email['cc'], 
                  "subject": email['subject'], 
                  "clean_subject": clean_subject, 
                  "body": email.get_payload()}
    
    dictionary_email_list.append(dictionary)

dictionary_email_list = []
received_emails = []

# Iterate through each email txt file in enron_with_categories
for directory, subdirectory, filenames in  os.walk(rootdir):
    for filename in filenames:
        if filename != "categories.txt" and filename.endswith(".txt"):
            email_analyse(os.path.join(directory, filename), dictionary_email_list, received_emails)

mydb = mysql.connector.connect(host='localhost',
                               user='root', 
                               passwd='enronemail', 
                               database='testdb')

mycursor = mydb.cursor(buffered=True)

# Drop current table if exists
mycursor.execute("DROP TABLE IF EXISTS emails")
mycursor.execute("DROP TABLE IF EXISTS received_emails")

# Create two main tables: emails, received_emails
# emails: row per email(msg_id)
# received_emails: row per recipient 
mycursor.execute("CREATE TABLE emails (msg_id TEXT(65535), date TEXT(65535), to_ppl TEXT(65535), direct INT(255), from_ppl TEXT(65535), cc_ppl TEXT(65535), subject TEXT(65535), clean_subject TEXT(65535), body TEXT(65535))")
mycursor.execute("CREATE TABLE received_emails (msg_id TEXT(65535), recipient TEXT(65535), date TEXT(65535), direct INT(255))")

sql1 = "INSERT INTO emails (msg_id, date, to_ppl, direct, from_ppl, cc_ppl, subject, clean_subject, body) VALUES (%(msg_id)s, %(date)s, %(to_ppl)s, %(direct)s, %(from_ppl)s, %(cc_ppl)s, %(subject)s, %(clean_subject)s, %(body)s)"
sql2 = "INSERT INTO received_emails (msg_id, recipient, date, direct) VALUES (%(msg_id)s, %(recipient)s, %(date)s, %(direct)s)"
mycursor.executemany(sql1, dictionary_email_list)
mycursor.executemany(sql2, received_emails)

# Function to save output as CSV
def output_to_csv(output_data, tbl_header, output_csv):
	with open(output_csv, 'w', newline='') as f_handle:
		writer = csv.writer(f_handle)
		# Add the header/column names
		writer.writerow(tbl_header)
		# Iterate over `output_data`  and  write to the csv file
		for row in output_data:
			writer.writerow(row)

# How many emails did each person receive each day? (Assignment #1)
question1_sql = """SELECT COUNT(msg_id) as count, recipient, date
FROM received_emails
GROUP BY date, recipient 
ORDER BY date DESC"""
mycursor.execute(question1_sql)

# Save output as CSV
q1_data = mycursor.fetchall()
q1_header = ['count', 'recipient', 'date']
output_to_csv(q1_data, q1_header, 'Question1.csv')

# Identify the person (or people) who received the largest number of direct emails (Assignment #2)
question2a_sql = """SELECT recipient, MAX(s1.count) AS max_count
FROM (SELECT recipient, COUNT(msg_id) as count
FROM received_emails
WHERE direct = 1
GROUP BY recipient
ORDER BY COUNT(msg_id) DESC
LIMIT 1) s1
GROUP BY recipient"""
mycursor.execute(question2a_sql)

# Save output as CSV
q2a_data = mycursor.fetchall()
q2a_header = ['recipient', 'count']
output_to_csv(q2a_data, q2a_header, 'Question2a.csv')

# Identify the person (or people) who sent the largest number of broadcast emails (Asssignment #2)
question2b_sql = """SELECT from_ppl, MAX(s1.count) AS max_count
FROM (SELECT from_ppl, COUNT(msg_id) as count
FROM email
WHERE direct = 0
GROUP BY from_ppl
ORDER BY COUNT(msg_id) DESC
LIMIT 1) s1
GROUP BY from_ppl"""
mycursor.execute(question2b_sql)

# Save output as CSV
q2b_data = mycursor.fetchall()
q2b_header = ['from_ppl', 'count']
output_to_csv(q2b_data, q2b_header, 'Question2b.csv')

# Find the five emails with the fastest response times. (Assignment #3)
question3_sql = """SELECT MIN(TIME_TO_SEC(TIMEDIFF(e1.date, e2.date))) as time_diff, MIN(e2.date) as first_date, MIN(e1.date) as second_date, MIN(e1.subject) as subject, MIN(e1.from_ppl) as first_sender, MIN(e2.from_ppl) as second_sender
FROM emails as e1, emails as e2 
WHERE (e1.clean_subject = e2.clean_subject) 
AND (TIME_TO_SEC(TIMEDIFF(e1.date, e2.date)) > 0)
AND (LOCATE(e1.from_ppl, e2.to_ppl) > 0)
AND (e1.from_ppl != e2.from_ppl)
GROUP BY e1.msg_id
ORDER BY time_diff
LIMIT 5"""
mycursor.execute(question3_sql)

# Save output as CSV
q3_data = mycursor.fetchall()
q3_header = ['time_diff', 'first_date', 'second_date', 'subject', 'first_sender', 'second_sender']
output_to_csv(q3_data, q3_header, 'Question3.csv')

mydb.commit()
