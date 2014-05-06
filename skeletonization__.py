#!/usr/bin/env python 
'''
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''
import inkex
import cubicsuperpath
import simplepath
from lxml import etree
import copy, math, re, random

# terminal point
def termNode(p):
    del p[-1]
    minXi = min(p[0][0][0],p[1][0][0])
    for i in range(2,len(p)):
        minXi = min(minXi,p[i][0][0])
    temp = []
    for i in range(len(p)):
        if (p[i][0][0] == minXi):
            temp.append(p[i][0])
    p.append(p[0])
    if (len(temp) != 1) :
        minYi = temp[0][1]
        for i in range(1,len(temp)) :
            minYi = min(minYi, temp[i][1])
        for i in range(len(temp)):
            if (minYi == temp[i][1]):
                return temp[i]   
    else :
        return temp[0]

# returns patern nodes   
def X(lines):
    X = []
    for i in range(len(lines)):
        X.append(lines[i][0])
    return X

# bypass of contour counterclockwise
def lines(p):
    
    lines = []
    n = int(len(p)-1)
    
    for i in range(n):
        if (termNode(p) in [p[i][0]]):
            del p[-1]
            if (i != n - 1) and (p[i + 1][0][1] >= p[i - 1][0][1]):
                for k in range(i - 1, n - 1):
                    lines.append([p[k][0],p[k + 1][0]])
                if i != 0: lines.append([p[n - 1][0],p[0][0]])
                for k in range(0,i - 1):
                    lines.append([p[k][0],p[k + 1][0]])
                p.append(p[0])
                return lines
            if (i != n - 1) and (p[i + 1][0][1] <= p[i - 1][0][1]):
                p.reverse()
                for k in range(n - i - 2, n - 1):
                    lines.append([p[k][0],p[k + 1][0]])
                if i!= 0 : lines.append([p[n-1][0],p[0][0]])
                for k in range(i-1,n - i - 2):
                    lines.append([p[k][0],p[k + 1][0]])
                p.reverse()
                p.append(p[0])                
                return lines
            # if termNode is n-point of points list
            if (p[0][0][1] >= p[n - 2][0][1]):
                for k in range(n - 1):
                    lines.append([p[k][0],p[k + 1][0]])
                lines.append([p[n - 1][0],p[0][0]])
                p.append(p[0])
                return lines
            if (p[0][0][1] <= p[n - 2][0][1]):
                p.reverse()
                lines.append([p[n - 1][0],p[0][0]])
                for k in range(n - 1):
                    lines.append([p[k][0],p[k + 1][0]])
                p.reverse()
                p.append(p[0])               
                return lines

# function returns concave nodes
def concaveNodes(points):
    concaveList = []
    points.append(points[0])
    points.append(points[1])
    termLines =(points[0][0] - points[1][0])*(points[1][1] - points[2][1])
    termLines-=(points[0][1] - points[1][1])*(points[1][0] - points[2][0])
    for i in range(1,len(points)-2):
        tempTermLines = (points[i][0] - points[i+1][0])*(points[i+1][1] - points[i+2][1])
        tempTermLines-= (points[i][1] - points[i+1][1])*(points[i+1][0] - points[i+2][0])
        if termLines*tempTermLines < 0:
            concaveList.append(points[i+1])
    del points[-1]
    del points[-1]
    return concaveList

##############################################################################
# Parametrization to find centre of circle in case circle tangents to 3 points
#or 3 lines
##############################################################################
# distance between 2 points
def distPoints(line):
    return math.sqrt((line[0][0] - line[1][0]) ** 2 + (line[0][1] - line[1][1]) ** 2)

def paramOfLine(line):
    return [-(line[1][1] - line[0][1]) / distPoints(line),
            (line[1][0] - line[0][0]) / distPoints(line),
            (line[1][1] * line[0][0] - line[0][1] * line[1][0]) / distPoints(line)]

def paramOf3Points(X1, X2, X3):
    return [[[2 * (X2[0] - X1[0]), 2 * (X2[1] - X1[1]), -(X2[0] ** 2 - X1[0] ** 2 + X2[1] ** 2 - X1[1] ** 2)], 
             [2 * (X3[0] - X1[0]), 2 * (X3[1] - X1[1]), -(X3[0] ** 2 - X1[0] ** 2 + X3[1] ** 2 - X1[1] ** 2)]]]

def paramOf3Lines(X1, X2, X3):
    if ((X2[0] - X1[0])*(X3[1] - X1[1]) - (X3[0] - X1[0])*(X2[1] - X1[1]) !=0 and (X2[0] - X1[0]) != 0):
        return [[[X2[0] - X1[0], X2[1] - X1[1], (X2[2] - X1[2])],
                [X3[0] - X1[0], X3[1] - X1[1], (X3[2] - X1[2])]]]
    else:
        return [[[X1[0] + X3[0], X1[1] + X3[1], X1[2] + X3[2]],
                [X2[0] - X3[0], X2[1] - X3[1], X2[2] - X3[2]]],
                [[X1[0] - X3[0], X1[1] - X3[1], X1[2] - X3[2]],
                 [X2[0] + X3[0], X2[1] + X3[1], X2[2] + X3[2]]]]

# return centre in case circle tangents to 3 points or 3 lines
def centreOfFirstCase(X):
    if (len(X[0]) == 2 and X[0][0][0] * X[0][1][1] - X[0][0][1] * X[0][1][0]) != 0 and X[0][0][0] != 0:
        Yc = -(X[0][0][0] * X[0][1][2] - X[0][1][0] * X[0][0][2]) / (X[0][0][0] * X[0][1][1] - X[0][0][1] * X[0][1][0])
        return [[-X[0][0][2] / X[0][0][0] - X[0][0][1] * Yc / X[0][0][0], Yc],
                [-X[0][0][2] / X[0][0][0] - X[0][0][1] * Yc / X[0][0][0], Yc]] 
    elif (len(X[0]) == 2 and X[0][0][0] * X[0][1][1] - X[0][0][1] * X[0][1][0]) != 0 and X[0][0][0] == 0:
        Yc = -X[0][0][2]/X[0][0][1]
        return [[-X[0][1][2]/X[0][1][0] - X[0][1][0]/X[0][1][0]*Yc, Yc],
                [-X[0][1][2]/X[0][1][0] - X[0][1][0]/X[0][1][0]*Yc, Yc]]
    else:
        Yc1 = (X[0][0][2] - X[0][0][0]*X[0][1][0])/(X[0][1][1]*X[0][0][0] - X[0][0][1])
        Yc2 = (X[1][0][2] - X[1][0][0]*X[1][1][0])/(X[1][1][1]*X[1][0][0] - X[1][0][1])
        return [[-(X[0][0][2]/X[0][0][0]) - X[0][0][1]/X[0][0][0]*Yc1, Yc1],
                [-(X[1][0][2]/X[1][0][0]) - X[1][0][1]/X[1][0][0]*Yc2, Yc2]]

##############################################################################
# Parametrization to find centre of circle in case circle tangents to 2 points
#and line or 2 lines and point
##############################################################################

def paramA1(X1, X2, X3):
    if (X2[0] - X3[0]) != 0 :
        return [[-(X2[2] - X3[2]) / (X2[0] - X3[0])],
                [- (X2[1] - X3[1]) / (X2[0] - X3[0])]]
    elif (X2[0] - X3[0]) == 0 and (X2[1] - X3[1]) != 0:
        return [[-(X2[2] - X3[2]) / - (X2[1] - X3[1])]]
    elif X2[0] != 0:
        return [[-(X2[2]+X2[2])/(2*X2[0])],
                [-X2[1]/X2[0]]]
    else:
        return [[-(X2[2]+X2[2])/(2*X2[1])],
                [-X2[1]/X2[1]],[]]

def paramA2(X1, X2, X3):
    if (X2[0] - X1[0]) != 0:
        return [[(X2[0] ** 2 - X1[0] ** 2 + X2[1] ** 2 - X1[1] ** 2) / (2 * (X2[0] - X1[0]))],
                [-(X2[1] - X1[1]) / (X2[0] - X1[0])]]
    else: return [[(X2[1] + X1[1]) / 2]]

def paramB(line1,line2, point):
    if (line2 !=[] and line1[0]*paramOfLine(line2)[1] - line1[1]*paramOfLine(line2)[0] !=0) or line2==[]:
        return [line1[0] ** 2 - 1,
                line1[0] * line1[2] + point[0],
                line1[1] ** 2 - 1,
                line1[1] * line1[2] + point[1],
                line1[0] * line1[1],
                line1[2] ** 2 - point[0] ** 2 - point[1] ** 2]
    elif paramOfLine(line2)[0] != 0:
        line=paramOfLine(line2)
        R = line[0]*projectionC(line2,point)[0]+line[1]*projectionC(line2,point)[1] + line[2]
        return [1,
                -point[0],
                1,
                -point[1],
                0,
                point[0]**2 + point[1]**2 - R**2]
    else:
        line=paramOfLine(line2)
        R = line[0]*projectionC(line2,point)[0]+line[1]*projectionC(line2,point)[1] + line[2]
        return [1,
                -point[1],
                1,
                -point[0],
                0,
                point[0]**2 + point[1]**2 - R**2]

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
    if C[0] ==0:
        if len(A) == 2:
            Yc1 = -C[2]/2/C[1]
            return [[A[0][0] + A[1][0] * Yc1, Yc1],
                    [A[0][0] + A[1][0] * Yc1, Yc1]]
        elif len(A)==1:
            Xc1 = -C[2]/2/C[1]
            return [[Xc1, A[0][0]],[Xc1, A[0][0]]]
        else:
            Xc1 = -C[2]/2/C[1]
            return [[Xc1, A[0][0] + A[1][0] * Xc1],
                    [Xc1, A[0][0] + A[1][0] * Xc1]]
    elif math.fabs((C[1] / C[0]) ** 2 - C[2] / C[0]) < 0.000001:
       if len(A) == 2:
          Yc1 = -C[1] / C[0]
          return [[A[0][0] + A[1][0] * Yc1, Yc1],
                  [A[0][0] + A[1][0] * Yc1, Yc1]]
       elif len(A) ==1: 
          Xc1 = -C[1] / C[0]
          return [[Xc1, A[0][0]],[Xc1, A[0][0]]]
       else:
           Xc1=-C[1] / C[0]
           return [[Xc1, A[0][0] + A[1][0] * Xc1],
                   [Xc1, A[0][0] + A[1][0] * Xc1]]
    elif (((C[1] / C[0]) ** 2) - (C[2] / C[0])) > 0  :
        if len(A) == 2:
            Yc1 = -C[1] / C[0] + math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            Yc2 = -C[1] / C[0] - math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            return [[A[0][0] + A[1][0] * Yc1, Yc1],
                    [A[0][0] + A[1][0] * Yc2, Yc2]]
        elif len(A) ==1:
            Xc1 = -C[1] / C[0] + math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            Xc2 = -C[1] / C[0] - math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            return [[Xc1, A[0][0]],[Xc2, A[0][0]]]
        else:
            Xc1 = -C[1] / C[0] + math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            Xc2 = -C[1] / C[0] - math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            return [[Xc1, A[0][0] + A[1][0] * Xc1],
                    [Xc2, A[0][0] + A[1][0] * Xc2]]

    else : return False

##############################################################################
# Parametrization to find virtual point of Bezier Curve
##############################################################################

def projectionC(line, V):
    coef = (line[1][0] - line[0][0]) * (V[0] - line[0][0]) + (line[1][1] - line[0][1]) * (V[1] - line[0][1])
    return [line[0][0] + (line[1][0] - line[0][0]) * coef / distPoints(line) ** 2,
            line[0][1] + (line[1][1] - line[0][1]) * coef / distPoints(line) ** 2] 

def coordVectors(A, C):
    return [[C[0][0] - A[0], C[0][1] - A[1]],
            [C[1][0] - A[0], C[1][1] - A[1]]]

def paramSystemV(vectors, V0, V1):
    return [[vectors[0][0], vectors[0][1], -(vectors[0][0] * V0[0] + vectors[0][1] * V0[1])],
            [vectors[1][0], vectors[1][1], -(vectors[1][0] * V1[0] + vectors[1][1] * V1[1])]]  

##############################################################################
# Testing found second end point of temp bisector
##############################################################################
# testing centre of circle
def testingCentre(Xc, line):
    
    a = (Xc[0] - line[0][0]) * (line[1][0] - line[0][0]) + (Xc[1] - line[0][1]) * (line[1][1] - line[0][1])
    if (((math.fabs(a) < 0.005) or (0 <= a <= distPoints(line) ** 2) or (math.fabs(a - distPoints(line) ** 2) < 0.01)) ):

        return Xc
    else: return False
        
# comparison between 2 end points
def comparePoints(centre, actbis,e):
    if (math.fabs(centre[0] - actbis[0]) < e and math.fabs(centre[1] - actbis[1]) < e): return False
    else: return True

# find intersection between radius of curve and segments of polygonal figure  
def testingIntersections(centre, line, point, segments, points, readyBisector):
    if line:
        Line = paramOfLine(line)
        distLine = math.fabs(Line[0]*centre[0] + Line[1]*centre[1] +Line[2])
        if intersectionSegments(centre, line, point, segments, points, readyBisector,distLine):
            return True
    if point:
        distPoint = distPoints([centre,point])
        if intersectionSegments(centre, line, point, segments, points, readyBisector,distPoint):
           return True
    return False
# this function used in testingProjections-function
def intersectionSegments(centre, line, point, segments, points, readyBisector,dist):
    for i in range(len(segments)):
        for k in range(len(points)):
            if testingCentre(projectionC(segments[i],centre),segments[i]):
                distSegment = distPoints([projectionC(segments[i],centre),centre])
                dist_points = distPoints([centre,points[k]])
                if ((distSegment > dist or math.fabs(distSegment - dist)<0.3)
                    and (dist_points > dist or math.fabs(dist_points - dist)<0.3)):0
                else: return False
    return True
#find intersection between distance from first end point of bisector to possible second end point 
#and segments of polygonal figure
def testingCurve(centre, lines, actBis):

    for line in lines:
        if ((not line in actBis) and testingCentre(projectionC(line,centre),line) 
            and math.fabs(paramOfLine([centre,actBis[2]])[0]*paramOfLine(line)[1] 
                          - paramOfLine([centre,actBis[2]])[1]*paramOfLine(line)[0])>0.001):
            d = centreOfFirstCase([[paramOfLine([centre,actBis[2]]),paramOfLine(line)]])
            if (d and 
#if intersection between possible bisector and segment exist  return false
                ((line[0][0]< d[0][0] <line[1][0] or line[0][0]> d[0][0] >line[1][0])
                and (line[0][1]< d[0][1] <line[1][1] or line[0][1]> d[0][1] >line[1][1])
                and (centre[0]< d[0][0]< actBis[2][0] or centre[0]> d[0][0]> actBis[2][0])
                and (centre[1]< d[0][1]< actBis[2][1] or centre[1]> d[0][1]> actBis[2][1]))):
               return False
    return True

##############################################################################
# Add to lists
##############################################################################
#
def orderSites(lines,sites):
    tempList = []
    sortList = []
    for site in sites:
        if len(site[1]) == 2:
            sortList.append(site)
    for site in sites:
        if len(site[1]) == 1:
            sortList.append(site)
    for i in range(len(lines)):
        for site in sortList:
            if site[1] in [lines[i]] and len(site[1])==2:
                tempList.append(site)
            if site[1][0] in [lines[i][1]] and len(site[1])==1:
                tempList.append(site)
            
    return tempList
            
# add ends point of bissector to skeletNodes-list 
# add ready bisector to readyBisector-list
# add new active bisectors to activeBisector-list
def addInLists(actBis, tempNodes, activeBisector, readyBisector, skeletNodes, segment,lines):
    node = []
    virtualNode = []
    node.append([[],actBis[0]])
    if segment:
        minDistNodes = distPoints([projectionC(segment,actBis[2]),projectionC(segment,tempNodes[0][0])])
        for nodes in tempNodes:
            minDistNodes = min(minDistNodes,distPoints([projectionC(segment,actBis[2]),projectionC(segment, nodes[0])]))
        for nodes in tempNodes:
            if math.fabs(minDistNodes - distPoints([projectionC(segment,actBis[2]),projectionC(segment, nodes[0])])) < 0.005:
                node.append(nodes)
                if len(actBis[0]) + len(actBis[1]) == 3:
                    virtualNode.append(centreOfFirstCase([paramSystemV(coordVectors([point for point in actBis if point!=segment][0][0],#actBis[i][0],
                                                                              [projectionC(segment,actBis[2]),
                                                                               projectionC(segment, nodes[0])]),
                                                                 actBis[2], nodes[0])]))
        if len(actBis[0]) + len(actBis[1]) == 3: skeletNodes.append([actBis[2], virtualNode[0][0], node[1][0]])
        else: skeletNodes.append([actBis[2],actBis[2], node[1][0]])
    else:
        minDistNodes = distPoints([actBis[2],tempNodes[0][0]])
        for nodes in tempNodes:
            minDistNodes = min(minDistNodes,distPoints([actBis[2], nodes[0]]))
        for nodes in tempNodes:
            if math.fabs(minDistNodes - distPoints([actBis[2], nodes[0]])) < 0.005:
                node.append(nodes)
        skeletNodes.append([actBis[2],actBis[2], node[1][0]])
    node.append([[],actBis[1]])
    readyBisector.append([actBis[0],actBis[1]])
    # reverse node-list in order touch sites circle from left active bisector to right active bisector
    if len(node) != 3:
        del node[0]
        del node[-1]
        node = orderSites(lines,node)
        node.insert(0,[[],actBis[1]])
        node.append([[],actBis[0]])
        node.reverse()
    # add in activeBisector
    for i in range(0,len(node) - 1):
        activeBisector.append([node[i][1],node[i + 1][1], node[1][0]])
    
##############################################################################
# Skeletization of polygonal figure
##############################################################################
def Skeletonization(lines, X, termNode):
    activeBisector = []
    readyBisector = []
    skeletNodes = []
    activeBisector.append([lines[0], lines[1], termNode])
    #skeletNodes.append([[],termNode])

    for actBis in activeBisector:
        if not [actBis for readyBis in readyBisector if (actBis[0] in readyBis) and (actBis[1] in readyBis)]:
            
            if len(actBis[0]) + len(actBis[1]) == 4:
                
                tempNode = [temp for temp in actBis[0] if temp in actBis[1]]
                       
                if  tempNode and (tempNode[0] in X) and not (tempNode[0] in [actBis[2]]):
                    #skeletNodes.append([actBis[2], tempNode[0]])
                    readyBisector.append([actBis[0], actBis[1]])
                else:
                    tempNodes = []
                    for T in concaveNodes(X):
                        if (not [i for i in range(len(skeletNodes)) if  T in [skeletNodes[i][1]]]
                            and not ([j for j in range(len(readyBisector)) if  (T in readyBisector[j][0] and len(readyBisector[j][0])==1 or
                                                                                T in readyBisector[j][1] and len(readyBisector[j][1])==1)])):
                            Xc = centreOfSecondCase(paramA1(T, paramOfLine(actBis[0]),paramOfLine(actBis[1])),
                                                                    paramC(paramA1(T, paramOfLine(actBis[0]),
                                                                                   paramOfLine(actBis[1])),
                                                                           paramB(paramOfLine(actBis[1]),actBis[0],T)))
                            if Xc:
                                for xc in Xc :
                                    node = []
                                    node.append([testingCentre(xc, actBis[0]),testingCentre(xc, actBis[1])])

                                    if ((node[0][0] and node[0][1]) and comparePoints(node[0][0], actBis[2], 0.03)
                                        and testingIntersections(node[0][0], [], T, lines, concaveNodes(X), readyBisector) 
                                        and testingCurve(node[0][0], lines, actBis)):
                                        tempNodes.append([node[0][0], [T]])
                                        break
                    for T in lines:
                        if (not T in actBis 
                            and not ([j for j in range(len(readyBisector)) if  T in readyBisector[j]])):
                        
                            Xc = centreOfFirstCase(paramOf3Lines(paramOfLine(T),
                                                                 paramOfLine(actBis[0]),
                                                                 paramOfLine(actBis[1])))
                            if Xc:
                                for xc in Xc:
                                    node = []
                                    node.append([testingCentre(xc, actBis[0]), testingCentre(xc, actBis[1]), testingCentre(xc, T)])
                        
                                    if ((node[0][0] and node[0][1] and node[0][2]) and comparePoints(node[0][0], actBis[2], 0.03)
                                        and testingIntersections(node[0][0], actBis[0], [], lines,concaveNodes(X), readyBisector) 
                                        and testingCurve(node[0][0], lines, actBis)):
                                        tempNodes.append([node[0][0], T])
                                        break
                    if tempNodes:
                        addInLists(actBis, tempNodes, activeBisector, readyBisector, skeletNodes, actBis[1], lines)
            if  len(actBis[0]) + len(actBis[1]) == 2: 
                tempNodes = []
                for T in concaveNodes(X):
                    if (not [T] in actBis and not [i for i in range(len(skeletNodes)) if   T in [skeletNodes[i][1]]]
                        and not ([j for j in range(len(readyBisector)) if  (T in readyBisector[j][0] and len(readyBisector[j][0])==1 or
                                                                            T in readyBisector[j][1] and len(readyBisector[j][1])==1)])): 

                        Xc = centreOfFirstCase(paramOf3Points(actBis[0][0],actBis[1][0], T))

                        if (comparePoints(Xc[0], actBis[2],0.03) 
                            and testingIntersections(Xc[0], [], actBis[0][0], lines, concaveNodes(X), readyBisector)
                            and testingCurve(Xc[0], lines, actBis)):
                            tempNodes.append([Xc[0], [T]])
                            
                for T in lines: 
                    if (not ([j for j in range(len(readyBisector)) if  T in readyBisector[j]])):
                        Xc = centreOfSecondCase(paramA2(actBis[0][0], actBis[1][0], T), 
                                                paramC(paramA2(actBis[0][0], actBis[1][0], T), 
                                                       paramB(paramOfLine(T),[],actBis[0][0])))
                        if Xc:
                            for xc in Xc :
                                node = testingCentre(xc, T)
                                if (node and comparePoints(node, actBis[2],0.03)
                                    and testingIntersections(node, [], actBis[0][0], lines, concaveNodes(X), readyBisector)
                                    and testingCurve(node, lines, actBis)):
                          
                                    tempNodes.append([node, T])
                                    break
                if tempNodes:
                    addInLists(actBis, tempNodes, activeBisector, readyBisector, skeletNodes, [], lines)
            if len(actBis[0]) + len(actBis[1]) == 3:
                i = len(actBis[0]) - 1
                if not actBis[i][0] in actBis[1 - i] :
                        tempNodes = []
                        for T in concaveNodes(X):
                             if (not T in actBis[i]  and not [j for j in range(len(skeletNodes)) if  T in [skeletNodes[j][1]]]# and comparasionOfLists(actBis,[T],readyBisector)
                                 and not ([j for j in range(len(readyBisector)) if  (T in readyBisector[j][0] and len(readyBisector[j][0])==1 or
                                                                                     T in readyBisector[j][1] and len(readyBisector[j][1])==1)])):
                                 Xc = centreOfSecondCase(paramA2(T,actBis[i][0],  actBis[1 - i]), 
                                                         paramC(paramA2(T,actBis[i][0], actBis[1 - i]), 
                                                                paramB(paramOfLine(actBis[1 - i]),[], T)))
                                 if Xc :
                                     for xc in Xc :
                                         node = testingCentre(xc, actBis[1 - i])
                                         if (node and comparePoints(node, actBis[2],0.03)
                                             and testingIntersections(node, [], T, lines, concaveNodes(X), readyBisector)
                                             and testingCurve(node, lines, actBis)):

                                             tempNodes.append([node, [T]])
                                             break
                        for T in lines:
                            if (not T in actBis
                                and not ([j for j in range(len(readyBisector)) if  T in readyBisector[j]])):
                                Xc = centreOfSecondCase(paramA1(actBis[i][0], paramOfLine(actBis[1 - i]),paramOfLine(T)),
                                                        paramC(paramA1(actBis[i][0], paramOfLine(actBis[1 - i]),
                                                                       paramOfLine(T)),
                                                               paramB(paramOfLine(T), actBis[1 - i],actBis[i][0])))
                                if Xc :
                                    for xc in Xc :
                                        node = []
                                        node.append([testingCentre(xc, actBis[1 - i]), testingCentre(xc, T)])

                                        if (node[0][0] and node[0][1] and comparePoints(node[0][0], actBis[2],0.03)
                                            and testingIntersections(node[0][0], T, [], lines, concaveNodes(X), readyBisector)
                                            and testingCurve(node[0][0], lines, actBis)):
                                            tempNodes.append([node[0][0], T])
                                            break
                        if tempNodes:
                            addInLists(actBis, tempNodes, activeBisector, readyBisector, skeletNodes, actBis[1-i], lines)
    return skeletNodes


def extSkeletNodes(skeletNodes):
    del skeletNodes[0]
    skeletPaths = []
    k=0
    while skeletNodes:
        skeletPaths.append([])
        skeletPaths[k].append(skeletNodes.pop(0))
        n = len(skeletNodes)
        lenSketetPaths = 0
        while lenSketetPaths != len(skeletPaths[k]):
            for i in range(n):
                if skeletPaths[k][-1][-1] in [skeletNodes[i][0]]:
                    skeletPaths[k].append(skeletNodes.pop(i))
                    break
            n = len(skeletNodes)
            lenSketetPaths+=1
        k+=1    
    return skeletPaths

# required for parser to svg-file                               
def AbsPath(skeletPaths):
    a = []
    a.append(['M', skeletPaths[0][0][0]])
    for i in range(len(skeletPaths)):
        for j in range(len(skeletPaths[i])):
                a.append(['C', skeletPaths[i][j][1] + skeletPaths[i][j][2] + skeletPaths[i][j][2]])
        if i!=len(skeletPaths)-1: a.append(['M', skeletPaths[i+1][0][0]])
    return a



def zSort(inNode,idList):
    sortedList=[]
    theid = inNode.get("id")
    if theid in idList:
       sortedList.append(theid)
    for child in inNode:
        if len(sortedList)==len(idList):
            break
        sortedList+=zSort(child,idList)
    return sortedList

class Skeleton(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

        self.OptionParser.add_option("-c", "--copymode",
                                     action="store", type="string", 
                                     dest="copymode", default="clone",
                                     help="duplicate pattern before skeletonization")

    def duplicateNodes(self, aList):
        clones={}
        for id,node in aList.iteritems():
            clone=copy.deepcopy(node)
            myid = node.tag.split('}')[-1]
            clone.set("id", self.uniqueId(myid))
            node.getparent().append(clone)
            clones[clone.get("id")]=clone
        return(clones)
    
    def uniqueId(self, prefix):
        id="%s%04i"%(prefix,random.randint(0,9999))
        while len(self.document.getroot().xpath('//*[@id="%s"]' % id,namespaces=inkex.NSS)):
            id="%s%04i"%(prefix,random.randint(0,9999))
        return(id)

    def prepareSelectionList(self):
        idList=self.options.ids
        idList=zSort(self.document.getroot(),idList)
        id = idList[-1]
        self.patternNode=self.selected[id]
        self.gNode = etree.Element('{http://www.w3.org/2000/svg}g')
        self.patternNode.getparent().append(self.gNode)

        if self.options.copymode=="copy":
            duplist=self.duplicateNodes({id:self.patternNode})
            self.patternNode = duplist.values()[0]

    def effect(self):
        self.prepareSelectionList()
        for id, node in self.selected.iteritems():
            if node.tag == inkex.addNS('path','svg'):

                p = cubicsuperpath.parsePath(node.get('d'))

                #inkex.debug("nodes: %s" % p) 
                node.set('d',simplepath.formatPath(AbsPath(extSkeletNodes(Skeletonization(lines(p[0]), X(lines(p[0])), termNode(p[0]))))))
if __name__ == '__main__':
    e = Skeleton()
    e.affect() 
