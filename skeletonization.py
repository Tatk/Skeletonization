#!/usr/bin/env python
'''
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
'''
#import inkex
#import cubicsuperpath
#import simplepath
#from lxml import etree
#import copy,
import math
import re
import _random

p = [[[[154.79967, 876.14817], [154.79967, 876.14817], [154.79967, 876.14817]], [[32.314223999999996, 856.97301], [32.314223999999996, 856.97301], [32.314223999999996, 856.97301]], [[95.786357, 988.1309200000001], [95.786357, 988.1309200000001], [95.786357, 988.1309200000001]], [[148.57143, 915.21933], [148.57143, 915.21933], [148.57143, 915.21933]], [[185.71429, 978.07647], [185.71429, 978.07647], [185.71429, 978.07647]], [[191.42857, 889.50504], [191.42857, 889.50504], [191.42857, 889.50504]], [[288.57143, 900.93361], [288.57143, 900.93361], [288.57143, 900.93361]], [[184.16621000000004, 855.1549100000001], [184.16621000000004, 855.1549100000001], [184.16621000000004, 855.1549100000001]], [[140.99455000000003, 801.43969], [140.99455000000003, 801.43969], [140.99455000000003, 801.43969]], [[154.79967, 876.14817], [154.79967, 876.14817], [154.79967, 876.14817]]]]


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class GroupPoint(object):
    def __init__(self, point):
        self.p0 = point[0]
        self.p1 = point[1]
        self.p2 = point[2]
    
class Line(object):
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
    def dist_points(self):
        return math.sqrt((self.p0.x - self.p1.x) ** 2 + (self.p0.y - self.p1.y) ** 2)
    def paramOfLine(self):
        '''
         a = -(self.p1.y - self.p0.y) / distPoints(self)
         b = (self.p1.x - self.p0.x) / distPoints(self)
         c = (self.p1.y * self.p0.x - self.p0.y * self.p1.x) / distPoints(self)
         return [a,b,c]
        '''
        return [-(self.p1.y - self.p0.y) / distPoints(self),
                (self.p1.x - self.p0.x) / distPoints(self),
                (self.p1.y * self.p0.x - self.p0.y * self.p1.x) / distPoints(self)]



# получить список экземпляров класса Point
def getPoints(p):
    points = []
    for i in range(len(p)-1):
        points.append( Point(p[i][1][0],p[i][1][1]))
    return points

# получить список экземпляров класса GroupPoint 
def getGroupPoints(p):
    points = []
    group_points = []
    for i in range(len(p)):
        points.append([])
        for j in range(2):
            points[i].append( Point(p[i][j][0],p[i][j][1]))
        group_points.append( GroupPoint(points[i]))
    return group_points


# terminal point
# здесь передать в функцию getPoints(p), т.е. points - список экземпляров класса Point
# функция нахождения терминальной точки: минимальная по оси абсцисс, и если таких несколько, то и по оси ординат.
def termNode(points):
    minXi = min(points[0].x,points[1].x)
    for i in range(2, len(points)):
        minXi = min(minXi,points[i].x)
    temp = []
    for i in range(len(points)):
        if (points[i].x == minXi):
            temp.append(points[i])
    if (len(temp) != 1) :
        minYi = temp[0][1]
        for i in range(1,len(temp)) :
            minYi = min(minYi, temp[i][1])
        for i in range(len(temp)):
            if (minYi == temp[i][1]):
                return temp[i]
    else :
        return temp[0]
        
#  the direction of traversal of a path
# направление обхода контура: True, если ппротив часовой стрелки, т.е. векторное произведение > 0
def traversePath(p0, p1, p2):
    if ((p1.x - p0.x)*(p2.y - p1.y) < (p1.y - p0.y)*(p2.x - p1.x)):
        return True
    else: return False

