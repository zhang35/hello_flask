# -*- coding: utf-8 -*-
# @Author  : zhang35
# @Time    : 2020/10/16 13:56
# @Function: extract stay points (implementation of algorithm in [2])

# References:
# [1] Q. Li, Y. Zheng, X. Xie, Y. Chen, W. Liu, and W.-Y. Ma, "Mining user similarity based on location history", in Proceedings of the 16th ACM SIGSPATIAL international conference on Advances in geographic information systems, New York, NY, USA, 2008, pp. 34:1--34:10.
# [2] Jing Yuan, Yu Zheng, Liuhang Zhang, XIng Xie, and Guangzhong Sun. 2011. Where to find my next passenger. In Proceedings of the 13th international conference on Ubiquitous computing (UbiComp '11). Association for Computing Machinery, New York, NY, USA, 109–118.

# test data could be downloaded from: https://www.microsoft.com/en-us/download/confirmation.aspx?id=52367

import time
from math import radians, cos, sin, asin, sqrt

time_format = '%Y-%m-%d %H:%M:%S'


# structure of point
class Point:
    def __init__(self, id, latitude, longitude, dateTime, arriveTime, leaveTime):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.dateTime = dateTime
        self.arriveTime = arriveTime
        self.leaveTime = leaveTime


# calculate distance between two points from their coordinate
def getDistanceOfPoints(pi, pj):
    lat1, lon1, lat2, lon2 = list(map(radians, [float(pi.latitude), float(pi.longitude),
                                                float(pj.latitude), float(pj.longitude)]))
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    m = 6371000 * c
    return m


# calculate time interval between two points
def getTimeIntervalOfPoints(pi, pj):
    t_i = time.mktime(time.strptime(pi.dateTime, time_format))
    t_j = time.mktime(time.strptime(pj.dateTime, time_format))
    return t_j - t_i


# compute mean coordinates of a group of points
def computMeanCoord(gpsPoints):
    lat = 0.0
    lon = 0.0
    for point in gpsPoints:
        lat += float(point.latitude)
        lon += float(point.longitude)
    return (lat / len(gpsPoints), lon / len(gpsPoints))


# extract stay points from a GPS log file
# input:
#        file: the name of a GPS log file
#        distThres: distance threshold
#        timeThres: time span threshold
# default values of distThres and timeThres are 200 m and 30 min respectively, according to [1]
def stayPointExtraction(points, distThres=200, timeThres=30 * 60):
    stayPointCenterList = []
    n = len(points)
    i = 0
    while i < n - 1:
        # j: index of the last point within distTres
        j = i + 1
        flag = False
        while j < n:
            if getDistanceOfPoints(points[i], points[j]) <= distThres:
                j += 1
            else:
                break

        j -= 1
        # at least one point found within distThres
        if j > i:
            # candidate cluster found
            if getTimeIntervalOfPoints(points[i], points[j]) > timeThres:
                nexti = i + 1
                j += 1
                while j < n:
                    if getDistanceOfPoints(points[nexti], points[j]) <= distThres and \
                            getTimeIntervalOfPoints(points[nexti], points[j]) > timeThres:
                        nexti += 1
                        j += 1
                    else:
                        break
                j -= 1
                id = points[i].id
                latitude, longitude = computMeanCoord(points[i: j + 1])
                arriveTime = time.mktime(time.strptime(points[i].dateTime, time_format))
                leaveTime = time.mktime(time.strptime(points[j].dateTime, time_format))
                dateTime = ""
                stayPointCenterList.append(Point(id, latitude, longitude, dateTime, arriveTime, leaveTime))
        i = j + 1
    return stayPointCenterList


def parseGpsPoints(id, gps_points):
    points = []
    for point in gps_points:
        latitude = point["lat"]
        longitude = point["long"]
        dateTime = point["occurtime"]
        points.append(Point(id, latitude, longitude, dateTime, 0, 0))
    return points


def getExcetpionInfo(objectTrajectoryJson, stayDistThres=0, stayTimeThres=10 * 60, hoverDistThres=5000,
                     hoverTimeThres=60):
    id = objectTrajectoryJson["id"]
    gps_points = objectTrajectoryJson["gps_points"]
    points = parseGpsPoints(id, gps_points)
    exceptionInfoList = []
    stayPointCenter = stayPointExtraction(points, stayDistThres, stayTimeThres)
    for sp in stayPointCenter:
        exceptionInfo = {
            "lastappeared_id": sp.id,
            "exception_type": "停留异常",
            "start_time": time.strftime(time_format, time.localtime(sp.arriveTime)),
            "end_time": time.strftime(time_format, time.localtime(sp.leaveTime)),
            "reason": "在[" + str(sp.longitude) + "," + str(sp.latitude) + "]点停留超过" + str(stayTimeThres) + "秒"
        }
        exceptionInfoList.append(exceptionInfo)
    hoverPointCenter = stayPointExtraction(points, hoverDistThres, hoverTimeThres)
    for sp in hoverPointCenter:
        exceptionInfo = {
            "lastappeared_id": sp.id,
            "exception_type": "盘旋异常",
            "start_time": time.strftime(time_format, time.localtime(sp.arriveTime)),
            "end_time": time.strftime(time_format, time.localtime(sp.leaveTime)),
            "reason": "在以[" + str(sp.longitude) + "," + str(sp.latitude) + "]为中心点的区域盘旋"
        }
        exceptionInfoList.append(exceptionInfo)
    return exceptionInfoList
