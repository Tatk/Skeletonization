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
    def __eq__(self, other):
        if (math.fabs(self.x - other.x)<0.000001 and math.fabs(self.y - other.y)<0.000001):
            return True
        else: return False

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
    def __eq__(self,other):
        if self.p0 == other.p0 or self.p0 == other.p1:
            return self.p0
        elif self.p1 == other.p0 or self.p1 == other.p1:
            return self.p1
        else: return False


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
        if not (math.fabs(A[0][0][0]) < 0.000001 or math.fabs(A[i][0][0]*A[i][1][1] - A[i][0][1]*A[i][1][0]) < 0.000001):
            Yc = -((A[0][0][0] * A[0][1][2] - A[0][1][0] * A[0][0][2]) / 
                   (A[0][0][0] * A[0][1][1] - A[0][0][1] * A[0][1][0]))
            return [-A[0][0][2] / A[0][0][0] - A[0][0][1] * Yc / A[0][0][0], Yc]
        else:
            Yc = -A[0][0][2] / A[0][0][1]
            return [-A[0][1][2] / A[0][1][0] - A[0][1][0] / A[0][1][0] * Yc, Yc]
        

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



def paramB(line1,line2, point):
    A = line1.paramOfLine()
    # A = [a, b, c]
    if (line2 != [] and math.fabs(A[0] * line2.paramOfLine()[1] - A[1] * line2.paramOfLine()[0])>0.000001) or not line2 != []:
        return [A[0] ** 2 - 1,
                A[0] * A[2] + point.x,
                A[1] ** 2 - 1,
                A[1] * A[2] + point.y,
                A[0] * A[1],
                line1_[2] ** 2 - point.x ** 2 - point.y ** 2]
    else:
       
        B = line2.paramOfLine()

        C0 = [[[-A[1], A[0], A[1]*point.x - A[0]*point.y],
               [A[0],A[1],A[2]]]]
        C1 = [[[-B[1], B[0], B[1]*point.x - B[0]*point.y],
               [B[0],B[1],B[2]]]]
        point0 = centreOfFirstCase(C0)
        point1 = centreOfFirstCase(C1)
        x = point0[0]+point1[0]
        y = point0[1]+point1[1]
        R = Line(Point(x,y),point0).dist_points()
        return [1,
                -x,
                1,
                -y,
                0,
                Line(Point(x,y),point).dist_points() ** 2 - R ** 2 + x**2 + y**2]

def paramC(A, B):
    if len(A) != 1:
        return [B[0] * A[1][0] ** 2 + B[2] + 2 * A[1][0] * B[4],
                B[0] * A[0][0] * A[1][0] + A[1][0] * B[1] + B[3] + B[4] * A[0][0],
                B[0] * A[0][0] ** 2 + 2 * A[0][0] * B[1] + B[5]]
    else:
        return [B[0], B[1] + B[4] * A[0][0], B[2] * A[0][0] ** 2 + 2 * A[0][0] * B[3] + B[5]]

# return centre in case circle tangents to 2 points and line or 2 lines and
# point
def centreOfSecondCase(A, C):
    if C[0] == 0:
        if len(A) == 2:
            Yc1 = -C[2] / 2 / C[1]
            return [[A[0][0] + A[1][0] * Yc1, Yc1],
                    [A[0][0] + A[1][0] * Yc1, Yc1]]
        else:
            Xc1 = -C[2] / 2 / C[1]
            return [[Xc1, A[0][0]],[Xc1, A[0][0]]]
        
    elif math.fabs((C[1] / C[0]) ** 2 - C[2] / C[0]) < 0.000001:
       if len(A) == 2:
          Yc1 = -C[1] / C[0]
          return [[A[0][0] + A[1][0] * Yc1, Yc1],
                  [A[0][0] + A[1][0] * Yc1, Yc1]]
       else:
          Xc1 = -C[1] / C[0]
          return [[Xc1, A[0][0]],[Xc1, A[0][0]]]
       
    elif (((C[1] / C[0]) ** 2) - (C[2] / C[0])) > 0 :
        if len(A) == 2:
            Yc1 = -C[1] / C[0] + math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            Yc2 = -C[1] / C[0] - math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            return [[A[0][0] + A[1][0] * Yc1, Yc1],
                    [A[0][0] + A[1][0] * Yc2, Yc2]]
        else:
            Xc1 = -C[1] / C[0] + math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            Xc2 = -C[1] / C[0] - math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            return [[Xc1, A[0][0]],[Xc2, A[0][0]]]

    else : return False

