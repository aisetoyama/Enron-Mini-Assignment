import os
from email.parser import Parser
rootdir = "./enron_with_categories/1"


def email_analyse(inputfile, to_email_list, from_email_list, date_email_list, subject_email_list, email_body):
    with open(inputfile, "r") as f:
        data = f.read()
 
    email = Parser().parsestr(data)
    if email['to']:
        email_to = email['to']
        email_to = email_to.replace("\n", "").replace("\t", "").replace(" ", "").split(",")
        to_email_list.append(str(email_to))
#         for email_to_1 in email_to:
#             to_email_list.append(email_to_1)
    
    from_email_list.append(email['from'])
    date_email_list.append(email['date'])
    subject_email_list.append(email['subject'])
 
    email_body.append(email.get_payload())
    

to_email_list = []
from_email_list = []
date_email_list = []
subject_email_list = []
email_body = []



for directory, subdirectory, filenames in  os.walk(rootdir):
    for filename in filenames:
        email_analyse(os.path.join(directory, filename), to_email_list, from_email_list, date_email_list, subject_email_list, email_body)

with open("to_email_list.txt", "w") as f:
    for to_email in to_email_list:
        if to_email:
            f.write(to_email)
            f.write("\n")
            
with open("from_email_list.txt", "w") as f:
    for from_email in from_email_list:
        if from_email:
            f.write(from_email)
            f.write("\n")        

with open("date_email_list.txt", "w") as f:
    for date_email in date_email_list:
        if date_email:
            f.write(date_email)
            f.write("\n")   

with open("subject_email_list.txt", "w") as f:
    for subject_email in subject_email_list:
        if subject_email:
            f.write(subject_email)
            f.write("\n")   

with open("email_body.txt", "w") as f:
    for email_bod in email_body:
        if email_bod:
            f.write(email_bod)
            f.write("\n")     