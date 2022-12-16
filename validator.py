import json
import numpy as np

class PoligonObject():
    def __init__(self, data):
        self.name = data['properties']['description'] if data['properties']['description'] else 'Без описания'
        self.id = data['id']
        self.points = self.pointParser(data['geometry']['coordinates'])


    def pointParser(self, data):
        geo_arr = []
        for j in range(len(data)-1):
            geo_arr.append((tuple(data[j]), tuple(data[j +1]), j))
        return geo_arr
    
    
class IntersectionResulter():
    def __init__(self, map_name):
        self.objects = self.createDataObjects(map_name)
        self.results = list()

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

    def checkThisData(self, points):
        for i in range(len(points)-1):
            k = points[i]
            for v in range(len(points)-i-2):
                v = points[v+i+2]
                if k[0] == v[1]: continue
                res = self.findIntersection(k, v)
                if isinstance(res, int):
                    self.results.append(res) 
                else:
                    self.results.append(tuple(res))

        if any(q:=tuple(filter(lambda x: x, self.results))):
            print('Ошибка, найдены точки пересечения:')
            print(*q, sep='\n')
        else:
            print('Пересечений нет, тест пройден')

    def createDataObjects(self, map_name):
        with open(f'{map_name}.geojson', 'r', encoding='utf-8') as file:
            my_map = file.read()
        my_map = json.loads(my_map)
        arr = list()
        for obj in  my_map['features']:
            if obj['geometry']['type'] == 'Polygon':
                arr.append(PoligonObject(obj))
        return arr



test = [
            [60.58338876708975, 56.832553409644696],
            [60.65102334960926, 56.83217699467162],
            [60.64999338134753, 56.84647809347648],
            [60.63935037597644, 56.86039757774293],
            [60.56656595214833, 56.85531944939838],
            [60.56261774047841, 56.84083357813022],
            [60.58338876708975, 56.832553409644696]
          ]

test_obj = {
      "type": "Feature",
      "id": 6,
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [60.722562424805155, 56.86003801020114],
            [60.73681031909227, 56.870192288802784],
            [60.73629533496143, 56.85919169536988],
            [60.720502488281745, 56.869628234829044],
            [60.70831453051804, 56.87808814750843],
            [60.722562424805155, 56.86003801020114]
          ]
        ]
      },
      "properties": {
        "fill": "#ed4543",
        "fill-opacity": 0.6,
        "stroke": "#ed4543",
        "stroke-width": "5",
        "stroke-opacity": 0.9
      }
    }

intersec = IntersectionResulter('map')
print(intersec.objects)
