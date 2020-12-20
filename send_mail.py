import requests


class Mail:
	def __init__(self):
		self.__api_key = "060fb4794fdcb1d93fab844678f5c4dc-1df6ec32-5f277f4e"
		self.__api_url = "https://api.mailgun.net/v3/mg.eclectic.best/messages"
		self.subject = None
		self.content = None

	def send(self, recipient):
		data = {"from": "Eclectic Support <support@eclectic.best>", "to": recipient}
		if self.subject is None:
			raise ValueError("No subject, aborting sending of mail.")
		else:
			data["subject"] = self.subject
		if self.content is None:
			raise ValueError("No message, aborting sending of mail")
		else:
			data["html"] = self.content
		r = requests.post(self.__api_url, auth=("api", self.__api_key), data=data)
		if r.status_code != 200:
			raise Exception("Error when sending mail, HTTP error: {}".format(r.status_code))