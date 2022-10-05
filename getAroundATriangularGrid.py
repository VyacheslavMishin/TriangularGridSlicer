import bpy
import math
import copy
import numpy as np
from collections import deque
from typing import List


class Node:
    '''
    Класс Node содержит в себе сведения о вершине триангулярной сетки:
    1. Декартовы координаты вершины __coordinates, тип данных - numpy array
    2. Массив индексов соседних вершин __neighboursIndices, индексы соседних вершин - целые числа
    3. Статус вершины self.__visited, логическое True, False
    4. Имя среза __sliceName (string) и подсреза __sliceSubSetName (string), которым принадлежит данная вершина 
    5. __rotatedZ - значение координаты вершины относительно направления нарезки (см. ниже) 
    '''    
    def __init__(self, bpyVertex, npNormal):
        '''
        Для создания вершины необходимо указать её прототип из Blender API вместо bpyVertex,
        а так же нормаль в виде numpy array, которая задаёт направление нарезки замкнутой поверхности
        '''
        self.__coordinates = np.array(bpyVertex.co)
        self.__neighboursIndices, self.__visited = [], False
        self.__sliceName, self.__sliceSubSetName = '',  ''
        self.rotateZ(npNormal)
    
    def getCoordinates(self):
        '''
        Возвращает ссылку на numpy array декартовых координат вершин 
        '''
        return self.__coordinates

    
    def addNeighbourIndex(self, index):
        '''
        Добавляет индекс соседа вершины к списку индексов соседей этой вершины
        '''
        self.__neighboursIndices.append(index)
    
    def getNeighboursIndecies(self):
        '''
        Возвращает ссылку на массив индексов соседей данной вершины
        '''
        return self.__neighboursIndices
    
    def markAsVisited(self):
        '''
        Отмечает данную вершину посещённой
        '''
        self.__visited = True


    def isVisited(self):
        '''
        Возвращает статус вершины
        '''
        return self.__visited

    
    def setSliceName(self, sliceName):
        '''
        Назначает имя среза, к которому принадлежит данная вершина
        '''
        self.__sliceName = sliceName

    
    def getSliceName(self):
        '''
        Возвращает имя среза, к которому принадлежит данная вершина
        '''
        return self.__sliceName    
    
    def rotateZ(self, npNormal):
        '''
        Вычисляет и сохраняет координату вершины вдоль направления нарезки
        '''
        self.__rotatedZ = self.__coordinates @ npNormal 

    
    def getRotatedZ(self):
        '''
        Возвращает координату вершины вдоль направления нарезки
        '''
        return self.__rotatedZ

    def getSliceSubSetName(self):
        '''
        Возвращает имя подсреза, которому принадлежит данная вершина
        '''
        return self.__sliceSubSetName
   
    def setSliceSubSetName(self, sliceSubSetName):
         '''
         Назначает имя подсреза, которому принадлежит данная вершина
         '''
         self.__sliceSubSetName = sliceSubSetName
         


