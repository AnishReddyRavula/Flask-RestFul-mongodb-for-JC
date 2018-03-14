from mongoengine import *
import datetime

connect("justchange")

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

class Users(DynamicDocument):
	meta = {
			'collection' : 'users'
	}
	account_type = StringField(max_length=50, default="user")
	dob = DateTimeField()

class InternshipAttendance(Document):
	intern_details = ReferenceField(Users, dbref = True)
	log_in = DateTimeField()
	log_out = DateTimeField()
	status = StringField(max_length = 100)
	hours_worked = FloatField(precision = 2)
	days_worked = IntField()

class InternStatus(Document):
	intern_details = ReferenceField(Users, dbref = True)
	points = IntField()
	status = StringField(max_length = 20)
	certificate_status = BooleanField(default = False)



class subCategories(DynamicDocument):
	meta = {
			'collection' : 'subCategories'
	}




class categories(DynamicDocument):
	meta = {
			'collection' : 'categories'
	}


class NGOs(DynamicDocument):
	meta = {
			'collection' : 'NGOs'
	}
	category = ReferenceField(categories, dbref = True)
	donationCategories = ListField(ReferenceField(subCategories, dbref = True))
	ngoCategories = ListField(ReferenceField(subCategories, dbref = True))

class internships(DynamicDocument):
	meta = {
		'collection': 'internships'
	}

class internshipMappers(DynamicDocument):
	meta = {
		'collection': 'internshipMappers'
	}
	internship = ReferenceField(internships, dbref=True)
	intern_details = ReferenceField(Users, dbref=True)
	mentor = ReferenceField(Users, dbref=True)

class Funding(Document):
	pass