# from datetime import datetime as dt
import csv
import openpyxl
# from itertools import combinations
# import pandas as pd
import json

MAP_NAME = 'map'
PRICE_NAME = 'price'
LOG_FILE = []

def save_log(type = 1):
    if type == 1:
        with open('log.txt', 'w', encoding='utf-8') as logfil:
            for line in LOG_FILE:
                logfil.write(line)
                logfil.write('\n')
    if type == 2:
        with open('log.txt', 'a', encoding='utf-8') as logfil:
            for line in LOG_FILE:
                logfil.write(line)
                logfil.write('\n')

with open(f'{PRICE_NAME}.csv', 'r', encoding='windows-1251') as samfile:
    reader = csv.reader(samfile, delimiter=';')
    flag = 0
    for row in reader:
        if flag < 1:
            flag += 1
            continue
  

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
        self.clear_pool__zone_names, self.id_name_map_zones, self.flag_names, self.map_region, self.flag_names_region, self.flag_alert = self.check_names()
        self.results = []
        self.flag = False
    
    def check_names(self):
        if self.objects:
            flag_names = True
            flag_names_region = True
            flag_alert = False
            raw_pool1 = [obj.name.strip().replace('\n','').replace('</br>','') for obj in self.objects]
            raw_pool = []
            for el_ in raw_pool1:
                pool_name = el_[:11] +' '+ el_[12:].strip(',').strip('.').strip().replace('\n','').replace('\br','')
                raw_pool.append(pool_name)
            zone_ids_names = [(_id, name) for _id, name in map(lambda x: (x[0], ' '.join(x[1:]).replace(',','').strip()), map(lambda y: y.split(), raw_pool))]
            zone_ids = sorted(set([(_id[0].strip().replace(',','')) for _id in (x.split() for x in raw_pool)]))
            zone_names = sorted(set([(' '.join(_id[1:])) for _id in (x.split() for x in raw_pool)]))
            # print('Проверка на совпадение ID зон')
            to_set = []
            to_set_region = []
            most_common = None # наиболее часто встречаемое значение
            qty_most_common = 0 # его количество
            zone_ids_reg = [x[0:6] for x in zone_ids]
            a_set = set(zone_ids_reg)
            for item in a_set:
                # переменной qty присваивается количество случаев
                # item в списке a
                qty = zone_ids_reg.count(item)
                # Если это количество больше максимального,
                if qty > qty_most_common:
                    qty_most_common = qty # то заменяем на него максимальное,
                    most_common = item # запоминаем само значение
            map_region = most_common
            for zone in zone_ids:
                if zone[0:6] != map_region:
                    flag_names_region = False
                    to_set_region.append(zone)
                filtList_id = list(filter(lambda x: x.split()[0] == zone, raw_pool))
                if len(filtList_id) > 1:
                    flag_names = False
                    to_set.append(filtList_id)
                 
            for zone in zone_names:
                if zone[:1] not in ('1','0'):
                    print(f'Ошибка в файле карты: зона "{zone}" без признака типа доставки 1/0 в названии')
                    LOG_FILE.append(f'Ошибка в файле карты: зона "{zone}" без признака типа доставки или нарушает шаблон [1/0]Название')
                    flag_alert = True
                filtList_name = list(filter(lambda x: ' '.join(x.split()[1:]) == zone, raw_pool))
                if len(filtList_name) > 1:
                    flag_names = False
                    to_set.append(filtList_name)

            if not flag_names:
                print('Ошибка в файле карты: Найдены зоны с одинаковым названием:')
                LOG_FILE.append('Ошибка в файле карты: Найдены зоны с одинаковым названием:')
                print(*set(to_set), sep='\n')
                sad = tuple(set(to_set))
                for i in sad:
                    LOG_FILE.append(i)
                print()
                LOG_FILE.append('\n')
            if not flag_names_region:
                print(f'Ошибка в файле карты: Найдены зоны которые не входят в карту региона {map_region}:')
                LOG_FILE.append(f'Ошибка в файле карты: Найдены зоны которые не входят в карту региона {map_region}:')
                print(*to_set_region, sep='\n')
                sad = tuple(set(to_set_region))
                for i in sad:
                    LOG_FILE.append(i)
                print()
                LOG_FILE.append('\n')
            
            return raw_pool, zone_ids_names, flag_names, map_region, flag_names_region, flag_alert
            
    
    def show_names(self):
        if self.clear_pool__zone_names:
            for zone in self.clear_pool__zone_names:
                print(zone)
                
    def show_zone_ids(self):
        if self.id_name_map_zones:
            for elm in self.id_name_map_zones:
                print(elm[0])
        
    def find_outside_points(self):
        if self.coord_objects:
            for obj in self.coord_objects:
                name = obj.name
                id = obj.id
                data = obj.rawData
                set_len = len(set([str(x) for x in data]))
                if len(data)-1 != set_len:
                    print(f'\nid зоны: {id}\nИмя зоны: {name}\nОшибка: В зоне найдены точки за пределами периметра зоны\n')
                    LOG_FILE.append(f'\nid зоны: {id}\nИмя зоны: {name}\nОшибка: В зоне найдены точки за пределами периметра зоны\n')

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
                    LOG_FILE.append('Найдены точки с одинаковым названием:')
                    print(*filt_list, sep='\n')
                    for i in filt_list:
                        LOG_FILE.append(i)
                    print()
                    LOG_FILE.append('\n')
                    return False
            for caption in point_icon_captions:
                filt_list = list(filter(lambda x: ' '.join(x.split()[1:]) == caption, raw_pool_icon_caption))
                if len(filt_list) > 1:
                    print('Найдены точки с одинаковым названием:')
                    LOG_FILE.append('Найдены точки с одинаковым названием:')
                    print(*filt_list, sep='\n')
                    for i in filt_list:
                        LOG_FILE.append(i)
                    print()
                    LOG_FILE.append('\n')
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
                ...  #код на добавление описания этой точки
            else:
                raise ValueError('Проверка не пройдена\nУстраните ошибки: одинаковые названия точек на карте')
        
    def create_json(self):
        objects = self.coord_objects
        points = self.points
        file = self.file
        file['metadata']['description'] = file['metadata']['description']+'\nобработан скриптом проверки'
        file['metadata']['features'] = [*objects, *points]

#NEW CODE

