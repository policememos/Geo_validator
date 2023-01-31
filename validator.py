import json
import numpy as np
import os
import csv_parser as cp

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
        self.del_fake_points()
        self.clear_pool__zone_names, self.id_name_map_zones, self.flag_names = self.check_names()
        self.results = []
        self.flag = False
    
    def check_names(self):
        if self.objects:
            flag_names = True
            raw_pool = [obj.name.replace('\n','').replace('</br>','') for obj in self.objects]
            zone_ids_names = [(_id, name) for _id, name in map(lambda x: (x[0], ' '.join(x[1:])), map(lambda y: y.split(), raw_pool))]
            zone_ids = sorted(set([(_id[0]) for _id in (x.split() for x in raw_pool)]))
            zone_names = sorted(set([(' '.join(_id[1:])) for _id in (x.split() for x in raw_pool)]))
            # print('Проверка на совпадение ID зон')
            to_set = []
            for zone in zone_ids:
                filtList_id = list(filter(lambda x: x.split()[0] == zone, raw_pool))
                if len(filtList_id) > 1:
                    flag_names = False
                    to_set += filtList_id
            for zone in zone_names:
                filtList_name = list(filter(lambda x: ' '.join(x.split()[1:]) == zone, raw_pool))
                if len(filtList_name) > 1:
                    flag_names = False
                    to_set += filtList_name

            if not flag_names:
                print('Ошибка в файле карты: Найдены зоны с одинаковым названием:')
                print(*set(to_set), sep='\n')
                print()
            
            return raw_pool, zone_ids_names, flag_names
            
    
    def show_names(self):
        if self.objects:
            raw_pool = [obj.name for obj in self.objects]
            for zone in raw_pool:
                print(zone)
                
    def zone_names(self):
        if self.objects:
            raw_pool = [obj.name.split()[0] for obj in self.objects]
            return raw_pool

        
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
            raw_pool_icon_caption = [pnt.icon_caption for pnt in self.points if hasattr(pnt, 'icon_caption')]
            point_ids = sorted(set([(_id[0]) for _id in (x.split() for x in raw_pool_names)]))
            point_icon_captions = sorted(set([' '.join(_id[1:]) for _id in (x.split() for x in raw_pool_icon_caption)]))
            for point in point_ids:
                filt_list = list(filter(lambda x: x.split()[0] == point, raw_pool_names))
                if len(filt_list) > 1:
                    print('Найдены точки с одинаковым названием:')
                    print(*filt_list, sep='\n')
                    return False
            for caption in point_icon_captions:
                filt_list = list(filter(lambda x: ' '.join(x.split()[1:]) == caption, raw_pool_icon_caption))
                if len(filt_list) > 1:
                    print('Найдены точки с одинаковым названием:')
                    print(*filt_list, sep='\n')
                    return False
            return True
    
    def del_fake_points(self):
        if self.points:
            res_arr = []
            for point in self.points:
                if hasattr(point, 'icon_caption'):
                    if 'tzru' in point.name.lower() or 'tzru' in point.icon_caption.lower():
                        res_arr.append(point)
                else:
                    if 'tzru' in point.name.lower():
                        res_arr.append(point)
            self.points = res_arr
            
            
    def rename_points(self):
        if self.points:
            for _point in self.points:
                if _point.icon_caption:
                    _point.name = _point.icon_caption
                    _point.point['properties'].pop('iconCaption')
                    _point.point['properties']['description'] = _point.name.replace('\n','').replace('<br>','')
            if self.check_points():
                ...
            else:
                raise ValueError('Проверка не пройдена\nУстраните ошибки: одинаковые названия точек на карте')
        
    def create_json(self):
        objects = self.coord_objects
        points = self.points
        file = self.file
        file['metadata']['description'] = file['metadata']['description']+'\nобработан скриптом проверки'
        file['metadata']['features'] = [*objects, *points]
             

def check_zones_diff_mapZones(name):
    excel_dataset = tp.parce_excel(name)
    map_names = intersec.zone_names()
    res_map_ex = set(map_names).difference(excel_dataset)
    print(f'map - excel {res_map_ex}')

print('Файл с картой для удобства лучше переименовать\nКарта Тюмени и Тюменской области_28-12-2022_11-39-44 -> карта\n')
print('Потом введите сюда название файла с картой и нажмите на кравиатуре Enter')