##############################################################################
# Parametrization to find virtual point of Bezier Curve
##############################################################################

# get projection of the point
def projectionC(line, point):
    coef = (line.p1.x - line.p0.x) * (point.x - line.p0.x) + (line.p1.y - line.p0.y) * (point.y - line.p0.y)
    return  Point(line.p0.x + (line.p1.x - line.p0.x) * coef / line.distPoints() ** 2,
            line.p0.y + (line.p1.y - line.p0.y) * coef / line.distPoints() ** 2)
def coordVectors(A, C):
    return Line(Point(C[0].x - A.x, C[0].y - A.y),
            Point(C[1].x - A.x, C[1].y - A.y))

def paramSystemV(vectors, V0, V1):
    return [[vectors.p0.x, vectors.p0.y, -(vectors.p0.x * V0.x + vectors.p0.y * V0.y)],
            [vectors.p1.x, vectors.p1.y, -(vectors.p1.x * V1.x + vectors.p1.y * V1.y)]]
##############################################################################
# Testing found second end point of temp bisector
##############################################################################
# testing centre of circle
def testingCentre(Xc, line):
    
    a = (Xc.x - line.p0.x) * (line.p1.x - line.p0.x) + (Xc.y - line.p0.y) * (line.p1.y - line.p0.y)
    if (((math.fabs(a) < 0.005) or (0 <= a <= distPoints(line) ** 2) or (math.fabs(a - distPoints(line) ** 2) < 0.01))):

        return Xc
    else: return False

# comparison between 2 end points
def comparePoints(centre, actbis,e):
    if (math.fabs(centre.x - actbis.x) < e and math.fabs(centre.y - actbis.y) < e): return False
    else: return True
# find intersection between radius of curve and segments of polygonal figure
def testingIntersections(centre, line, point, segments, points):
    if line:
        pLine = line.paramOfLine()
        distLine = math.fabs(pLine[0] * centre.x + pLine[1] * centre.y + pLine[2])
        if intersectionSegments(centre, line, point, segments, points, distLine):
            return True
    if point:
        distPoint = Line(centre,point).dist_points()
        if intersectionSegments(centre, line, point, segments, points, distPoint):
           return True
    return False
# this function used in testingProjections-function
def intersectionSegments(centre, line, point, segments, points,dist):
    for i in range(len(segments)):
        for k in range(len(points)):
            if testingCentre(projectionC(segments[i],centre),segments[i]):
                distSegment = Line(projectionC(segments[i],centre),centre).dist_points()
                distPoint = Line(centre,points[k]).dist_points()
                if ((distSegment > dist or math.fabs(distSegment - dist) < 0.03) and 
                    (distPoint > dist or math.fabs(distPoint - dist) < 0.03)):0
                else: return False
    return True
##############################################################################
# Add to lists
##############################################################################
#
def orderSites(lines,sites):
    tempList = []
    for i in range(len(lines)):
        for site in sites:
            if ((isinstance(site,Line) and 
                site.p0 == lines[i].p0 and site.p1 == lines[i].p1) 
                or 
                (isinstance(site,Point) and site == lines[i].p1)):
                
                tempList.append(site)       
    return tempList