# получить список экземпляров класса Line в порядке обхода против часовой стрелки
# здесь передать в функцию getPoints(p), т.е. points - список экземпляров класса Point
def getLines(points):

    points.append(points[0])
    lines = []
    n = int(len(points) - 1)

    for i in range(n):
        if (termNode(points) in [points[i]]):
            if i==0 :
                if  not traversePath(points[n-1],points[i],points[i+1]):
                    points.reverse()

                lines.append( Line(points[n-1],points[i]))
                for j in range(1, n):
                    lines.append( Line(points[i-1],points[i]))
                return lines
            else:
                if  not traversePath(points[i-1],points[i],points[i+1]):
                    points.reverse()
                    i = n-i

                for j in range(i, n+1):
                    lines.append( Line(points[i-1],points[i]))
                for k in range(1,i):
                    lines.append( Line(points[i-1],points[i]))
                return lines

# lines = getLines(getPoints(p))
def getBypassPoints(lines):
    points = []
    for i in range(len(lines)):
        points.append(lines[i].p0)
    return points

# function returns concave angles
# points = getBypassPoints(getLines(getPoints(p)))
def concaveNodes(points):
    concaveList = []
    n = len(points)-1
    termLines = traversePath(points[0], points[1], points[2])
    for i in range(2,n):
        tempTermLines = traversePath(points[i-1], points[i], points[i+1])
        if termLines * tempTermLines < 0:
            concaveList.append(points[i])
    tempTermLines = traversePath(points[n-1], points[n], points[0])  
    if termLines * tempTermLines < 0:
        concaveList.append(points[n])
    return concaveList   

##############################################################################
# Parametrization to find centre of circle in case circle tangents to 3 points
#or 3 lines
##############################################################################

def paramOf3Points(p0, p1, p2):
    '''
     A0 = 2 * (p1.x - p0.x)
     A1 = 2 * (p1.y - p0.y)
     A2 = -(p1.x ** 2 - p0.x ** 2 + p1.y ** 2 - p0.y ** 2)
     B0 = 2 * (p2.x - p0.x)
     B1 = 2 * (p2.y - p0.y)
     B2 = -(p2.x ** 2 - p0.x ** 2 + p2.y ** 2 - p0.y ** 2)]
     A = [A0,A1,A2]
     B = [B0, B1, B2]
     return [[A, B]]
    '''
    return [[[2 * (p1.x - p0.x), 2 * (p1.y - p0.y), -(p1.x ** 2 - p0.x ** 2 + p1.y ** 2 - p0.y ** 2)],
             [2 * (p2.x - p0.x), 2 * (p2.y - p0.y), -(p2.x ** 2 - p0.x ** 2 + p2.y ** 2 - p0.y ** 2)]]]

def paramOf3Line(A0, A1, A2):
    # Ai = [ai,bi,ci] - the coefficients of line
    return [
            [[A1[0] - A0[0], A1[1] - A0[1], (A1[2] - A0[2])],
             [A2[0] + A0[0], A2[1] + A0[1], (A2[2] + A0[2])]],
            [[A1[0] + A0[0], A1[1] + A0[1], (A1[2] + A0[2])],
             [A2[0] - A0[0], A2[1] - A0[1], (A2[2] - A0[2])]],
            [[A1[0] - A0[0], A1[1] - A0[1], (A1[2] - A0[2])],
             [A2[0] - A0[0], A2[1] - A0[1], (A2[2] - A0[2])]],
            [[A1[0] + A0[0], A1[1] + A0[1], (A1[2] + A0[2])],
             [A2[0] + A0[0], A2[1] + A0[1], (A2[2] + A0[2])]]
             ]

def paramOf3Lines(A0, A1, A2):
    
    if not math.fabs((A1[0] - A0[0]) * (A2[1] - A0[1]) - (A2[0] - A0[0]) * (A1[1] - A0[1])) < 0.000001: #lines non-parallel
        return paramOf3Line(A0,A1,A2)
    elif not math.fabs((A2[0] - A0[0]) * (A2[1] - A1[1]) - (A2[0] - A1[0]) * (A2[1] - A0[1])) < 0.000001:
        return paramOf3Line(A2,A0,A1)
    else:
        return paramOf3Line(A1,A0,A2)

