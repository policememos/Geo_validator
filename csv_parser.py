import csv

def parce_excel(name, _type):
    dataset = []
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
                            err_flag = True
                            break
                    else:
                        print(f'Ошибка: в файле отношений зон неправильно заполнена строка, данные из строки не валидны\nЗона отбытия: {row[3], row[6], row[57], row[60]}')
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
                        print(f'Ошибка: в файле коды зон неправильно заполнена строка, данные из строки не валидны\nЗона: {row[3], row[7], row[10]}')
                        err_flag = True
                        break

            
            
    if err_flag:
        return None
    else:
        return set(dataset)