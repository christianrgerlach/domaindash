from peewee import *
from app import db

class BaseModel(Model):
    class Meta:
        database = db

class Domain(BaseModel):
	domain_check_time = DateTimeField()
	domain_name = CharField()
	domain_health = BooleanField()
	domain_registration_expiry_date = DateField()
	domain_registration_expiry_health = BooleanField()
	domain_ssl_expiry_date = DateField()
	domain_ssl_expiry_health = BooleanField()

class MXToolboxReport(BaseModel):
	domain = ForeignKeyField(Domain, backref = 'mx_toolbox_reports', null = True)
	mxtoolbox_check_time = DateTimeField
	command = CharField()
	response = TextField()
	domain_mx_toolbox_health = BooleanField()
