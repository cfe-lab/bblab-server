## Checked for 3.7 ##

import smtplib, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# This function creates a new file object. (email encoded)
def create_file(filename, filetype, filecontent):
	'''filetype is the end string without a period, ex. for "index.html", filetype is 'html'.
		filename is without the filetype at the end.'''

	# Create a text file.
	part = MIMEBase('application', "octet-stream")
	part.set_payload(filecontent)  # This is the text in the file.
	encoders.encode_base64(part)

	part.add_header( 'Content-Disposition', 'attachment; filename="{}.{}"'.format(filename, filetype) )

	return part


# This function sends an email from an sfu email.
# attachment_list is a list of the attachment class.  -1 means no attachments. attachment_list must be a list.
# For cc email, if -1 then none, else it holds the addresses to cc. (list)
def send_sfu_email(sender_name, reciever_email, subject_text, body_text, attachment_list=-1, cc_list=-1):
	'''this function sends an email from an sfu email.
		attachment_list is a list of the attachment class.  -1 means no attachments. attachment_list must be a list.'''
	
	### construct the message and sending information.
	sender = "{}@bccfe.ca".format(sender_name)
	#sender = "{}@sfu.ca".format(sender_name)
	reciever = reciever_email

	msg = MIMEMultipart()
	msg.attach(MIMEText(body_text))  # attach the text to the email.
	msg['Subject'] = subject_text
	msg['From'] = sender
	msg['To'] = reciever

	### attach a file if there are any.
	if attachment_list != -1:
		for attachment in attachment_list:
			msg.attach(attachment)

	send_to = reciever

	### cc the people if need be.
	if cc_list != -1:
		ccs = ", ".join(cc_list)  # people to cc to.
		msg['Cc'] = ccs
		send_to = [reciever, ccs]  # send the email to the cced people too.

	### attempt to send the email.
	try:
		### for some reason the newer smtp server thinks we aren't part of sfu
		### so we have to use the old smtp server. -> if emails stop working this is 
		### very likely the case.
		#smtpobj = smtplib.smtp("mailgate.sfu.ca", 0)
		#smtpobj = smtplib.SMTP("smtpserver.sfu.ca", 25)
		smtpobj = smtplib.SMTP("mail.bccfe.ca",25)
		smtpobj.sendmail(sender, send_to, msg.as_string())
		return 0
	except Exception as e:
		print ( "Error: unable to send email. \nerror: {}".format(e), file=sys.stderr )
		return 1


### EXAMPLE CODE ###
'''
txt_file = create_file("great_filename", 'txt', "This is just some text in a file.")
msg_body = "This is the body of the email.  There is some text here.  There is also an attached file."
if send_sfu_email("test_email_name", "reciever@email.com", "You've Got Some Mail!", msg_body, [txt_file]) == 1:
	print "Error: unable to send email"
else:
	print "Successfully sent email"

'''
