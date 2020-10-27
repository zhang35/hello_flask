from flask import request
from database.postsqldb.models import ObjectTrajactoryModel,ImportantRegion,LastappearedModel
from datetime import datetime, timedelta
from database.postsqldb.db import db
from sqlalchemy.sql import select, func
from flask_restful import Resource,  marshal_with
from database.postsqldb.models import neighborhood_fields,neighborhood_area_fields
from flask_restful import reqparse
from sqlalchemy import desc,asc

class ObjectTrajactoryApi(Resource):
  def get(self,id):
    objectTrajactory = ObjectTrajactoryModel.query.get(id)
    return objectTrajactory.dictRepr(),200

class ObjectTrajactoryAbnormalPositonApi(Resource):
  def get(self,id):
    objectTrajactory = ObjectTrajactoryModel.query.get(id)
    importantRegions = ImportantRegion.query.filter(func.ST_Intersects(ImportantRegion.geom,objectTrajactory.gps_line)).all()
    result = objectTrajactory.dictRepr()
    result["important_regions"] = [r.dictRepr() for r in  importantRegions]
    return result,200

class ObjectTrajactoryPredictorFromSelfApi(Resource):
  """
  """
  def get(self,id):
    
    objectTrajactory = ObjectTrajactoryModel.query.get(id)
    
    sub = LastappearedModel.query.filter_by(object_id=objectTrajactory.lastappeared.object_id).subquery()
    row = ObjectTrajactoryModel.query.join(sub,sub.c.id == ObjectTrajactoryModel.lastappeared_id).filter(ObjectTrajactoryModel.lastappeared_id!=id).with_entities(ObjectTrajactoryModel,func.ST_FrechetDistance(ObjectTrajactoryModel.gps_line,func.ST_AsEWKT(objectTrajactory.gps_line)).label('similar')).order_by(asc('similar')).first()

    if row is None:
      return "没有该目标的历史轨迹，无法预测"
    else:
      r,s = row
      return r.dictRepr(similar=1.0/(s+1))
class ObjectTrajactoryPredictorFromAllApi(Resource):
  def get(self,id):
    
    objectTrajactory = ObjectTrajactoryModel.query.get(id)
    
    row = ObjectTrajactoryModel.query.filter(ObjectTrajactoryModel.lastappeared_id!=id).with_entities(ObjectTrajactoryModel,func.ST_FrechetDistance(ObjectTrajactoryModel.gps_line,func.ST_AsEWKT(objectTrajactory.gps_line)).label('similar')).order_by(asc('similar')).first()

    if row is None:
      return "没有用于预测的历史轨迹"
    else:
      r,s = row
      return r.dictRepr(similar=1.0/(s+1))

class ObjectTrajactorysApi(Resource):
  
  def get(self):
    return  [row.dictRepr() for row in ObjectTrajactoryModel.query.all()]



class SimilarObjectTrajactorysApi(Resource):
  from sqlalchemy import desc,asc

  def get(self,id):
    parser = reqparse.RequestParser()

    parser.add_argument('similar_num',type=int)

    args = parser.parse_args()
    similar_num = 10 if args['similar_num'] is None else args['similar_num']
    objectTrajactory = ObjectTrajactoryModel.query.get(id)
    rows = ObjectTrajactoryModel.query.filter(ObjectTrajactoryModel.lastappeared_id!=id).with_entities(ObjectTrajactoryModel,func.ST_HausdorffDistance(ObjectTrajactoryModel.gps_line,func.ST_AsEWKT(objectTrajactory.gps_line)).label('similar')).order_by(asc('similar')).limit(similar_num).all()
    return  [o.dictRepr(similar=1.0/(s+1)) for o,s in rows]



class ObjectTrajectoryLastNminutesApi(Resource):
  def get(self, minutes):
    t = datetime(2020, 10, 16, 16, 20, 0)
    # t = datetime.now()
    requiredTime = (t - timedelta(minutes=minutes))
    query = ObjectTrajactoryModel.query.filter(
      ObjectTrajactoryModel.gps_line.ST_EndPoint().ST_M() >= requiredTime.timestamp()).all()
    return [row.dictRepr() for row in query]