# add ends point of bissector to skeletNodes-list
# add ready bisector to readyBisector-list
# add new active bisectors to activeBisector-list
def addInLists(tempNodes, activeBis, readyBisector, skeletNodes, segment,lines):
    node = []
    virtualNode = []
    node.append([[],activeBis[0][0]])
    if segment:
        minDistNodes = Line(projectionC(segment,activeBis[0][2]),projectionC(segment,tempNodes[0][0])).dist_points()
        for nodes in tempNodes:
            minDistNodes = min(minDistNodes,Line(projectionC(segment,activeBis[0][2]),projectionC(segment,nodes[0])).dist_points())
        for nodes in tempNodes:
            if math.fabs(minDistNodes - Line(projectionC(segment,activeBis[0][2]),projectionC(segment,nodes[0])).dist_points()) < 0.005:
                node.append(nodes)
                if isinstance(activeBis[0][0], Line) and isinstance(activeBis[0][1], Line):
                    skeletNodes.append([activeBis[0][2], node[1][0]])
                else:
                    virtualNode.append(centreOfFirstCase([paramSystemV(coordVectors([point for point in activeBis[0] if isinstance(point, Point)][0],
                                                                                    [projectionC(segment,activeBis[0][2]),
                                                                                     projectionC(segment, nodes[0])]),
                                                                       activeBis[0][2], nodes[0])]))
                    skeletNodes.append([activeBis[0][2], virtualNode[0], node[1][0]])
    else:
        minDistNodes = Line(activeBis[0][2],tempNodes[0][0]).dist_points()
        for nodes in tempNodes:
            minDistNodes = min(minDistNodes,Line(activeBis[0][2],nodes[0]).dist_points())
        for nodes in tempNodes:
            if math.fabs(minDistNodes - Line(activeBis[0][2],nodes[0]).dist_points()) < 0.005:
                node.append(nodes)
        skeletNodes.append([activeBis[0][2], node[1][0]])
    node.append([[],activeBis[0][1]])

    # reverse node-list in order touch sites circle from left active bisector
    # to right active bisector
    if len(node) != 3:
        del node[0]
        del node[-1]
        node = orderSites(lines,node)
        node.insert(0,[[],activeBis[0][0]])
        node.append([[],activeBis[0][1]])
    
    readyBisector.append([activeBis[0][0],activeBis[0][1]])
    activeBis[0].clear()

    # add in activeBisector
    for i in range(0,len(node) - 1):
        activeBis.append([node[i][1],node[i + 1][1], node[1][0]])