def parce_excel(name, _type, caller):
    dataset = []
    dataset_price = []
    flag = False
    err_flag = False
    match _type:
        case 'yt':
            with open(f'{name}.csv', 'r', encoding='windows-1251') as file:
                reader = csv.reader(file, delimiter=';')
                for row in reader:
                    if flag < 9:
                        flag += 1
                        continue
                    if all(list(map(lambda x: x == row[3],(row[6],row[57],row[60])))):
                        if all(map(lambda x: x == row[8],(row[11],row[62],row[65]))):
                            dataset.append((row[3], row[8]))
                        else:
                            print(f'Ошибка: в файле отношений зон неправильно заполнена строка, данные из строки не валидны\nЗона прибытия: {row[8], row[11], row[62], row[65]}')
                            LOG_FILE.append(f'Ошибка: в файле отношений зон неправильно заполнена строка, данные из строки не валидны\nЗона прибытия: {row[8], row[11], row[62], row[65]}')
                            err_flag = True
                            break
                    else:
                        print(f'Ошибка: в файле отношений зон неправильно заполнена строка, данные из строки не валидны\nЗона отбытия: {row[3], row[6], row[57], row[60]}')
                        LOG_FILE.append(f'Ошибка: в файле отношений зон неправильно заполнена строка, данные из строки не валидны\nЗона отбытия: {row[3], row[6], row[57], row[60]}')
                        err_flag = True
                        break

        case 'price':
            with open(f'{name}.csv', 'r', encoding='windows-1251') as file:
                reader = csv.reader(file, delimiter=';')
                flag = 1
                for row in reader:
                    if flag:
                        flag = 0
                        continue
                    dataset.append((row[0], row[2]))  
        
        case 'price_zones':
            with open(f'{name}.csv', 'r', encoding='windows-1251') as file:
                reader = csv.reader(file, delimiter=';')
                flag = 1
                for row in reader:
                    if flag:
                        flag = 0
                        continue
                    dataset.append((row[0], row[1]))  
                    dataset.append((row[2], row[3])) 
                    dataset_price.append([[row[0], row[1]],[row[2], row[3]]]) 
            
        case 'code_zones':
            with open(f'{name}.csv', 'r', encoding='windows-1251') as file:
                reader = csv.reader(file, delimiter=';')
                for row in reader:
                    if flag < 9:
                        flag += 1
                        continue
                    if row[3] == row[7]:
                            dataset.append((row[3], row[10]))
                    else:
                        err_flag = True
                        LOG_FILE.append(f'Ошибка: в файле коды зон неправильно заполнена строка, данные из строки не валидны\nЗона: {row[3], row[7], row[10]}')
                        break
            
    if err_flag:
        return None
    else:
        if caller == 'type1':
            return set(dataset), dataset, dataset_price
        if caller == 'type2':
            return dataset, dataset_price 

# def check_zones_diff_mapZones(name):
#     excel_dataset = parce_excel(name)
#     map_names = intersec.zone_names()
#     res_map_ex = set(map_names).difference(excel_dataset)
#     print(f'map - excel {res_map_ex}')
#     LOG_FILE.append(f'map - excel {res_map_ex}')


print('''Подготовтье файлы для проверки (должны лежать в этой же директории с валидатором):
      Карта из яндекса\t->\tmap.geojson
      Тарифы\t\t->\tprice.csv''')
print('\nи нажмите на клавиатуре Enter')

# while not os.path.exists(user_input:=str(input())+'.geojson'):
#     print(f'\n\nВы ввели: {user_input.split(".")[0]}\nКарты с таким именем в этой папке не найдено')
#     print('Попробуйте снова')
    
# os.system('clear')
# print('Считаю')
# intersec = IntersectionResulter(user_input)
# intersec.show_names()
print(input())


print("Проверяю карту...")
LOG_FILE.append("Проверяю карту...")
intersec = IntersectionResulter(f'{MAP_NAME}.geojson')

intersec.find_outside_points()
if intersec.flag_names:
    print('Имена зон на карте проверены, валидно')
    LOG_FILE.append('Имена зон на карте проверены, валидно')
    print()
    LOG_FILE.append('\n')
# intersec.show_names()
# intersec.show_zone_ids()

if intersec.flag_names_region:
    print('Имена зон на карте проверены, валидно')
    LOG_FILE.append('Имена зон на карте проверены, валидно')
    print()
    LOG_FILE.append('\n')
else:
    print('Файлы не сформированы, исправте ошибки')
    LOG_FILE.append('Файлы не сформированы, исправте ошибки')
    print()
    LOG_FILE.append('\n')
    
if intersec.check_points():
    print('Точки на карте проверены, валидно')
    LOG_FILE.append('Точки на карте проверены, валидно')
    print()
    LOG_FILE.append('\n')
# intersec.rename_points()
# intersec.create_json()

def csv_to_excel(csv_file, excel_file):
    csv_data = []
    with open(csv_file) as file_obj:
        reader = csv.reader(file_obj)
        for row in reader:
            csv_data.append(row)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for row in csv_data:
        sheet.append(row)
    workbook.save(excel_file)

