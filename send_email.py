import yagmail

def send_mail(receiver, body, filename):
    """
    Yagmail is for Gmail only!
    ---
    EXAMPLE OF ARGUMENTS:
    receiver = "your@gmail.com"
    body = "Hello there from Yagmail"
    filename = "document.pdf"
    ---
    """

    yag = yagmail.SMTP(receiver)
    yag.send(
        to=receiver,
        subject="INTRUDER ALERT",
        contents=body, 
        attachments=filename,
    )