# while not os.path.exists(user_input:=str(input())+'.geojson'):
#     print(f'\n\nВы ввели: {user_input.split(".")[0]}\nКарты с таким именем в этой папке не найдено')
#     print('Попробуйте снова')
    
os.system('clear')
# print('Считаю')
# intersec = IntersectionResulter(user_input)
# intersec.show_names()
intersec = IntersectionResulter('sam_map.geojson')
# intersec.checkThisData()
intersec.find_outside_points()
if intersec.flag_names:
    print('Имена зон на карте проверены, валидно')
    print()
if intersec.check_points():
    print('Точки на карте проверены, валидно')
    print()
# intersec.rename_points()
# intersec.create_json()

map_zone_names = intersec.id_name_map_zones
map_region = map_zone_names[0][0][:6]
yt, yt_noset = cp.parce_excel('sam_yt', 'yt')
price, price_noset = cp.parce_excel('sam_price', 'price')
price_zones, price_zones_noset = cp.parce_excel('sam_price', 'price_zones')
code_zones, code_zones_noset = cp.parce_excel('sam_shab_kodi_zon', 'code_zones')
code_zones_shab_ids = [x[0] for x in code_zones_noset]
    
code_price_zones = sorted(list(price_zones))    
code_zones_zo = sorted(list(code_zones)) 
# Проверка  повторения id зон в шаблонах
for el in price_noset:
    if tuple(price_noset).count(el)>1:
        print(f'Ошибка: в файле Тарифы найдено повторение тарифа из {el[0]} в {el[1]}')
        price_noset.remove(el)
for el in yt_noset:
    if tuple(yt_noset).count(el)>1:
        print(f'Ошибка: в файле yt/zt найдено повторение трансп. отношения из {el[0]} в {el[1]}')
        yt_noset.remove(el)
for el in code_zones_shab_ids:
    if tuple(code_zones_shab_ids).count(el)>1:
        print(f'Ошибка: в файле Шаблон коды зон найдено повторение id зоны {el}')
        code_zones_shab_ids.remove(el)
        


# Проверка названия зон в шаблонах
pr_fl = True
for i in code_price_zones:
    if i[0][0:6] != map_region:
        print(f'Ошибка: в карте с регионом {map_region} найдена зона {i[0]}, с названием {i[1]}')
    else:
        for j in code_zones_zo:
            if i[0] == j[0]:
                if i[1] != j[1]:
                    if pr_fl:
                        print()
                        print('Найдена неточность: найдены различия в названии зон в файлах Тарифы и Шаблон коды зон')
                        pr_fl = False
                    print(f'В файле Тарифы id:"{i[0]}", название:"{i[1]}"\nА в Шаблоне коды зон: "{j[1]}"\n')
pr_fl1 = True
id_z_cod_zones = [x[0] for x in code_zones]
for i in code_price_zones:
    if i[0][:6] == map_region:
        if i[0] not in id_z_cod_zones:
            if pr_fl1:
                print()
                ppr_fl1 = False
            print(f'Ошибка: в файле Шаблон код зон не найдена зона {i[0]} с названием {i[1]}')
print()
# Проверка на наличие в файле zt/yt
if temp_1:=set(price) - set(yt):
    t_l = [x for x in temp_1 if x[0][0:6] == map_region]
    if len(t_l)>1:
        print('Найдена ошибка: в файле кодов отношения зон (yt/zt) нет отношения:')
        for i in t_l:
            print(f'из {i[0]} в {i[1]}')
    elif len(t_l) == 1:
        print(f'Найдена ошибка: в файле кодов отношения зон (yt/zt) нет отношения из {t_l[0][0]} в {t_l[0][1]}')
print()

# Проверка зон из карты с зонами в шаблонах
geojson_id_zones = [x[0] for x in intersec.id_name_map_zones]
yt_id_zones = []
for i,j in yt:
    yt_id_zones.append(i)
    yt_id_zones.append(j)
price_zones_ids = [x[0] for x in price_zones]

for _id in set(geojson_id_zones):
    if _id not in code_zones_shab_ids:
        print(f'Ошибка: на карте есть зона id {_id}, но её нет в фалйе Шаблон коды зон')
        
for _id in set(geojson_id_zones):
    if _id not in yt_id_zones:
        print(f'Ошибка: на карте есть зона id {_id}, но её нет в фалйе трансп. отношений yt/zt')

for _id in set(geojson_id_zones):
    if _id not in price_zones_ids:
        print(f'Ошибка: на карте есть зона id {_id}, но её нет в фалйе Тарифы')

    