if not intersec.flag_alert:

    map_zone_names = intersec.id_name_map_zones
    map_region = intersec.map_region

    price_zones, price_zones_noset, dataset_price = parce_excel(f'{PRICE_NAME}', 'price_zones', 'type1')


    # Проверка зон из карты с зонами в шаблонах
    geojson_id_zones = [x[0] for x in intersec.id_name_map_zones]

    price_zones_ids = [x[0] for x in price_zones]



    for _id in set(geojson_id_zones):
        if _id not in price_zones_ids:
            print(f'Ошибка: На карте есть зона id {_id}, но её нет в файле Тарифы')
            LOG_FILE.append(f'Ошибка: На карте есть зона id {_id}, но её нет в файле Тарифы')

    for _id in set(price_zones_ids):
        if _id not in geojson_id_zones:
            if _id[:6] != map_region:
                print(f'Ошибка: В файле тарифов указана зона {_id} регион этой зоны не входит в текущий регион карты {map_region}')
                LOG_FILE.append(f'Ошибка: В файле тарифов указана зона {_id} регион этой зоны не входит в текущий регион карты {map_region}')
                continue
            print(f'Ошибка: в файле тарифов есть зона id {_id}, но её нет на карте')
            LOG_FILE.append(f'Ошибка: в файле тарифов есть зона id {_id}, но её нет на карте')

    # делаем csv

    data_for_shab_naming = [
        'BAPI_TZSRVSCMB_SAVEMULTI;BAPI_TZSRVSCMB_GETLIST;;;;;;;;;;;;;;;;;;;;',
        ';;;;;;;;;;;;;;;;;;;;;',
        'LOGICAL_SYSTEM;BUSINESS_SYSTEM_GROUP;COMMIT_CONTROL;ZONE_HD;;;;ZONE_DESCRIPTION;;;;LOGICAL_SYSTEM;BUSINESS_SYSTEM_GROUP;LANGUAGE;ZONE_HD;;;;ZONE_DESCRIPTION;;;',
        ';;;;;;;;;;;;;;;;;;;;;',
        'logical_system;business_system_group;commit_control;id_zone_ext;longitude;latitude;del_flag;id_zone_ext;langu;langu_iso;descr;logical_system;business_system_group;language;id_zone_ext;longitude;latitude;del_flag;id_zone_ext;langu;langu_iso;descr',
        'Logical System;Business System Group;COMMIT Control;Transportation Zone: External Zone ID;Transportation Zone: Longitude Geocoordinate;Transportation Zone: Latitude Geocoordinate;Transportation Zone: Deletion Checkbox;Transportation Zone: External Zone ID;Transportation Zone: Language;Transportation Zone: Language ISO Code;Transportation Zone: Zone Description;Logical System;Business System Group;Transportation Zone: Language;Transportation Zone: External Zone ID;Transportation Zone: Longitude Geocoordinate;Transportation Zone: Latitude Geocoordinate;Transportation Zone: Deletion Checkbox;Transportation Zone: External Zone ID;Transportation Zone: Language;Transportation Zone: Language ISO Code;Transportation Zone: Zone Description',
        'bapiscmblogsys;bapiscmblogqs;bapi10004commctrl;bapiscmb0008zoneid;bapiscmb0008zoneycoord;bapiscmb0008zonexcoord;bapiscmb0008zonedelflg;bapiscmb0008zoneid;bapiscmb0008zonelangu;bapiscmb0008zonelanguiso;bapiscmb0008zdescr;bapiscmblogsys;bapiscmblogqs;bapiscmb0008zonelangu;bapiscmb0008zoneid;bapiscmb0008zoneycoord;bapiscmb0008zonexcoord;bapiscmb0008zonedelflg;bapiscmb0008zoneid;bapiscmb0008zonelangu;bapiscmb0008zonelanguiso;bapiscmb0008zdescr',
        'char 000010;char 000008;char 000001;char 000020;dec 000015;dec 000015;char 000001;char 000020;lang 000001;char 000002;char 000040;char 000010;char 000008;lang 000001;char 000020;dec 000015;dec 000015;char 000001;char 000020;lang 000001;char 000002;char 000040',
        'Simple Input Parameter;Simple Input Parameter;Simple Input Parameter;Table Parameters;;;;Table Parameters;;;;Simple Input Parameter;Simple Input Parameter;Simple Input Parameter;Table Parameters;;;;Table Parameters;;;'
    ]

    data_for_ztyt =[
        'BAPI_TRLSRVAPS_SAVEMULTI2;BAPI_TRLSRVAPS_GETLIST2;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;',
        ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;',
        'LOGICAL_SYSTEM;TRANSPORTATION_LANE;;;;;;;;;;;;;;;;;;;;;;;;;;;TRANSPORTATION_LANE_X;;;;;;;;;;;;;;;;;;;;;;;;;;;MEANS_OF_TRANSPORT;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;MEANS_OF_TRANSPORT_X;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;RETURN;;;;;;;;;;;;;',
        ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;',
        'logical_system;model;location_id_from;location_from;loctype_from;location_from_bsg;location_from_int;location_id_to;location_to;loctype_to;location_to_bsg;location_to_int;short_text;planner;order_processing_calendar;communication_duration;order_fixing_period;max_weight;max_weight_uom;max_weight_uom_iso;max_volume;max_volume_uom;max_volume_uom_iso;max_dimension;max_dimension_uom;max_dimension_uom_iso;corr_fix_period;promotion_rounding_rule;model;location_id_from;location_from;loctype_from;location_from_bsg;location_from_int;location_id_to;location_to;loctype_to;location_to_bsg;location_to_int;short_text;planner;order_processing_calendar;communication_duration;order_fixing_period;max_weight;max_weight_uom;max_weight_uom_iso;max_volume;max_volume_uom;max_volume_uom_iso;max_dimension;max_dimension_uom;max_dimension_uom_iso;corr_fix_period;promotion_rounding_rule;model;location_id_from;location_from;loctype_from;location_from_bsg;location_from_int;location_id_to;location_to;loctype_to;location_to_bsg;location_to_int;val_from;val_to;means_of_transport;all_products_flg;aggregated_planning_usage_flg;detailed_planning_usage_flg;short_text;transportation_calendar;distance_dependent_costs;duration;duration_fixing_flg;distance;distance_fixing_flg;stopover_duration;transportation_costs;transportation_costs_uom;transportation_costs_uom_iso;transportation_costs_function;resuid;resource;resource_bsg;resource_int;tlb_profile;discrete_flg;bucket_offset;period_factor;duration_distance_precision;no_stock_in_transit_flg;vmi_tlb_profile;default_order_guideline_set;order_guideline_set;loading_method;rule_tolerance;pull_in_horizon;sizing_decision;sizing_thrval;bus_share_tol_pos;bus_share_tol_neg;bus_share_penalty_or;bus_share_penalty_uu;bus_share_usage_flg;capacity_basis;capacity_usage_flg;cost_origin;tsp_selection_strategy;continous_move_type;buckets_profile;tsp_selection_flg;proc_lead_time_pull;proc_lead_time_push;stk_transfer_time_pull;stk_transfer_time_push;min_distance_dependent_costs;model;location_id_from;location_from;loctype_from;location_from_bsg;location_from_int;location_id_to;location_to;loctype_to;location_to_bsg;location_to_int;val_from;val_to;means_of_transport;all_products_flg;aggregated_planning_usage_flg;detailed_planning_usage_flg;short_text;transportation_calendar;distance_dependent_costs;duration;duration_fixing_flg;distance;distance_fixing_flg;stopover_duration;transportation_costs;transportation_costs_uom;transportation_costs_uom_iso;transportation_costs_function;resuid;resource;resource_bsg;resource_int;tlb_profile;discrete_flg;bucket_offset;period_factor;duration_distance_precision;no_stock_in_transit_flg;vmi_tlb_profile;default_order_guideline_set;order_guideline_set;loading_method;rule_tolerance;pull_in_horizon;sizing_decision;sizing_thrval;bus_share_tol_pos;bus_share_tol_neg;bus_share_penalty_or;bus_share_penalty_uu;bus_share_usage_flg;capacity_basis;capacity_usage_flg;cost_origin;tsp_selection_strategy;continous_move_type;buckets_profile;tsp_selection_flg;proc_lead_time_pull;proc_lead_time_push;stk_transfer_time_pull;stk_transfer_time_push;min_distance_dependent_costs;type;id;number;message;log_no;log_msg_no;message_v1;message_v2;message_v3;message_v4;parameter;row;field;system',
        'Logical System;Model Name in Supply Chain Network;Location GUID (Length 32);External Location Identifier;Location Type;Business System Group;Location;Location GUID (Length 32);External Location Identifier;Location Type;Business System Group;Location;Transportation Lane Description;Transportation Planner;Order Processing Calendar;Communication Duration;Order Fixing Period;Deployment: Maximum Weight for Express Shipment Decision;Unit of Weight;ISO code for unit of measurement;Deployment: Maximum Volume for Express Shipment Decision;Unit of Volume;ISO code for unit of measurement;Deployment: Maximum Dimension for Express Shipment Decision;Unit of Dimension;ISO code for unit of measurement;Correction of Freeze Period;Special Promotion Rounding Rule;Model Name in Supply Chain Network;Location GUID (Length 32);External Location Identifier;Location Type;Business System Group;Location;Location GUID (Length 32);External Location Identifier;Location Type;Business System Group;Location;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Model Name in Supply Chain Network;Location GUID (Length 32);External Location Identifier;Location Type;Business System Group;Location;Location GUID (Length 32);External Location Identifier;Location Type;Business System Group;Location;Time Stamp at Start of Validity Period;Time Stamp at End of Validity Period;Means of Transport;Indicator: Whether Means of Transport Valid for All Products;Indicator for Use in Aggregated Planning;Indicator for Usage in Detailed Planning;Description of Means of Transport from a Transportation Lane;Transportation Calendar;Distance-Dependent Costs of a Means of Transport (per km);Transportation Time of a Transportation Lane (in hhmmss);Indicator for Fixing the Duration of Transportation;Transportation Distance of a Transportation Lane in km;Indicator to Fix Transportation Distance;Additional Retention Period for Transp. Lane (in hhmmss);Variable Transportation Costs;Unit of Measure for Transportation Costs of a Product;ISO code for unit of measurement;Supply Network Planning: External Cost Function;Resources GUID (Length 32);External Resource;Business System Group;Resource Name;SNP: Profile for Transport Load Builder (old);SNP Optimizer: Discrete Means of Transport at Transp. Lane;Bucket Offset for Product Availability During Shipment;Period Factor for Calculating the Availability Date/Time;Precision of Distance and Duration at Transportation Lane;Do Not Create Stock in Transit;TLB Profile;TLB: Default Order Guideline Set;TLB: Set of Transportation Guidelines;Loading Method;Multiplier for Minimum Load for Direct Delivery;TLB: Pull-In Horizon;TLB: Decision Basis for Shipment Sizing;TLB: Threshold Value for Shipment Sizing;Business Share: Positive Tolerance;Business Share: Negative Tolerance;Penalty Costs for Exceeding Tolerance;Penalty Costs for Tolerance Shortfall;Use Business Share;Capacity Basis;Use Transportation Allocations;Cost Origin;Strategy for Transportation Service Provider Selection;Continuous Move Type;Planning Period;Relevant to TSP Selection;Total Procurement Lead Time (Pull);Total Procurement Lead Time (Push);Total Stock Transfer Time (Pull);Total Stock Transfer Time (Push);Minimal Distance-Dependent Costs of a Means of Transport;Model Name in Supply Chain Network;Location GUID (Length 32);External Location Identifier;Location Type;Business System Group;Location;Location GUID (Length 32);External Location Identifier;Location Type;Business System Group;Location;Time Stamp at Start of Validity Period;Time Stamp at End of Validity Period;Means of Transport;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Updated information in related user data field;Message type: S Success, E Error, W Warning, I Info, A Abort;Message Class;Message Number;Message Text;Application log: log number;Application log: Internal message serial number;Message Variable;Message Variable;Message Variable;Message Variable;Parameter Name;Lines in parameter;Field in parameter;Logical system from which message originates',
        'bapiscmblogsys;/sapapo/c_modelid;bapi10002locid_32;/sapapo/ext_locno;/sapapo/c_loctype;/sapapo/logqs;/sapapo/locno;bapi10002locid_32;/sapapo/ext_locno;/sapapo/c_loctype;/sapapo/logqs;/sapapo/locno;/sapapo/tr_trdescr;/sapapo/planner_trans;/sapapo/tr_opcal;/sapapo/tr_comm_dura;/sapapo/tr_perd_no_ordchg;/sapapo/tr_dpl_wgt_lim;/sapapo/tr_dpl_wgt_uom;isocd_unit;/sapapo/tr_dpl_vol_lim;/sapapo/tr_dpl_vol_uom;isocd_unit;/sapapo/tr_dpl_lwh_lim;/sapapo/tr_dpl_lwh_uom;isocd_unit;/sapapo/tr_corr_fix_perd;/sapapo/tr_promo_round_rule;/sapapo/c_modelid;bapi10002locid_32;/sapapo/ext_locno;/sapapo/c_loctype;/sapapo/logqs;/sapapo/locno;bapi10002locid_32;/sapapo/ext_locno;/sapapo/c_loctype;/sapapo/logqs;/sapapo/locno;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;/sapapo/c_modelid;bapi10002locid_32;/sapapo/ext_locno;/sapapo/c_loctype;/sapapo/logqs;/sapapo/locno;bapi10002locid_32;/sapapo/ext_locno;/sapapo/c_loctype;/sapapo/logqs;/sapapo/locno;/sapapo/scc_valfromtstmp;/sapapo/scc_valtotstmp;/sapapo/tr_traty;/sapapo/tr_allprodtflag;/sapapo/tr_aggplflg;/sapapo/tr_dtlplflg;/sapapo/tr_trmdescr;/sapapo/trcal;/sapapo/tr_trtypecost;bapi11201trmdurat;/sapapo/tr_durflg;/sapapo/tr_dist;/sapapo/tr_distflg;bapi11201trmstopdurat;/sapapo/tr_trcost;/sapapo/tr_trcostunit;/sapapo/isocd_unit;/sapapo/snpcosex;bapi10004resid_32;bapi10004ext_resname;/sapapo/logqs;/sapapo/cres_name;/sapapo/snptprex;/sapapo/snptdisc;/sapapo/snprndtrp;/sapapo/rrp_req_cover_type;/sapapo/tr_prec;/sapapo/tr_nstkit;/scmb/vtprid;/scmb/vtosiddef;/scmb/vtosid;/scmb/vt_loadsel;/scmb/vt_ordtol;/scmb/vt_pihor;/scmb/vt_sizedec;/scmb/vt_sizeth;/sapapo/tr_bstol_pos;/sapapo/tr_bstol_neg;/sapapo/tr_bspen_or;/sapapo/tr_bspen_uu;/sapapo/tr_bsuse;/sapapo/tr_cpbase;/sapapo/tr_cpuse;/sapapo/tr_cobase;/sapapo/tr_stbase;/sapapo/tr_cmbase;/sapapo/tr_tbbuom;/sapapo/tr_usage_carrsel;/sapapo/tr_drp_depl_lt_pull;/sapapo/tr_drp_depl_lt_push;/sapapo/tr_sto_sttr_lt_pull;/sapapo/tr_sto_sttr_lt_push;/sapapo/tr_trtypecost_min;/sapapo/c_modelid;bapi10002locid_32;/sapapo/ext_locno;/sapapo/c_loctype;/sapapo/logqs;/sapapo/locno;bapi10002locid_32;/sapapo/ext_locno;/sapapo/c_loctype;/sapapo/logqs;/sapapo/locno;/sapapo/scc_valfromtstmp;/sapapo/scc_valtotstmp;/sapapo/tr_traty;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapiupdate;bapi_mtype;symsgid;symsgno;bapi_msg;balognr;balmnr;symsgv;symsgv;symsgv;symsgv;bapi_param;bapi_line;bapi_fld;bapilogsys',
        'char 000010;char 000022;char 000032;char 000020;char 000004;char 000008;char 000020;char 000032;char 000020;char 000004;char 000008;char 000020;char 000040;char 000003;char 000010;dec 000011;dec 000011;quan 000013;unit 000003;char 000003;quan 000013;unit 000003;char 000003;quan 000013;unit 000003;char 000003;dec 000004;numc 000001;char 000022;char 000032;char 000020;char 000004;char 000008;char 000020;char 000032;char 000020;char 000004;char 000008;char 000020;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000022;char 000032;char 000020;char 000004;char 000008;char 000020;char 000032;char 000020;char 000004;char 000008;char 000020;dec 000015;dec 000015;char 000010;char 000001;char 000001;char 000001;char 000040;char 000010;dec 000013;dec 000011;char 000001;dec 000010;char 000001;dec 000011;dec 000015;unit 000003;char 000003;char 000010;char 000032;char 000040;char 000008;char 000040;char 000010;char 000001;dec 000003;dec 000004;numc 000004;char 000001;char 000010;char 000010;char 000010;char 000001;dec 000003;dec 000003;char 000001;dec 000003;dec 000004;dec 000004;dec 000013;dec 000013;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;dec 000011;dec 000011;dec 000011;dec 000011;dec 000013;char 000022;char 000032;char 000020;char 000004;char 000008;char 000020;char 000032;char 000020;char 000004;char 000008;char 000020;dec 000015;dec 000015;char 000010;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000001;char 000020;numc 000003;char 000220;char 000020;numc 000006;char 000050;char 000050;char 000050;char 000050;char 000032;int4 000010;char 000030;char 000010',
        'Simple Input Parameter;Table Parameters;;;;;;;;;;;;;;;;;;;;;;;;;;;Table Parameters;;;;;;;;;;;;;;;;;;;;;;;;;;;Table Parameters;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;Table Parameters;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;Table Parameters;;;;;;;;;;;;;'
    ]

    with open('Шаблон коды зон.csv', 'w', newline='', encoding='windows-1251') as codefile:
        writer = csv.writer(codefile, delimiter=';', dialect='excel')
        print()
        print('Формирую файл Шаблон коды зон.csv')            
        LOG_FILE.append('\n')  
        LOG_FILE.append('Формирую файл Шаблон коды зон.csv')  
        for line in data_for_shab_naming:
            dat = line.split(';')
            writer.writerow(dat)
        flg = 0
        for _zone_id, _zone_name in map_zone_names:
            if not flg:
                tmp = f'TP0CLNT600;SPKTM;A;{_zone_id};0;0;;{_zone_id};R;RU;{_zone_name};;;;;;;;;;;'
                temp = tmp.split(';')
                writer.writerow(temp)
                flg = 1
                continue
            tmp = f';;A;{_zone_id};0;0;;{_zone_id};R;RU;{_zone_name};;;;;;;;;;;'
            temp = tmp.split(';')
            writer.writerow(temp)


    with open('Шаблон YT.csv', 'w', newline='', encoding='windows-1251') as codefile:
        writer = csv.writer(codefile, delimiter=';', dialect='excel')
        print()
        print('Формирую файл Шаблон YT.csv')            
        LOG_FILE.append('\n')  
        LOG_FILE.append('Формирую файл Шаблон YT.csv') 
        for line in data_for_ztyt:
            dat = line.split(';')
            writer.writerow(dat)
        flg = 0
        for _el in dataset_price:
            el_fr = _el[0][0][0:6] 
            el_to = _el[1][0][0:6]
            if el_fr != map_region or el_to != map_region:
                continue
            el_fr = [_el[0][0],'n']
            el_to = [_el[1][0],'n']
            for zon_name in map_zone_names:
                if zon_name[0] == el_fr[0]:
                    el_fr[1] = zon_name[1]
                    if zon_name[0] == el_to[0]:
                        el_to[1] = zon_name[1]
                elif zon_name[0] == el_to[0]:
                    el_to[1] = zon_name[1]
                    if zon_name[0] == el_fr[0]:
                        el_fr[1] = zon_name[1]
            if el_fr[1] == 'n':
                print(f'Шаблон YT.csv - зона прибытия {el_fr} - не сформирован, не нашлось такой же зоны в файле карт')
                print('Файл Шаблон YT.csv - не сформирован, добавьте отсутствующие зоны на карту')
                LOG_FILE.append(f'зона прибытия{el_fr} - не сформирован, не нашлось такой же зоны в файле карт')
                LOG_FILE.append('Файл Шаблон YT.csv - не сформирован, добавьте отсутствующие зоны на карту')
                save_log()
            if el_to[1] == 'n':
                print(f'Шаблон YT.csv - зона прибытия {el_to} - не сформирован, не нашлось такой же зоны в файле карт')
                print('Файл Шаблон YT.csv - не сформирован, добавьте отсутствующие зоны на карту')
                LOG_FILE.append(f'зона прибытия{el_to} - не сформирован, не нашлось такой же зоны в файле карт')
                LOG_FILE.append('Файл Шаблон YT.csv - не сформирован, добавьте отсутствующие зоны на карту')
                save_log()

            el_fr_ty = int(el_fr[1][:1])
            el_to_ty = int(el_to[1][:1])

            cargo_type = el_fr_ty or el_to_ty
            crg = 'Город' if not cargo_type else 'Междугородняя'
            if not flg:
                tmp = f'TP0CLNT600;000;;{el_fr[0]};1005;SPKTM;{el_fr[0]};;{el_to[0]};1005;SPKTM;{el_to[0]};{crg};;;0;1;0;;;0;;;0;;;0;0;000;;;;;;;;;;;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;000;;{el_fr[0]};1005;SPKTM;{el_fr[0]};;{el_to[0]};1005;SPKTM;{el_to[0]};20120122000000;99990101235959;YT;X;X;X;{crg};;0,000;0;;0;;0;0;;;;;;;;;;0;0;1000;;;;;;0;0;;0;0;0;0;0;;P;;I;X;;;X;0;0;0;0;0;000;;;;;;;;;;;0;0;;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;;;;;;;;;;;;;;'
                temp = tmp.split(';')
                writer.writerow(temp)
                flg = True
                continue
            tmp = f';000;;{el_fr[0]};1005;SPKTM;{el_fr[0]};;{el_to[0]};1005;SPKTM;{el_to[0]};{crg};;;0;1;0;;;0;;;0;;;0;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;000;;{el_fr[0]};1005;SPKTM;{el_fr[0]};;{el_to[0]};1005;SPKTM;{el_to[0]};20120122000000;99990101235959;YT;X;X;X;{crg};;0,000;0;;0;;0;0;;;;;;;;;;0;0;1000;;;;;;0;0;;0;0;0;0;0;;P;;I;X;;;X;0;0;0;0;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'
            temp = tmp.split(';')
            writer.writerow(temp)

    with open('Шаблон ZT.csv', 'w', newline='', encoding='windows-1251') as codefile:
        writer = csv.writer(codefile, delimiter=';', dialect='excel')
        print()
        print('Формирую файл Шаблон ZT.csv')            
        LOG_FILE.append('\n')  
        LOG_FILE.append('Формирую файл Шаблон ZT.csv') 
        for line in data_for_ztyt:
            dat = line.split(';')
            writer.writerow(dat)
        flg = 0
        for _el in dataset_price:
            el_fr = _el[0][0][0:6] 
            el_to = _el[1][0][0:6]
            if el_fr != map_region or el_to != map_region:
                continue
            el_fr = [_el[0][0],'n']
            el_to = [_el[1][0],'n']
            for zon_name in map_zone_names:
                if zon_name[0] == el_fr[0]:
                    el_fr[1] = zon_name[1]
                    if zon_name[0] == el_to[0]:
                        el_to[1] = zon_name[1]
                elif zon_name[0] == el_to[0]:
                    el_to[1] = zon_name[1]
                    if zon_name[0] == el_fr[0]:
                        el_fr[1] = zon_name[1]
            if el_fr[1] == 'n':
                print(f'Шаблон ZT.csv - зона прибытия {el_fr} - не сформирован, не нашлось такой же зоны в файле карт')
                print('Файл Шаблон ZT.csv - не сформирован, добавьте отсутствующие зоны на карту')
                LOG_FILE.append(f'зона прибытия{el_fr} - не сформирован, не нашлось такой же зоны в файле карт')
                LOG_FILE.append('Файл Шаблон ZT.csv - не сформирован, добавьте отсутствующие зоны на карту')
                save_log()
            if el_to[1] == 'n':
                print(f'Шаблон ZT.csv - зона прибытия {el_to} - не сформирован, не нашлось такой же зоны в файле карт')
                print('Файл Шаблон ZT.csv - не сформирован, добавьте отсутствующие зоны на карту')
                LOG_FILE.append(f'зона прибытия{el_to} - не сформирован, не нашлось такой же зоны в файле карт')
                LOG_FILE.append('Файл Шаблон ZT.csv - не сформирован, добавьте отсутствующие зоны на карту')
                save_log()
            el_fr_ty = int(el_fr[1][:1])
            el_to_ty = int(el_to[1][:1])
            cargo_type = el_fr_ty or el_to_ty
            crg = 'Город' if not cargo_type else 'Междугородняя'
            if not flg:
                tmp = f'TP0CLNT600;000;;{el_fr[0]};1005;SPKTM;{el_fr[0]};;{el_to[0]};1005;SPKTM;{el_to[0]};{crg};;;0;1;0;;;0;;;0;;;0;0;000;;;;;;;;;;;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;000;;{el_fr[0]};1005;SPKTM;{el_fr[0]};;{el_to[0]};1005;SPKTM;{el_to[0]};20120122000000;99990101235959;ZT;X;X;X;{crg};;0,000;0;;0;;0;0;;;;;;;;;;0;0;1000;;;;;;0;0;;0;0;0;0;0;;P;;I;X;;;X;0;0;0;0;0;000;;;;;;;;;;;0;0;;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;;;;;;;;;;;;;;'
                temp = tmp.split(';')
                writer.writerow(temp)
                flg = True
                continue
            tmp = f';000;;{el_fr[0]};1005;SPKTM;{el_fr[0]};;{el_to[0]};1005;SPKTM;{el_to[0]};{crg};;;0;1;0;;;0;;;0;;;0;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;000;;{el_fr[0]};1005;SPKTM;{el_fr[0]};;{el_to[0]};1005;SPKTM;{el_to[0]};20120122000000;99990101235959;ZT;X;X;X;{crg};;0,000;0;;0;;0;0;;;;;;;;;;0;0;1000;;;;;;0;0;;0;0;0;0;0;;P;;I;X;;;X;0;0;0;0;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'
            temp = tmp.split(';')
            writer.writerow(temp)

    with open('price.csv', 'r', encoding='windows-1251') as file:
        reader = csv.reader(file, delimiter=';')
        temporary =[]
        flag = 1
        for row in reader:
            if flag:
                flag = 0
                temporary.append(row)
                continue
            if row[0][:6] == map_region and row[2][:6] == map_region:
                if any(row[4:]):
                    temporary.append(row)
                else:
                    print(f'В генерируемом файле тарифов не добавлен прайс {row[0]}  -  {row[2]}, т.к. он пуст')    
                    LOG_FILE.append(f'В генерируемом файле тарифов не добавлен прайс {row[0]}  -  {row[2]}, т.к. он пуст') 
            else:
                print(f'В генерируемом файле тарифов не добавлен прайс {row[0]}  -  {row[2]}, т.к. он не входит в регион карты {map_region}')    
                LOG_FILE.append(f'В генерируемом файле тарифов не добавлен прайс {row[0]}  -  {row[2]}, т.к. он не входит в регион карты {map_region}')    
            
        for root1 in map_zone_names:
            for i in range(len(temporary)):
                if root1[0] == temporary[i][0]:
                    temporary[i][1] = root1[1]
                if root1[0] == temporary[i][2]:
                    temporary[i][3] = root1[1]

        with open('Прайс_сгенерировано.csv', 'w', newline='', encoding='windows-1251') as codefile:
            writer = csv.writer(codefile, delimiter=';', dialect='excel')
            print()
            print('Формирую файл Прайс_сгенерировано.csv')            
            LOG_FILE.append('\n')  
            LOG_FILE.append('Формирую файл Прайс_сгенерировано.csv')
            writer.writerows(temporary)
            
    csv_to_excel('Шаблон коды зон.csv', 'Шаблон коды зон.xlsx')
    csv_to_excel('Шаблон YT.csv', 'Шаблон YT.csv.xlsx')
    csv_to_excel('Шаблон ZT.csv', 'Шаблон ZT.xlsx')
    csv_to_excel('Прайс_сгенерировано.csv', 'Прайс_сгенерировано.xlsx')

                
            
