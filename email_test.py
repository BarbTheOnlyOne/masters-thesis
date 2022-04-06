import send_email
import os

receiver = "michal.barborik96@gmail.com"
body = "Alert! The secured spaces has been compromised!"
filename = "test.pdf"
file_path = "D:\\Programování\\masters-thesis"
attachment = os.path.join(file_path, filename)

send_email.send_mail(receiver, body, attachment)
