import csv

def parce_excel(name):
    dataset = []
    with open(f'{name}.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        flag = 0
        err_flag = 0
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
            
    if err_flag:
        return None
    else:
        return set(dataset)