else:
    print('Файлы для загрузки не созданы, исправте ошибки')            
    LOG_FILE.append('Файлы для загрузки не созданы, исправте ошибки')            


print("====DONE====\n")
LOG_FILE.append("====DONE====\n")
save_log()






# OLD CODE

# xls_name = 'price_samara.xlsx'
# sheet_n = pd.ExcelFile(xls_name).sheet_names[0]
# xls = pd.read_excel(xls_name, sheet_name = sheet_n)

# from_data = [x for x in xls['   Код Геозоны отправления']]
# to_data = [x for x in xls['   Код Геозоны прибытия']]
# all_set = list(set(from_data + to_data))
# region = ''

# date_time = dt.now().strftime("%d.%m.%Y, %H:%M")
# все <-> все кроме все -> ПЦС
# for i in all_set:
#     if '-0001' in i:
#         region = i[4:6]
#         break
# for i in all_set:
#     if region != i[4:6]:
#         if 'TZRU00' not in i.upper():
#             all_set.remove(i)
# all_combo = [(x,y) for x in all_set for y in all_set if x != y]

# МБ<->все
# for i in all_set:
#     if '-0001' in i:
#         region = i[4:6]
#         mb = i
#         break









# all_combo_fmb = [(mb, x) for x in all_set if mb != x]
# all_combo_tmb = [(x, mb) for x in all_set if mb != x]
# all_combo = all_combo_fmb + all_combo_tmb


