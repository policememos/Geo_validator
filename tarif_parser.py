import csv

def parce_excel(name):
    dataset = []
    with open(f'{name}.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        flag = 1
        for row in reader:
            if flag:
                flag = 0
                continue
            dataset.append(row[0])
            dataset.append(row[2])    
    return set(dataset)

