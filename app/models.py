from peewee import *
from app import db

class BaseModel(Model):
    class Meta:
        database = db

class MXToolboxApiQueryBatch(BaseModel):
	count = IntegerField()
	datetime = DateTimeField()

class Domain(BaseModel):
	domain_name = CharField()
	domain_health = BooleanField()
	domain_registration_expiry_date = DateField()
	domain_registration_expiry_health = BooleanField()
	domain_ssl_expiry_date = DateField()
	domain_ssl_expiry_health = BooleanField()

class MXToolboxReport(BaseModel):
	domain = ForeignKeyField(Domain, backref = 'mx_toolbox_reports')
	mx_toolbox_api_query_batch = ForeignKeyField(Domain, backref = 'mx_toolbox_reports', null = True)
	command = CharField()
	response = TextField()
	domain_mx_toolbox_health = BooleanField()
