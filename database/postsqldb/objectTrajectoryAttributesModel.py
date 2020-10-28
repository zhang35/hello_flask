# -*- coding: utf-8 -*-
# @Author  : zhang35
# @Time    : 2020/10/15 14:25
# @Function:
from database.postsqldb.db import db
from datetime import datetime
from geoalchemy2.types import Geometry
from flask_restful import fields
from geoalchemy2.elements import WKTElement
from random import random
class ObjectTrajectoryAttributesModel(db.Model):
    __tablename__ = 'objecttrajectoryattributes'

    lastappeared_id = db.Column(db.Integer, db.ForeignKey('objecttrajactory.lastappeared_id', ondelete='CASCADE'), primary_key=True)
    machine_type = db.Column(db.String(), nullable=False, default=0)
    average_speed = db.Column(db.Float(), nullable=False, default=0)
    max_speed = db.Column(db.Float(), nullable=False, default=0)
    max_accerate_speed = db.Column(db.Float(), nullable=False, default=0)
    turn_degree = db.Column(db.Float(), nullable=False, default=0)
    lastmodified_time = db.Column(db.DateTime, nullable=False)

    def dictRepr(self):
        info = {
            "lastappeared_id ": self.lastappeared_id,
            "machine_type ": self.machine_type,
            "average_speed": self.average_speed,
            "max_speed": self.max_speed,
            "max_accerate_speed": self.max_accerate_speed,
            "turn_degree": self.turn_degree,
            "lastmodified_time": self.lastmodified_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return info
