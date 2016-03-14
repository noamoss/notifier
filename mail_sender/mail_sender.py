#!/bin/env python

import sendgrid


'''

client = sendgrid.SendGridClient("SENDGRID_APIKEY")
message = sendgrid.Mail()

message.add_to("test@sendgrid.com")
message.set_from("you@youremail.com")
message.set_subject("Sending with SendGrid is Fun")
message.set_html("and easy to do anywhere, even with Python")
 
 client.send(message)
 '''

def main():
    # TODO: setup an exception handler that print to the log


if '__main__' == __name__:
    main()