class SliceSubSet:

    '''
    Класс SliceSubSet содержит в себе сведения о подсрезе:
    1. __sliceName - имя среза, частью которого является данный подсрез
    2. __sliceSubSetIndex - индекс подсреза
    3. __sliceSubSetNodes - список индексов вершин, входящих в данный подсрез
    4. __initialNodeIndex - индекс вершины, с которой начато построение данного подсреза и его редуцирование
    5. __reducedSlice - список индексов вершин, получившийся в итоге редуцирования списка всех вершин подсреза
    6. __ownName - имя подсреза, которое есть последовательная конкатенация стороки имени среза и индекса подсреза
    '''
    
    def __init__(self, initialNode: Node, initialNodeIndex: int, sliceSubSetIndex: int):
        
        '''
        Для создания подсреза необходимо указать начальную вершину вместо initialNode (экземпляр класса Node)
        Индекс этой начальной вершины вместо переменной initialNodeIndex (целое число)
        Индекс подсреза вместо переменной sliceSubSetIndex (целое число)  
        '''
        self.__sliceName = initialNode.getSliceName()
        self.__sliceSubSetIndex = sliceSubSetIndex
        self.__sliceSubSetNodes: List[int] = []
        self.__initialNodeIndex: int = initialNodeIndex
        self.__reducedSlice: List[int] = []
        self.__ownName = self.nodeSubSetName()

    
    def getOwnName(self):
        '''
         Возвращает имя данного подсреза
        '''
        return self.__ownName

    
    def getReducedSlice(self):
        '''
        Возвращает ссылку на массив индексов вершин данного среза, получившийся в 
        итоге редуцирования этого подсреза
        '''
        return self.__reducedSlice

    
    def addToReducedSlice(self, nodeIndex: int):
        '''
        Добавляет индекс вершины в список индексов вершин, получающемуся в 
        итоге редуцирования данного подсреза
        '''
        self.__reducedSlice.append(nodeIndex)
    
    def getInitialNodeIndex(self):
        '''
        Возвращает индекс вершины, с которой начато построение данного подсреза
        Этот же индекс отвечает вершине, с которой начинается редуцирование данного подсреза
        '''
        return self.__initialNodeIndex

    
    def setInitialNodeIndex(self, indexValue: int):
        '''
        Назначает индекс начальной вершины, с которой начинается построение данного подсреза
        '''
        self.__initialNodeIndex = indexValue    

    
    def getSliceName(self):
        '''
        Возвращает имя среза, к которому принадлежит данный подсрез
        '''
        return self.__sliceName

    def getSliceSubSetIndex(self):
        '''
        Возвращает индекс данного подсреза
        '''
        return self.__sliceSubSetIndex


    
    def addNode(self, neighbourIndex: int):
        '''
        Добавляет индекс вершины к списку таковых, состоящих в данном подсрезе
        '''
        self.__sliceSubSetNodes.append(neighbourIndex)

    
    def getAllNodesIndecies(self):
        '''
        Возвращает ссылку на список индексов всех вершин, состоящих в данном подсрезе
        '''
        return self.__sliceSubSetNodes    
    
    def nodeSubSetName(self):
        '''
        Составляет имя подсреза
        '''
        return self.getSliceName() + str(self.getSliceSubSetIndex())
    
    
    def bfs(self, initialNodeIndex: int, nodesArr: List[Node]):
        '''
        Поиск в ширину: принимает в себя индекс начальной вершины данного подсреза initialNodeIndex
        и ссылку на массив всех вершин nodeArr
        Поиск в ширину применяется для назначения всем вершинам, входящим в данный подсрез, имени этого подсреза
        '''
        bfsQueue = deque()
        bfsQueue.append(initialNodeIndex)
        self.addNode(initialNodeIndex)
        currentNode = nodesArr[initialNodeIndex]
        currentNode.setSliceSubSetName(self.nodeSubSetName())

        while len(bfsQueue):
            currentNode = nodesArr[bfsQueue.popleft()]
            for neighbourIndex in currentNode.getNeighboursIndecies():
                nodeToChek = nodesArr[neighbourIndex]
                if(not nodeToChek.getSliceSubSetName() and nodeToChek.getSliceName() == self.getSliceName()):
                    nodeToChek.setSliceSubSetName(self.getOwnName())
                    bfsQueue.append(neighbourIndex)
                    self.addNode(neighbourIndex)

    
    def reducer(self, nodesArr):
        ''' 
        Редуктор: принимает в себя ссылку на список всхех вершин nodesArr
        Редуктор применяется для редуцирования подсреза до замкнутой цепи вершин исходной сетки
        ВНИМАНИЕ: на данный момент редуктор так же подбирает (незначительное количество в сравнении с общим числом точек в конечной цепи)
        точки, которые могут формировать один или несколько треугольников, отстоящих от основной цепи.
        Эту особенность предполагается исправить чуть позже
        '''
        strategy = max
        currentNode = nodesArr[self.getInitialNodeIndex()]
        self.addToReducedSlice(self.getInitialNodeIndex())

        for neighbourIndex in currentNode.getNeighboursIndecies():
            neighbour = nodesArr[neighbourIndex] 
            if(neighbour.getRotatedZ() < currentNode.getRotatedZ() and neighbour.getSliceName() != currentNode.getSliceName()):
                strategy = min
                break

        for nodeIndex in self.getAllNodesIndecies():
            currentNode = nodesArr[nodeIndex]
            if(not currentNode.isVisited()):
                currentNode.markAsVisited()
                candidatIndices = list(filter(lambda index: nodesArr[index].getSliceSubSetName() != self.getOwnName(), currentNode.getNeighboursIndecies()))
                if(len(candidatIndices)):
                    candidatIndices.append(nodeIndex)
                    resultIndex = strategy(candidatIndices, key=lambda index: nodesArr[index].getRotatedZ())
                    if(resultIndex != nodeIndex):
                        self.addToReducedSlice(nodeIndex)
                    else:
                        continue   
                else:
                    continue 
                