# return centre in case circle tangents to 3 points or 3 lines
def centreOfFirstCase(A):
    # if 3 lines
    if len(A) != 1: 
        temp = []
        for i in range(len(A)):
            if not (math.fabs(A[i][0][0]) < 0.000001 or  
                    math.fabs(A[i][0][0]*A[i][1][1] - A[i][0][1]*A[i][1][0]) < 0.000001) :
                Yc = (-(A[i][0][0] * A[i][1][2] - A[i][1][0] * A[i][0][2]) /
                      (A[i][0][0] * A[i][1][1] - A[i][0][1] * A[i][1][0]))
                temp.append([-A[i][0][2] / A[i][0][0] - A[i][0][1] * Yc / A[i][0][0], Yc])
            if (math.fabs(A[i][0][0]) < 0.000001 and 
                not math.fabs(A[i][0][0]*A[i][1][1] - A[i][0][1]*A[i][1][0]) < 0.000001):
                Yc1 = -A[i][0][2] / A[i][0][1]
                temp.append([-A[i][1][2] / A[i][1][0] - A[i][1][0] / A[i][1][0] * Yc1, Yc1])
        return temp
    # if 3 points
    else:
        if not (math.fabs(A[0][0][0]) < 0.000001 or  math.fabs(A[0][1][0]) < 0.000001):
            Yc = -((A[0][0][0] * A[0][1][2] - A[0][1][0] * A[0][0][2]) / 
                   (A[0][0][0] * A[0][1][1] - A[0][0][1] * A[0][1][0]))
            return [-A[0][0][2] / A[0][0][0] - A[0][0][1] * Yc / A[0][0][0], Yc]
        elif not (math.fabs(A[0][0][1]) < 0.000001 or math.fabs(A[0][1][0]) < 0.000001): 
            Yc = -A[0][0][2] / A[0][0][1]
            return [-A[0][1][2] / A[0][1][0] - A[0][1][0] / A[0][1][0] * Yc, Yc]
        else:
            if not (math.fabs(A[0][1][1]) < 0.000001 or math.fabs(A[0][0][0]) < 0.000001): 
                Yc = -A[0][1][2] / A[0][1][1]
                return [-A[0][0][2] / A[0][0][0] - A[0][0][1] / A[0][0][0] * Yc, Yc]

##############################################################################
# Parametrization to find centre of circle in case circle tangents to 2 points
#and line or 2 lines and point
##############################################################################
# 2 lines and 1 point
def paramA1( A0, A1):
    # Ai = [ai,bi,ci] - the coefficients of line
    if (A0[0] - A1[0]) != 0 :
        return [[-(A0[2] - A1[2]) / (A0[0] - A1[0])],
                [- (A0[1] - A1[1]) / (A0[0] - A1[0])]]
    elif (A0[0] - A1[0]) == 0 and (A0[1] - A1[1]) != 0:
        return [[-(A0[2] - A1[2]) / - (A0[1] - A1[1])]]
    
    elif A0[0] != 0:
        return [[-(A0[2] + A1[2]) / 2/ A0[0]],[-A0[1] / A0[0]]]
    else: return [[-(A0[2] + A1[2]) / 2 / A1[1]]]

# 2 points and 1 line
def paramA2(p0, p1):
    if (p1.x - p0.x) != 0:
        return [[(p1.x ** 2 - p0.x ** 2 + p1.y ** 2 - p0.y ** 2) / (2 * (p1.x - p0.y))],
                [-(p1.y - p0.y) / (p1.x - p0.x)]]
    else: return [[(p1.y + p0.y) / 2]]


# get projection of the point
def projectionC(line, point):
    coef = (line.p1.x - line.p0.x) * (point.x - line.p0.x) + (line.p1.y - line.p0.y) * (point.y - line.p0.y)
    return  Point(line.p0.x + (line.p1.x - line.p0.x) * coef / line.distPoints() ** 2,
            line.p0.y + (line.p1.y - line.p0.y) * coef / line.distPoints() ** 2)