# with open('shab_tr_ont.csv', 'a', newline='') as file:
#     first_line = 'TP0CLNT600;000;;TZRU66-0001;1005;SPKTM;TZRU66-0001;;TZRU66-0002;1005;SPKTM;TZRU66-0002;Test route;;;0;1;0;;;0;;;0;;;0;0;000;;;;;;;;;;;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;000;;TZRU66-0001;1005;SPKTM;TZRU66-0001;;TZRU66-0002;1005;SPKTM;TZRU66-0002;20120122000000;99990101235959;YT;X;X;X;Test route;;0,000;0;;0;;0;0;;;;;;;;;;0;0;1000;;;;;;0;0;;0;0;0;0;0;;P;;I;X;;;X;0;0;0;0;0;000;;;;;;;;;;;0;0;;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;;;;;;;;;;;;;;'
#     last_line = ';000;;TZRU66-0001;1005;SPKTM;TZRU66-0001;;TZRU66-0003;1005;SPKTM;TZRU66-0003;Test route;;;0;1;0;;;0;;;0;;;0;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;000;;TZRU66-0001;1005;SPKTM;TZRU66-0001;;TZRU66-0003;1005;SPKTM;TZRU66-0003;20120122000000;99990101235959;YT;X;X;X;Test route;;0,000;0;;0;;0;0;;;;;;;;;;0;0;1000;;;;;;0;0;;0;0;0;0;0;;P;;I;X;;;X;0;0;0;0;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'
#     writer = csv.writer(file, delimiter=';', dialect='excel')
#     fl = 0
#     for f,t in all_combo:
#         if not fl:
#             first_line = first_line.split(';')
#             first_line[3], first_line[6], first_line[8], first_line[11], first_line[12] = f, f, t, t, date_time
#             first_line[57], first_line[60], first_line[62], first_line[65], first_line[72] = f, f, t, t, date_time
#             writer.writerow(first_line)
#             fl += 1
#             continue
#         if 'TZRU00' in t.upper():
#             continue
#         last_line2 = last_line.split(';')
#         last_line2[3], last_line2[6], last_line2[8], last_line2[11], last_line2[12] = f, f, t, t, date_time
#         last_line2[57], last_line2[60], last_line2[62], last_line2[65], last_line2[72] = f, f, t, t, date_time
#         writer.writerow(last_line2)

