# -*- coding: utf-8 -*-
import datetime as dt
import json

from flask.ext.login import UserMixin

from extractor_train.extensions import bcrypt
from extractor_train.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)


# class Role(SurrogatePK, Model):
#     __tablename__ = 'roles'
#     name = Column(db.String(80), unique=True, nullable=False)
#     user_id = ReferenceCol('users', nullable=True)
#     user = relationship('User', backref='roles')

#     def __init__(self, name, **kwargs):
#         db.Model.__init__(self, name=name, **kwargs)

#     def __repr__(self):
#         return '<Role({name})>'.format(name=self.name)

class Dlannotations( Model):

    __tablename__ = 'dlannotations'
#    dlannotationname = Column(db.String(80), unique=True, nullable=False)
    downloads_id = Column(db.Integer(), unique=True,  primary_key=True, nullable=False)
    annotations_json = Column(db.Text( convert_unicode=True),  nullable=False)
    #: The hashed password
    # password = Column(db.String(128), nullable=True)
    # created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    # first_name = Column(db.String(30), nullable=True)
    # last_name = Column(db.String(30), nullable=True)
    # active = Column(db.Boolean(), default=False)
    # is_admin = Column(db.Boolean(), default=False)

    def __init__(self, downloads_id, annotations_json, **kwargs):
        db.Model.__init__(self, downloads_id=downloads_id, annotations_json=annotations_json, **kwargs)
    #     if password:
    #         self.set_password(password)
    #     else:
    #         self.password = None

    # def set_password(self, password):
    #     self.password = bcrypt.generate_password_hash(password)

    # def check_password(self, value):
    #     return bcrypt.check_password_hash(self.password, value)

    @property
    def annotations(self):
        return json.loads( self.annotations_json )

    def __repr__(self):
        return '<Dlannotation({downloads_id!r})>'.format(downloads_id=self.downloads_id)
