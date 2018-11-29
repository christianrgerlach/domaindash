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

class MXToolboxReport(BaseModel):
	domain = ForeignKeyField(Domain, backref = 'mxtoolbox_reports', null = True)
	command = CharField()
	response = TextField()

class MXToolboxBatch(BaseModel):
	mxtoolbox_batch_time = DateTimeField()
	domain = ForeignKeyField(Domain, backref = 'mxtoolbox_batch', null = True)
	report = ForeignKeyField(MXToolboxReport, backref = 'mxtoolbox_batch', null = True)