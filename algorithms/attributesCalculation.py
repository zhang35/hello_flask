# -*- coding: utf-8 -*-
# @Author  : zhang35
# @Time    : 2020/10/27 16:41
# @Function: Calculate machine_type, avg_speed, max_speed, max_acc_speed, turn_radius of a trajectory
from geoalchemy2 import Geometry, WKBElement
from sqlalchemy.sql import func
import json

from geoalchemy2.functions import GenericFunction

def calculateAttributes(trajectory: WKBElement) -> json:
    attr = {}
    return attr
