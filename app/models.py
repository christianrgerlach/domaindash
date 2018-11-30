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
	domain_ssl_issuer_cn = CharField()
	domain_ssl_expiry_date = DateField()
	domain_ssl_expiry_health = BooleanField()
	domain_mxtoolbox_health = BooleanField(null = True)

class MXToolboxBatch(BaseModel):
	run_time = DateTimeField()
	domain = ForeignKeyField(Domain, backref = 'mxtoolbox_batches', null = True)

class MXToolboxReport(BaseModel):
	batch = ForeignKeyField(MXToolboxBatch, backref = 'mxtoolbox_reports', null = True)
	domain = ForeignKeyField(Domain, backref = 'mxtoolbox_reports', null = True)
	check_time = DateTimeField()
	command = CharField()
	response = TextField()