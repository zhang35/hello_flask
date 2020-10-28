# -*- coding: utf-8 -*-
# @Author  : zhang35
# @Time    : 2020/10/27 15:03
# @Function: get machine_type, avg_speed, max_speed, max_acc_speed, turn_radius of a trajectory

from flask_restful import Resource
from database.postsqldb.db import db
from database.postsqldb.models import ObjectTrajactoryModel
from database.postsqldb.objectTrajectoryAttributesModel import ObjectTrajectoryAttributesModel
from algorithms.attributesCalculation import calculateAttributes
class ObjecttrajectoryattributesApi(Resource):
    def get(self, lastappeared_id):
        objectTrajactory = ObjectTrajactoryModel.query.get(lastappeared_id)
        lastmodified_time = objectTrajactory.lastmodified_time()

        objectTrajectoryAttrModel = ObjectTrajectoryAttributesModel.query.filter(ObjectTrajectoryAttributesModel.lastappeared_id==lastappeared_id,
                                                             ObjectTrajectoryAttributesModel.lastmodified_time==lastmodified_time).first()
        # 若未找到lastappeared_id 和 lastmodified_time 均匹配的记录
        if not objectTrajectoryAttrModel:
            # 删除lastappeared_id的现有记录
            existingModel = ObjectTrajectoryAttributesModel.query.get(lastappeared_id)
            print("db.session.delete: ", existingModel .dictRepr())
            db.session.delete(existingModel)
            # 计算并新增记录
            attr = calculateAttributes(objectTrajactory.gps_line)
            attr["lastappeared_id"] = lastappeared_id
            attr["lastmodified_time"] = lastmodified_time
            model = ObjectTrajectoryAttributesModel(**attr)
            db.session.add(model)
            print("db.session.add: ", attr)
            db.session.commit()
            objectTrajectoryAttrModel = ObjectTrajectoryAttributesModel.query.get(lastappeared_id)
        return objectTrajectoryAttrModel.dictRepr()