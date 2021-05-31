# Enron-Mini-Assignment

Enron, the infamous energy company that went bankrupt in the early 2000s after engaging in massive accounting fraud, was a heavy user of email. As part of the government's investigation into Enron's malfeasance, a large number of emails written by Enron's executive team was released to the public, and this corpus has since become a useful resource for computer scientists, computational linguists, and sociologists. In this exercise, we would like you to use this data to help us understand how people communicated with one another before Slack existed.
You will want to download an annotated sample of the Enron emails from UC Berkeley (4.5 MB, tar.gz), and you can find the entire data set and a collection of analyses/papers that have been written about it at the Carnegie Mellon site if you're interested. We'd like to answer the following questions about the email messages provided in the sample from Berkeley:
1. How many emails did each person receive each day? (Assignment #1)
2. Let's label an email as "direct" if there is exactly one recipient and "broadcast" if it has multiple recipients. Identify the person (or people) who received the largest number of direct emails and the person (or people) who sent the largest number of broadcast emails. (Assignment #2)
3. Find the five emails with the fastest response times. (A response is defined as a message from one of the recipients to the original sender whose subject line contains all of the words from the subject of the original email, and the response time should be measured as the difference between when the original email was sent and when the response was sent.). This is a bonus question. (Assignment #3)

## Results 
1. Question1.csv
2. Person who received the largest number of direct emails: 	maureen.mcvicker@enron.com, Question2a.csv
   Person who sent the largest number of broadcast emails:  steven.kean@enron.com
3. Question3.csv
	time_diff	first_date	second_date	subject	first_sender	second_sender
1	148	2001-11-21 08:48:57	2001-11-21 08:52:26	FW: Confidential - GSS Organization Value to ETS	stanley.horton@enron.com	rod.hayslett@enron.com
2	236	2001-10-26 08:51:41	2001-10-26 09:22:54	RE: CONFIDENTIAL Personnel issue	lizzette.palmer@enron.com	gina.corteselli@enron.com
3	240	2001-05-10 06:51:00	2001-05-10 06:55:00	RE: Eeegads...	jeff.dasovich@enron.com	paul.kaufman@enron.com
4	262	2001-07-30 11:17:48	2001-07-30 11:22:10	FW: SRP SETTLEMENT PROPOSAL - PRIVILEGED AND CONFIDENTIAL FOR
 SETTLEM	ENT DISCUSSIONS ONLY	stephanie.miller@enron.com	m..tholt@enron.com
5	322	2001-10-26 08:51:41	2001-10-26 09:18:58	RE: CONFIDENTIAL Personnel issue	michelle.cash@enron.com	gina.corteselli@enron.com
