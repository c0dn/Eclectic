from send_mail import Mail

m1 = Mail("info")
m1.content = "Test message"
m1.subject = "Test"
m1.send("boxixe5211@mailboxt.net")