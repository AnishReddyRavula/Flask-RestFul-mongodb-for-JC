from mongoengine import *
import datetime.datetime
# this will be inside other fields
class Name(EmbeddedDocument):
	first_name = StringField(max_length = 200)
	last_name = StringField(max_length = 200)


class Adminuser(Document):
	name = EmbeddedDocumentField(Name)
	username = StringField(max_length=200, required=True)
	password = StringField(max_length = 100, min_length = 6)
	
class Ngouser(Document):
	name = EmbeddedDocumentField(Name)
	username = StringField(max_length=200, required=True)
	password = StringField(max_length = 100, min_length = 6)
	ngo =  StringField(max_length=200)


class Details(Document):
	name = StringField(max_length=200)
	email = EmailField()
	phone = StringField(max_length=20)
	Address= StringField(max_length=300)

class Contact(Document):
	basic_details = EmbeddedDocumentField(Details)
	registered_address = StringField(max_length=300)

class InternshipAttendance(Document):
	intern_details = ReferenceField()
	log_in = DateTimeField(default = datetime.now())
	log_out = DateTimeField(default = datetime.now())
	status = StringField(max_length = 100)
	hours_worked = FloatField(precision = 2)
	days_worked = IntField()

class InternStatus(Document):
	intern_details = ReferenceField(dbref = True)
	points = IntField()
	status = StringField(max_length = 20)
	certificate_status = BooleanField(default = False)


class Ngo(Document):
	pass


class Funding(Document):
	pass