LOG_FILE = []
print("\n============\nРасширенная проверка созданных файлов\n")
LOG_FILE.append("\n============\nРасширенная проверка созданных файлов\n")

if intersec.flag_names_region and not intersec.flag_alert:
    print("Импортирую файл Шаблон YT")
    LOG_FILE.append("Импортирую файл Шаблон YT")
    try:
        yt, yt_noset = parce_excel('Шаблон YT', 'yt', 'type2')
    except:
        print('Не найден файл Шаблон YT.csv')
        LOG_FILE.append('Не найден файл Шаблон YT.csv')
        save_log(2)
    print("Импортирую файл Прайс_сгенерировано")
    LOG_FILE.append("Импортирую файл Прайс_сгенерировано")
    try:
        price, price_noset = parce_excel('Прайс_сгенерировано', 'price', 'type2')
    except:
        print('Не найден файл Прайс_сгенерировано.csv')
        LOG_FILE.append('Не найден файл Прайс_сгенерировано.csv')
        save_log(2)
    price_zones, price_zones_noset = parce_excel('Прайс_сгенерировано', 'price_zones', 'type2')
    print("Импортирую файл Шаблон коды зон.csv\n")
    LOG_FILE.append("Импортирую файл Шаблон коды зон.csv\n")
    try:
        code_zones, code_zones_noset = parce_excel('Шаблон коды зон', 'code_zones', 'type2')
    except:
        print('Не найден файл Шаблон коды зон.csv')
        LOG_FILE.append('Не найден файл Шаблон коды зон.csv')
        save_log(2)

    code_zones_shab_ids = [x[0] for x in code_zones]
        
    code_price_zones = sorted(list(price_zones))    
    code_zones_zo = sorted(list(code_zones)) 

    # Проверка  повторения id зон в шаблонах
    for el in price:
        if price.count(el)>1:
            print(f'Ошибка: в файле Тарифы найдено повторение тарифа из {el[0]} в {el[1]}')
            LOG_FILE.append(f'Ошибка: в файле Тарифы найдено повторение тарифа из {el[0]} в {el[1]}')
            price.remove(el)
    for el in yt:
        if yt.count(el)>1:
            print(f'Ошибка: в файле yt/zt найдено повторение трансп. отношения из {el[0]} в {el[1]}')
            LOG_FILE.append(f'Ошибка: в файле yt/zt найдено повторение трансп. отношения из {el[0]} в {el[1]}')
            yt.remove(el)
    for el in code_zones_shab_ids:
        if tuple(code_zones_shab_ids).count(el)>1:
            print(f'Ошибка: в файле Шаблон коды зон найдено повторение id зоны {el}')
            LOG_FILE.append(f'Ошибка: в файле Шаблон коды зон найдено повторение id зоны {el}')
            code_zones_shab_ids.remove(el)
            


    # Проверка названия зон в шаблонах
    pr_fl = True
    for i in code_price_zones:
        if i[0][0:6] != map_region:
            print(f'Ошибка: в карте с регионом {map_region} найдена зона {i[0]}, с названием {i[1]}')
            LOG_FILE.append(f'Ошибка: в карте с регионом {map_region} найдена зона {i[0]}, с названием {i[1]}')
        else:
            for j in code_zones_zo:
                if i[0] == j[0]:
                    if i[1] != j[1]:
                        if pr_fl:
                            print()
                            LOG_FILE.append('\n')
                            print('Найдена неточность: найдены различия в названии зон в файлах Тарифы и Шаблон коды зон')
                            LOG_FILE.append('Найдена неточность: найдены различия в названии зон в файлах Тарифы и Шаблон коды зон')
                            pr_fl = False
                        print(f'В файле Тарифы id:"{i[0]}", название:"{i[1]}"\nА в Шаблоне коды зон: "{j[1]}"\n')
                        LOG_FILE.append(f'В файле Тарифы id:"{i[0]}", название:"{i[1]}"\nА в Шаблоне коды зон: "{j[1]}"\n')
    pr_fl1 = True
    id_z_cod_zones = [x[0] for x in code_zones]
    for i in code_price_zones:
        if i[0][:6] == map_region:
            if i[0] not in id_z_cod_zones:
                if pr_fl1:
                    ppr_fl1 = False
                print(f'Ошибка: в файле Шаблон код зон не найдена зона {i[0]} с названием {i[1]}')
                LOG_FILE.append(f'Ошибка: в файле Шаблон код зон не найдена зона {i[0]} с названием {i[1]}')
    print()
    LOG_FILE.append('\n')
    # Проверка на наличие в файле zt/yt
    a = set(price)
    b = set(yt)
    if temp_1:=set(price) - set(yt):
        t_l = [x for x in temp_1 if x[0][0:6] == map_region]
        if len(t_l)>1:
            print('Найдена ошибка: в файле кодов отношения зон (yt/zt) нет отношения:')
            LOG_FILE.append('Найдена ошибка: в файле кодов отношения зон (yt/zt) нет отношения:')
            for i in t_l:
                print(f'из {i[0]} в {i[1]}')
                LOG_FILE.append(f'из {i[0]} в {i[1]}')
        elif len(t_l) == 1:
            print(f'Найдена ошибка: в файле кодов отношения зон (yt/zt) нет отношения из {t_l[0][0]} в {t_l[0][1]}')
            LOG_FILE.append(f'Найдена ошибка: в файле кодов отношения зон (yt/zt) нет отношения из {t_l[0][0]} в {t_l[0][1]}')
    print()
    LOG_FILE.append('\n')

    # Проверка зон из карты с зонами в шаблонах
    geojson_id_zones = [x[0] for x in intersec.id_name_map_zones]
    yt_id_zones = []
    for i,j in yt:
        yt_id_zones.append(i)
        yt_id_zones.append(j)
    price_zones_ids = [x[0] for x in price_zones]

    for _id in set(geojson_id_zones):
        if _id not in code_zones_shab_ids:
            print(f'Ошибка: на карте есть зона id {_id}, но её нет в файле Шаблон коды зон')
            LOG_FILE.append(f'Ошибка: на карте есть зона id {_id}, но её нет в файле Шаблон коды зон')
            
    for _id in set(geojson_id_zones):
        if _id not in yt_id_zones:
            print(f'Ошибка: на карте есть зона id {_id}, но её нет в файле трансп. отношений yt/zt')
            LOG_FILE.append(f'Ошибка: на карте есть зона id {_id}, но её нет в файле трансп. отношений yt/zt')

    for _id in set(geojson_id_zones):
        if _id not in price_zones_ids:
            print(f'Ошибка: на карте есть зона id {_id}, но её нет в файле Тарифы')
            LOG_FILE.append(f'Ошибка: на карте есть зона id {_id}, но её нет в файле Тарифы')
    save_log(2)
else:
    print("\n============\nРасширенная проверка созданных файлов не пройдена - исправте ошибки\n")
    LOG_FILE.append("\n============\nРасширенная проверка созданных файлов не пройдена - исправте ошибки\n")
    save_log(2)