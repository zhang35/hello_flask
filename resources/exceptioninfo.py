# -*- coding: utf-8 -*-
# @Author  : zhang35
# @Time    : 2020/10/15 14:14
# @Function: exceptioninfo table api

from flask import request
from database.postsqldb.exceptionInfoModel import ExceptionInfoModel
from database.postsqldb.models import ObjectTrajactoryModel
from database.postsqldb.db import db
from algorithms.exceptionDetection import getExcetpionInfo

from flask_restful import Resource, reqparse

def getGpsPointsWithinTimePeriod(lastappeared_id, start_time, end_time):
    objectTrajactory = ObjectTrajactoryModel.query.get(lastappeared_id)
    gpsPoints = objectTrajactory.gps_points()
    si = 0 # start_time index
    ei = 0 # end_time index
    for i in range(0, len(gpsPoints)):
        if gpsPoints[i]["occurtime"] == start_time:
            si = i
        if gpsPoints[i]["occurtime"] == end_time:
            ei = i
            break
    return gpsPoints[si : ei+1]

class ExceptionInfoApi(Resource):
    def get(self, lastappeared_id):
        objectTrajactory = ObjectTrajactoryModel.query.get(lastappeared_id)
        lastmodified_time = objectTrajactory.lastmodified_time()
        print(lastmodified_time)
        # 查询异常信息表
        exceptionInfoModel = ExceptionInfoModel.query.filter(ExceptionInfoModel.lastappeared_id==lastappeared_id,
                                                             ExceptionInfoModel.lastmodified_time==lastmodified_time).first()
        # 若未找到lastappeared_id 和 lastmodified_time 均匹配的记录
        if not exceptionInfoModel:
            # 删除lastappeared_id的所有记录
            existingModels = ExceptionInfoModel.query.filter(ExceptionInfoModel.lastappeared_id == lastappeared_id).all()
            for model in existingModels:
                print("db.session.delete: ", model.dictRepr())
                db.session.delete(model)
            # 计算并新增记录
            objectTrajactoryJson = objectTrajactory.dictRepr()
            exceptionInfoList = getExcetpionInfo(objectTrajectoryJson=objectTrajactoryJson, stayDistThres=0, stayTimeThres = 60, hoverDistThres = 10000, hoverTimeThres = 60)
            for exception in exceptionInfoList:
                exception["lastmodified_time"] = lastmodified_time
                model = ExceptionInfoModel(**exception)
                db.session.add(model)
                print("db.session.add: ", exception)
            db.session.commit()
        # 返回lastappeared_id 和 lastmodified_time 均匹配的记录
        exceptionInfoModel = ExceptionInfoModel.query.filter(ExceptionInfoModel.lastappeared_id==lastappeared_id,
                                                             ExceptionInfoModel.lastmodified_time==lastmodified_time).all()
        exceptionDetailList = []
        for row in exceptionInfoModel:
            exceptionDetail = {
                "id": row.id,
                "lastappeared_id ": row.lastappeared_id,
                "exception_type": row.exception_type,
                "reason": row.reason,
                "gps_points": getGpsPointsWithinTimePeriod(row.lastappeared_id, row.start_time.strftime("%Y-%m-%d %H:%M:%S"), row.end_time.strftime("%Y-%m-%d %H:%M:%S"))
            }
            exceptionDetailList.append(exceptionDetail )
        return exceptionDetailList
        # exceptionInfoList = [row.dictRepr() for row in exceptionInfoModel]
        # # 如果未查到，计算异常信息
        # if len(exceptionInfoList)==0:
        #
        # for exception in exceptionInfoList:
        #     exception_type = exception["exception_type"]
        #     start_time = exception["start_time"]
        #     end_time = exception["end_time"]
        #     reason = exception["reason"]
        #     gps_points = getGpsPointsWithinTimePeriod(start_time, end_time)
        #     exceptionDetailList.append({
        #         "lastappeared_id" : lastappeared_id,
        #         "exception_type": exception_type,
        #         "start_time": start_time,
        #         "end_time": end_time,
        #         "reason": reason,
        #         "gps_points": gps_points,
        #         "lastmodified_time": lastmodified_time})
        # rows = ExceptionInfoModel.query.filter_by(lastappeared_id=lastappeared_id)
        # return [row.dictRepr() for row in rows]
    def put(self, id):
        body = request.get_json()
        body["id"] = id
        exceptionInfo = ExceptionInfoModel(**body)
        db.session.add(exceptionInfo)
        db.session.commit()
        return {'id': exceptionInfo.id}
class ExceptionInfosApi(Resource):
    def get(self):
        rows = ExceptionInfoModel.query.all()
        return [row.dictRepr() for row in rows]

    # 更新object_id和start_time均相同的条目，若没有均相同的，则新建
    def put(self):
        body = request.get_json()
        for info in body:
            exceptionInfoModel = ExceptionInfoModel.query\
                .filter(ExceptionInfoModel.object_id==info["object_id"],
                        ExceptionInfoModel.start_time==info["start_time"])\
                .first()
            if exceptionInfoModel is None:
                exceptionInfoModel = ExceptionInfoModel(**info)
                db.session.add(exceptionInfoModel)
            else:
                exceptionInfoModel.update(info)
        db.session.commit()
        return str(len(body))+" items updated", 200