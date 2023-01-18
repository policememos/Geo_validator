import json
import numpy as np
import os

class PoligonObject():
    def __init__(self, data, i=0):
        self.name = data.get('properties').get('description').replace('\n','').replace('<br>','') if data.get('properties').get('description') else 'Без описания'
        self.id = data['id']
        self.points = self.point_parser(data['geometry']['coordinates'][i])
        self.rawData = data['geometry']['coordinates'][i]
        self.object = data

    def point_parser(self, data):
        geo_arr = []
                
        for j in range(len(data)-1):
            geo_arr.append([data[j], data[j +1], j])
        return geo_arr
    
    
class PointObject():
    def __init__(self, data):
        self.name = data.get('properties').get('description') if data.get('properties').get('description') else 'Без описания'
        self.id = data['id']
        self.point_coord = data.get('geometry').get('coordinates')
        if x:=data.get('properties').get('iconCaption'):
            self.icon_caption = x
        self.point = data

    
    
class IntersectionResulter():
    def __init__(self, map_name):
        self.coord_objects, self.points, self.file, self.objects = self.create_data_objects(map_name)
        self.clear_pool__zone_names = self.check_names()
        self.results = []
        self.flag = False
    
    def check_names(self):
        if self.objects:
            raw_pool = [obj.name.replace('\n','').replace('</br>','') for obj in self.objects]
            zone_ids = sorted(set([(_id[0]) for _id in (x.split() for x in raw_pool)]))
            zone_names = sorted(set([(' '.join(_id[1:])) for _id in (x.split() for x in raw_pool)]))
            for zone in zone_ids:
                filtList = list(filter(lambda x: x.split()[0] == zone, raw_pool))
                if len(filtList) > 1:
                    print('Найдены зоны с одинаковым названием:')
                    print(*filtList, sep='\n')
            for zone in zone_names:
                filtList = list(filter(lambda x: ' '.join(x.split()[1:]) == zone, raw_pool))
                if len(filtList) > 1:
                    print('Найдены зоны с одинаковым названием:')
                    print(*filtList, sep='\n')
            return raw_pool
            
    
    def show_names(self):
        if self.objects:
            raw_pool = [obj.name for obj in self.objects]
            for zone in raw_pool:
                print(zone)

        
    def find_outside_points(self):
        if self.coord_objects:
            for obj in self.coord_objects:
                name = obj.name
                id = obj.id
                data = obj.rawData
                set_len = len(set([str(x) for x in data]))
                if len(data)-1 != set_len:
                    print(f'\nid зоны: {id}\nИмя зоны: {name}\nОшибка: В зоне найдены точки за пределами периметра зоны\n')

    def find_intersection(self, line1, line2):
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

    def check_this_data(self):
        if self.coord_objects:
            for obj in self.coord_objects:
                name = obj.name
                id = obj.id
                points = obj.points
                for i in range(len(points)-1):
                    k = points[i]
                    
                    for v in range(len(points)-i-2):
                        v = points[v+i+2]
                        if k[0] == v[1]: continue
                        res = self.find_intersection(k, v)
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

    def create_data_objects(self, map_name):
        with open(f'{map_name}', 'r', encoding='utf-8') as file:
            my_map = file.read()
        my_map = json.loads(my_map)
        arr_coords = list()
        arr_points = list()
        arr_objects = list()
        for obj in  my_map['features']:
            if obj['geometry']['type'] == 'Polygon':
                for i in range(len(obj['geometry']['coordinates'])):
                    arr_coords.append(PoligonObject(obj, i))
                arr_objects.append(PoligonObject(obj))
            if obj['geometry']['type'] == 'Point':
                arr_points.append(PointObject(obj))
        return arr_coords, arr_points, my_map, arr_objects
    
    def check_points(self):
        if self.points:
            raw_pool_names = [pnt.name for pnt in self.points]
            raw_pool_icon_caption = [pnt.icon_caption for pnt in self.points]
            point_ids = sorted(set([(_id[0]) for _id in (x.split() for x in raw_pool_names)]))
            point_icon_captions = sorted(set([' '.join(_id[1:]) for _id in (x.split() for x in raw_pool_icon_caption)]))
            for point in point_ids:
                filt_list = list(filter(lambda x: x.split()[0] == point, raw_pool_names))
                if len(filt_list) > 1:
                    print('Найдены точки с одинаковым названием:')
                    print(*filt_list, sep='\n')
                    return False
            for point in point_icon_captions:
                filt_list = list(filter(lambda x: ' '.join(x.split()[1:]) == point, raw_pool_icon_caption))
                if len(filt_list) > 1:
                    print('Найдены точки с одинаковым названием:')
                    print(*filt_list, sep='\n')
                    return False
            return True
        
    def rename_points(self):
        if self.points:
            if self.check_points():
                for _point in self.points:
                    if _point.icon_caption:
                        _point.name = _point.icon_caption
                        _point.point['properties'].pop('iconCaption')
                        _point.point['properties']['description'] = _point.name.replace('\n','').replace('<br>','')
            else:
                raise ValueError('Проверка не пройдена\nУстраните ошибки: одинаковые названия точек на карте')
        
    def create_json(self):
        objects = self.coord_objects
        points = self.points
        file = self.file
        file['metadata']['description'] = file['metadata']['description']+'\nобработан скриптом проверки'
        file['metadata']['features'] = [*objects, *points]
             

print('Файл с картой для удобства лучше переименовать\nКарта Тюмени и Тюменской области_28-12-2022_11-39-44 -> карта\n')
print('Потом введите сюда название файла с картой и нажмите на кравиатуре Enter')

while not os.path.exists(user_input:=str(input())+'.geojson'):
    print(f'\n\nВы ввели: {user_input.split(".")[0]}\nКарты с таким именем в этой папке не найдено')
    print('Попробуйте снова')
    
os.system('clear')
print('Считаю')
intersec = IntersectionResulter(user_input)
# intersec.checkThisData()
# intersec.find_outside_points()
# intersec.check_names()
intersec.check_points()
# intersec.create_json()