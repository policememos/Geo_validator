import json
import numpy as np

class PoligonObject():
    def __init__(self, data, i):
        self.name = data.get('properties').get('description') if data.get('properties').get('description') else 'Без описания'
        self.id = data['id']
        self.points = self.pointParser(data['geometry']['coordinates'][i])
        self.rawData = data['geometry']['coordinates'][i]


    def pointParser(self, data):
        geo_arr = []
                
        for j in range(len(data)-1):
            geo_arr.append([data[j], data[j +1], j])
        return geo_arr
    
    
class IntersectionResulter():
    def __init__(self, map_name):
        self.objects = self.createDataObjects(map_name)
        self.results = []
        self.flag = False
        
    def findOutsidePoints(self):
        for obj in self.objects:
            name = obj.name
            id = obj.id
            data = obj.rawData
            set_len = len(set([str(x) for x in data]))
            if len(data)-1 != set_len:
                print(f'id зоны: {id}\nИмя зоны: {name}\nОшибка: В зоне найдены точки за пределами периметра зоны')

    def findIntersection(self, line1, line2):
        '''
        X(y2-y1) + Y(x1-x2) - x1*y2 + y1*x2 = 0 
        line = [[x1,y1],[x2,y2]] 
        '''
        line1_x1 = line1[0][0]
        line1_x2 = line1[1][0]
        line1_y1 = line1[0][1]
        line1_y2 = line1[1][1]
        line1_x = line1_y2-line1_y1
        line1_y = line1_x1-line1_x2
        line1_c = -line1_x1*line1_y2 + line1_y1*line1_x2
        
        line2_x1 = line2[0][0]
        line2_x2 = line2[1][0]
        line2_y1 = line2[0][1]
        line2_y2 = line2[1][1]
        line2_x = line2_y2-line2_y1
        line2_y = line2_x1-line2_x2
        line2_c = -line2_x1*line2_y2 + line2_y1*line2_x2

        m1 = np.array([[float(line1_x), float(line1_y)], [float(line2_x), float(line2_y)]])
        v1 = np.array([float(line1_c)*(-1), float(line2_c)*(-1)])
        try:
            return np.linalg.solve(m1, v1)
        except np.linalg.LinAlgError:
            return 0

    def checkThisData(self):
        for obj in self.objects:
            name = obj.name
            id = obj.id
            points = obj.points
            for i in range(len(points)-1):
                k = points[i]
                
                for v in range(len(points)-i-2):
                    v = points[v+i+2]
                    if k[0] == v[1]: continue
                    res = self.findIntersection(k, v)
                    if type(res) == int:
                        self.results.append(res) 
                    else:
                        if k[0][0] <= res[0] <= k[1][0] or v[0][0] <= res[0] <= v[1][0]:
                            if k[0][1] <= res[1] <= k[1][1] or v[0][1] <= res[1] <= v[1][1]:
                                self.results.append(tuple(res))

            if any(q:=tuple(filter(lambda x: x, self.results))):
                self.flag = True
                print(f'id зоны: {id}\nИмя зоны: {name}')
                print('Ошибка, найдены точки пересечения:')
                print(*q, sep='\n', end='\n\n')
        if not self.flag:
            print('Тест пройден, пересечений нет')



    def createDataObjects(self, map_name):
        with open(f'{map_name}.geojson', 'r', encoding='utf-8') as file:
            my_map = file.read()
        my_map = json.loads(my_map)
        arr = list()
        for obj in  my_map['features']:
            if obj['geometry']['type'] == 'Polygon':
                for i in range(len(obj['geometry']['coordinates'])):
                    arr.append(PoligonObject(obj, i))
        return arr


intersec = IntersectionResulter('Карта Тюмени и Тюменской области_28-12-2022_11-39-44')
intersec.findOutsidePoints()

