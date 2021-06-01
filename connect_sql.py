import os
from email.parser import Parser
from email.utils import parsedate_to_datetime
import mysql.connector
import datetime
import time
import re
import csv

rootdir = "./enron_with_categories"

# Function to parse an email file, extract fields 
def email_analyse(inputfile, dictionary_email_list, to_email_dict):
    with open(inputfile, "r") as f:
        data = f.read()
 
    email = Parser().parsestr(data)
    if email['to']:
        email_to = email['to']
        email_to = email_to.replace("\n", "").replace("\t", "").replace(" ", "").split(",")
        for email_to_1 in email_to:
            received_emails.append({"msg_id": email['Message-ID'], 
                                  "recipient": email_to_1, 
                                 "date": str(parsedate_to_datetime(email['date'])).split(" ")[0],
                                 "direct": int(len(email_to) == 1)})
    else: 
        email_to = []
        
    clean_subject = email['subject']
    if email['subject']:
        subject_list = re.split('RE: |FW: |FWD: ',str(email['subject']))
        if len(subject_list) > 1:
            clean_subject = subject_list[1]

    dictionary = {"msg_id": email['Message-ID'], 
                  "date": parsedate_to_datetime(email['date']), 
                  "to_ppl": str(email_to), 
                  "direct": int(len(email_to) == 1),
                  "from_ppl": email['from'], 
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
mycursor.execute("CREATE TABLE emails (msg_id TEXT(65535), date TEXT(65535), to_ppl TEXT(65535), direct INT(255), from_ppl TEXT(65535), subject TEXT(65535), clean_subject TEXT(65535), body TEXT(65535))")
mycursor.execute("CREATE TABLE received_emails (msg_id TEXT(65535), recipient TEXT(65535), date TEXT(65535), direct INT(255))")

sql1 = "INSERT INTO emails (msg_id, date, to_ppl, direct, from_ppl, subject, clean_subject, body) VALUES (%(msg_id)s, %(date)s, %(to_ppl)s, %(direct)s, %(from_ppl)s, %(subject)s, %(clean_subject)s, %(body)s)"
sql2 = "INSERT INTO received_emails (msg_id, recipient, date, direct) VALUES (%(msg_id)s, %(recipient)s, %(date)s, %(direct)s)"
mycursor.executemany(sql1, dictionary_email_list)
mycursor.executemany(sql2, received_emails)

# question1_sql = """SELECT COUNT(msg_id), recipient, date
# INTO OUTFILE '/Results/TESTQ1s.csv'
# FIELDS TERMINATED BY ','
# ENCLOSED BY '"'
# LINES TERMINATED BY '\n'
# FROM received_emails
# GROUP BY date, recipient 
# ORDER BY date DESC"""

# How many emails did each person receive each day? (Assignment #1)
question1_sql = """SELECT COUNT(msg_id) as count, recipient, date
FROM received_emails
GROUP BY date, recipient 
ORDER BY date DESC"""
mycursor.execute(question1_sql)

# Save outputt as CSV
q1_data = mycursor.fetchall()
with open('Question1.csv', 'w', newline='') as f_handle:
    writer = csv.writer(f_handle)
    # Add the header/column names
    header = ['count', 'recipient', 'date']
    writer.writerow(header)
    # Iterate over `data`  and  write to the csv file
    for row in q1_data:
        writer.writerow(row)

# Identify the person (or people) who received the largest number of direct emails (Assignment #2)
question2a_sql = """SELECT COUNT(msg_id) as count, recipient
FROM received_emails
WHERE direct = 1
GROUP BY direct, recipient
ORDER BY COUNT(msg_id) DESC
LIMIT 1"""
mycursor.execute(question2a_sql)

# Save outputt as CSV
q2a_data = mycursor.fetchall()
with open('Question2a.csv', 'w', newline='') as f_handle:
    writer = csv.writer(f_handle)
    # Add the header/column names
    header = ['count', 'recipient']
    writer.writerow(header)
    # Iterate over `data`  and  write to the csv file
    for row in q2a_data:
        writer.writerow(row)

# Identify the person (or people) who sent the largest number of broadcast emails (Asssignment #2)
question2b_sql = """SELECT COUNT(msg_id), from_ppl
FROM emails
WHERE direct = 0
GROUP BY direct, from_ppl
ORDER BY COUNT(msg_id) DESC
LIMIT 1"""
mycursor.execute(question2b_sql)

# Save output as CSV
q2b_data = mycursor.fetchall()
with open('Question2b.csv', 'w', newline='') as f_handle:
    writer = csv.writer(f_handle)
    # Add the header/column names
    header = ['count', 'recipient']
    writer.writerow(header)
    # Iterate over `data`  and  write to the csv file
    for row in q2b_data:
        writer.writerow(row)

# Find the five emails with the fastest response times. (Assignment #3)
question3_sql = """SELECT MIN(TIME_TO_SEC(TIMEDIFF(e1.date, e2.date))) as time_diff, MIN(e2.date) as first_date, MIN(e1.date) as second_date, MIN(e1.subject) as subject, MIN(e1.from_ppl) as first_sender, MIN(e2.from_ppl) as second_sender
FROM emails as e1, emails as e2 
WHERE (e1.clean_subject = e2.clean_subject) 
AND (TIME_TO_SEC(TIMEDIFF(e1.date, e2.date)) > 0)
AND (LOCATE(e1.from_ppl, e2.to_ppl) > 0)
AND (e1.from_ppl != e2.from_ppl)
AND (e1.clean_subject != '')
GROUP BY e1.msg_id
ORDER BY time_diff
LIMIT 5"""
mycursor.execute(question3_sql)

# Save outputt as CSV
q3_data = mycursor.fetchall()
with open('Question3.csv', 'w', newline='') as f_handle:
    writer = csv.writer(f_handle)
    # Add the header/column names
    header = ['time_diff', 'first_date', 'second_date', 'subject', 'first_sender', 'second_sender']
    writer.writerow(header)
    # Iterate over `data`  and  write to the csv file
    for row in q3_data:
        writer.writerow(row)


mydb.commit()