class SlicerSoliton:
    '''
    Класс SlicerSoliton представляет собой интерфейс, позволяющий произвести нарезку
    триангулярной сетки, которая представленна списком Blender API вершин bpyVerticesArr,
    списком рёбер bpyEdgesArr. 
    Направление нарезки представляется вектором трёхмерным вектором npNormal (numpy array)
    Все перечисленные переменные необходимо указать при создании экземпляря класса SlicerSoliton.
    При создании экземпляра автоматически происходит построение графа (заполнение списка соседей каждой вершины исходной
    триангулярной сетки), а так же расчёт максимального возможного значения координаты вершины вдоль направления нарезки
    '''
    
    def __init__(self, bpyVerticesArr, bpyEdgesArr, npNormal):
        self.setDirection(npNormal)
        self.__initialBpyNodes = bpyVerticesArr
        self.__initialBpyEdges = bpyEdgesArr
        self.__nodesArr = [Node(vertex, npNormal) for vertex in bpyVerticesArr]
        self.__sortedNodesIndices = sorted(list(range(len(bpyVerticesArr))), key=lambda index: self.getNodesArr()[index].getRotatedZ())
        self.buildGraph()
        self.cubeEdgeLengthEval()
        self.logestDiagonalLength()
        '''
            Наиважнейшее поле в этом классе - словарь подсрезов
            Ключами словаря являются имена всех срезов данной триангулярной сетки
            Значениями являются списки подсрезов
            Все подсрезы в данном списке представлены экземплярами класса SliceSubSet
        '''
        self.__subSlicesDict = dict()

    
    def buildGraph(self):
        '''
        Заполняет список соседей вершин
        '''
        arrayToOperateWith = self.getNodesArr() 
        for edge in self.getBpyEdges():
            arrayToOperateWith[edge.vertices[0]].addNeighbourIndex(edge.vertices[1])
            arrayToOperateWith[edge.vertices[1]].addNeighbourIndex(edge.vertices[0])

    
    def cubeEdgeLengthEval(self):
        '''
        Вычисляет длину ребра куба координатной сетки
        '''
        firstNode = self.getNodesArr()[0]
        neighbourNode = self.getNodesArr()[firstNode.getNeighboursIndecies()[0]]
        vectorDifference = firstNode.getCoordinates() - neighbourNode.getCoordinates()

        self.__cubeEdgeLength = math.sqrt(vectorDifference @ vectorDifference)
    
    def logestDiagonalLength(self):
        '''
        Вычисляет длину самой длинной диагонали куба
        '''
        self.__maxRotatedZ = self.getCubeEdgeLenght() * (3 ** 0.5)

    
    def slicer(self):
        '''
        Производит нарезку данного графа вершин в заданном направлении
        '''
        nodesArr = self.getNodesArr()
        sortedIndices = self.getSortedIndices()
        baseNode = nodesArr[sortedIndices[0]]
        actualDivergency = self.getMaxRotatedZ()
        sliceIndex, sliceBaseID = 0, self.getSliceNameBase()

        currentSliceName = sliceBaseID + str(sliceIndex)

        for index in sortedIndices:
    
            currentNode = nodesArr[index]
    
            if(abs(baseNode.getRotatedZ() - currentNode.getRotatedZ()) <= actualDivergency):
                currentNode.setSliceName(currentSliceName)
                continue

            sliceIndex += 1
            currentSliceName = sliceBaseID + str(sliceIndex)
            currentNode.setSliceName(currentSliceName)
            baseNode = currentNode

    
    def sliceRunner(self):
        '''
        Выполняет разметку подсрезов и их редуцирование
        '''
        sortedNodesIndices = self.getSortedIndices()
        nodesList = self.getNodesArr()
        slicesDict = self.getSubSlicesDict()

        for nodeIndex in sortedNodesIndices:

            currentNode = nodesList[nodeIndex]
            self.initiateNewSubSlicesList(currentNode)

            if(not currentNode.getSliceSubSetName()):

                for neighbourIndex in currentNode.getNeighboursIndecies():

                    neighbourNode = nodesList[neighbourIndex]
                    if(neighbourNode.getSliceName() != currentNode.getSliceName()):
                        
                        newSubSlice = SliceSubSet(currentNode, nodeIndex, len(slicesDict[currentNode.getSliceName()]))
                        newSubSlice.bfs(nodeIndex, nodesList)
                        newSubSlice.reducer(nodesList)
                        self.appendNewSubSlice(newSubSlice)
                        break

    
    def slicesHighlighter(self, sliceIndex, subSlicesIndices=[]):
        '''
        Выполняет подсветку всех подсрезов среза с данным индексом sliceIndex
        Если указать массив целых неотрицательных чисел subSlicesIndices, то будут подсвечены
        подсрезы данного среза с индексами, указанными в subSlicesIndices, если такие существуют
        '''
        slicesDict = self.getSubSlicesDict()
        certainKeyToHighlight = list(slicesDict.keys())[sliceIndex]
        subSlicesArr = slicesDict[certainKeyToHighlight]
        initialBpyNodes = self.getBpyNodes()

        if(subSlicesIndices):
            
            for index in subSlicesIndices:
                try:
                    subSliceList = subSlicesArr[index]
                except KeyError:
                    continue
                else:    
                    for subIndex in subSliceList.getReducedSlice():
                        initialBpyNodes[subIndex].select = True
        else:
            for subSlice in subSlicesArr:
                for subIndex in subSlice.getReducedSlice():
                    initialBpyNodes[subIndex].select = True

    def getDirection(self):
        return self.__sliceDirection

    def setDirection(self, normalizedVector):
        self.__sliceDirection = normalizedVector

    def getNodesArr(self):
        return self.__nodesArr

    def getBpyNodes(self):
        return self.__initialBpyNodes
    
    def getSortedIndices(self):
        return self.__sortedNodesIndices

    def getBpyEdges(self):
        return self.__initialBpyEdges
    
    def getCubeEdgeLenght(self):
        return self.__cubeEdgeLength

    def getMaxRotatedZ(self):
        return self.__maxRotatedZ

    def getSliceNameBase(self):
        return self.__sliceNameBase
    
    def setSliceNameBase(self, stringValue):
        self.__sliceNameBase = stringValue

    def getSubSlicesDict(self):
        return self.__subSlicesDict


    def initiateNewSubSlicesList(self, node: Node):
        subSlicesDict = self.getSubSlicesDict()
        sliceName = node.getSliceName()
        try:
            subSlicesList = subSlicesDict[sliceName]
        except KeyError:
            subSlicesDict[sliceName] = []
        else:
            return

    def appendNewSubSlice(self, subSlice: SliceSubSet):
        subSlicesDict = self.getSubSlicesDict()
        subSlicesDict[subSlice.getSliceName()].append(subSlice)



bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object
bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')
vertices = obj.data.vertices
edges = obj.data.edges


'''
    Пример использвания SlicerSoliton
'''
# Инициализация направления нарезки, 
# направление - это вектор единичной длины, представленный numpy array
npNormal = np.array([0, 0, 1]) # np.array([1, 0, 1]) / math.sqrt(2)

# Инициализация экземпляра SlicerSoliton: 
# указаты списки вершин и рёбер исходной триангулярной сетки, 
# а так же направление нарезки
slicer = SlicerSoliton(vertices, edges, npNormal)

# Указывается строка-основа, из которой будут формироваться имена срезов и подсрезов
slicer.setSliceNameBase('slice')

# Нарезка сетки
slicer.slicer()

# Выделение и редуцирование подсрезов
slicer.sliceRunner()

# Подсветка точек подсрезов среза с данным номером в Blender 
slicer.slicesHighlighter(20)


bpy.ops.object.mode_set(mode = 'EDIT') 