##############################################################################
# Skeletization of polygonal figure
##############################################################################
def Skeletonization(termNode, Lines, Points):
    activeBis = []
    activeBis.append([Lines[0], Lines[1], termNode])
    readyBisector = []
    skeletNodes = []
    skeletNodes.append([ [], termNode])
    while activeBis:
        if not [activeBis[0] for readyBis in readyBisector if (activeBis[0][0] in readyBis) and (activeBis[0][1] in readyBis)]:

            if isinstance(activeBis[0][0], Line) and isinstance(activeBis[0][1], Line):

                if activeBis[0][0] == activeBis[0][1]:
                    tempNode = activeBis[0][0] == activeBis[0][1]

                    if tempNode != activeBis[0][2]:
                        skeletNodes.append([activeBis[0][2], tempNode])
                        readyBisector.append([activeBis[0][0], activeBis[0][1]])
                    else:
                        tempNodes = []
                        for T in Points:
                             if (not [i for i in range(len(skeletNodes)) if T == skeletNodes[i][1]]):

                                 Xc = centreOfSecondCase(paramA1(activeBis[0][0].paramOfLine(), activeBis[0][1].paramOfLine()),
                                                         paramC(paramA1(T, activeBis[0][0].paramOfLine(), activeBis[0][1].paramOfLine()),
                                                                paramB(activeBis[0][1], activeBis[0][0], T)))
                                 if Xc:
                                        for xc in Xc :
                                            xc = Point(xc[0],xc[1])
                                            node = []
                                            node.append([testingCentre(xc, activeBis[0][0]),testingCentre(xc, activeBis[0][1])])

                                            if ((node[0][0] and node[0][1]) and comparePoints(node[0][0], activeBis[0][2], 0.02)
                                                and not [k for k in range(len(skeletNodes)) if not comparePoints(node[0][0], skeletNodes[k][1], 0.02) ] 
                                                and testingIntersections(node[0][0], [], T, Lines, Points)):
                                                tempNodes.append([node[0][0], T])
                                                break
                        for T in Lines:
                            if (not T in activeBis[0] ):

                                Xc = centreOfFirstCase(paramOf3Lines(T.paramOfLine(), activeBis[0][0].paramOfLine(), activeBis[0][1].paramOfLine()))

                                if Xc:
                                    for xc in Xc:
                                        xc = Point(xc[0],xc[1])
                                        node = []
                                        node.append([testingCentre(xc, activeBis[0][0]), testingCentre(xc, activeBis[0][1]), testingCentre(xc, T)])
                        
                                        if ((node[0][0] and node[0][1] and node[0][2]) and comparePoints(node[0][0], activeBis[0][2], 0.02)
                                        and not [k for k in range(len(skeletNodes)) if not comparePoints(node[0][0], skeletNodes[k][1], 0.02) ] 
                                        and testingIntersections(node[0][0], activeBis[0][0], [], Lines, Points)):
                                            tempNodes.append([node[0][0], T])
                        if tempNodes:
                            addInLists(tempNodes, activeBis, readyBisector, skeletNodes, actBis[1], Lines)
            elif isinstance(activeBis[0][0], Point) and isinstance(activeBis[0][1], Point):
                tempNodes = []
                for T in Points:
                    if (not T in [activeBis[0][0] , activeBis[0][1]] and not [g for g in range(len(skeletNodes)) if T == skeletNodes[g][1]]):
                         Xc = centreOfFirstCase(paramOf3Points(activeBis[0][0],activeBis[0][1], T))
                         Xc = Point(Xc[0],Xc[1])
                         if (comparePoints(Xc, activeBis[0][2],0.02)
                             and not [k for k in range(len(skeletNodes)) if not comparePoints(Xc, skeletNodes[k][1], 0.02) ] 
                             and testingIntersections(Xc, [], activeBis[0][0], Lines, Points)):
                             tempNodes.append([Xc, T])
                for T in Lines:
                    Xc = centreOfSecondCase(paramA2(activeBis[0][0], activeBis[0][1]),
                                            paramC(paramA2(activeBis[0][0], activeBis[0][1], T),
                                                   paramB(T, [], activeBis[0][1])))
                    if Xc:
                        for xc in Xc :
                            xc = Point(xc[0],xc[1])
                            node = testingCentre(xc, T)
                            if (node and comparePoints(node, activeBis[2], 0.02)
                                and not [k for k in range(len(skeletNodes)) if not comparePoints(node, skeletNodes[k][1], 0.02) ]
                                and testingIntersections(node, [], activeBis[0][0], Lines, Points)):
                                tempNodes.append([node, T])
                                break
                if tempNodes:
                    addInLists(tempNodes, activeBis, readyBisector, skeletNodes, [], Lines)
            else:
                point = Point(0,0)
                line = Line(point,point)
                if isinstance(activeBis[0][0], Point):
                    point = activeBis[0][0].deepcopy()
                    line = activeBis[0][1].deepcopy()
                else:
                    point = activeBis[0][1].deepcopy()
                    line = activeBis[0][0].deepcopy()
                if not Line(point,point) == line:
                    tempNodes = []
                    for T in Points:
                        if (T != point and not [j for j in range(len(skeletNodes)) if T == skeletNodes[j][1]]):
                            
                            Xc = centreOfSecondCase(paramA2(T,point),
                                                    paramC(paramA2(T,point, line),
                                                           paramB(line, [], T)))
                            if Xc :
                                for xc in Xc :
                                    xc = Point(xc[0],xc[1])
                                    node = testingCentre(xc, line)
                                    if (node and comparePoints(node, activeBis[0][2],0.02)
                                             and not[k for k in range(len(skeletNodes)) if not comparePoints(node, skeletNodes[k][1], 0.02) ]
                                             and testingIntersections(node, [], T, Lines, Points)):
                                        tempNodes.append([node, T])
                                        break
                    for T in lines:
                        if T.p0 != line.p0 and T.p1 != line.p1:
                            Xc = centreOfSecondCase(paramA1(line.paramOfLine(), T.paramOfLine()),
                                                    paramC(paramA1(point, line.paramOfLine(), T.paramOfLine()),
                                                           paramB(T, actBis[1 - i],actBis[i][0])))
                            if Xc :
                                for xc in Xc :
                                    xc = Point(xc[0],xc[1])
                                    node = []
                                    node.append([testingCentre(xc, actBis[1 - i]), testingCentre(xc, T)])
                                    if (node[0][0] and node[0][1]
                                        and not [k for k in range(len(skeletNodes)) if not comparePoints(node[0][0], skeletNodes[k][1], 0.02) ]
                                        and comparePoints(node[0][0], activeBis[0][2],0.02)
                                        and testingIntersections(node[0][0], T, [], lines, Points)):
                                        tempNodes.append([node[0][0], T])
                                        break
                    if tempNodes:
                        addInLists(tempNodes, activeBis, readyBisector, skeletNodes, line, Lines)
    return skeletNodes

def AbsPath(sk):
    a = []
    for i in range(1,len(sk)):
        if len(sk[i]) == 2:
            a.append(['M', sk[i][0]])
            a.append(['L', sk[i][1]])
        else:
            a.append(['M', sk[i][0]])
            a.append(['C', sk[i][1] + sk[i][2] + sk[i][2]])
    return a

