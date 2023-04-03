# from datetime import datetime as dt
import csv
# from itertools import combinations
import pandas as pd

# with open()


xls_name = 'price_samara.xlsx'
sheet_n = pd.ExcelFile(xls_name).sheet_names[0]
xls = pd.read_excel(xls_name, sheet_name = sheet_n)

from_data = [x for x in xls['   Код Геозоны отправления']]
to_data = [x for x in xls['   Код Геозоны прибытия']]
all_set = list(set(from_data + to_data))
region = ''
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
for i in all_set:
    if '-0001' in i:
        region = i[4:6]
        mb = i
        break

for raw in xls:
    print(raw)




all_combo_fmb = [(mb, x) for x in all_set if mb != x]
all_combo_tmb = [(x, mb) for x in all_set if mb != x]
all_combo = all_combo_fmb + all_combo_tmb


with open('shab_tr_ont.csv', 'a', newline='') as file:
    first_line = 'TP0CLNT600;000;;TZRU66-0001;1005;SPKTM;TZRU66-0001;;TZRU66-0002;1005;SPKTM;TZRU66-0002;Test route;;;0;1;0;;;0;;;0;;;0;0;000;;;;;;;;;;;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;000;;TZRU66-0001;1005;SPKTM;TZRU66-0001;;TZRU66-0002;1005;SPKTM;TZRU66-0002;20120122000000;99990101235959;YT;X;X;X;Test route;;0,000;0;;0;;0;0;;;;;;;;;;0;0;1000;;;;;;0;0;;0;0;0;0;0;;P;;I;X;;;X;0;0;0;0;0;000;;;;;;;;;;;0;0;;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;X;;;;;;;;;;;;;;'
    last_line = ';000;;TZRU66-0001;1005;SPKTM;TZRU66-0001;;TZRU66-0003;1005;SPKTM;TZRU66-0003;Test route;;;0;1;0;;;0;;;0;;;0;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;000;;TZRU66-0001;1005;SPKTM;TZRU66-0001;;TZRU66-0003;1005;SPKTM;TZRU66-0003;20120122000000;99990101235959;YT;X;X;X;Test route;;0,000;0;;0;;0;0;;;;;;;;;;0;0;1000;;;;;;0;0;;0;0;0;0;0;;P;;I;X;;;X;0;0;0;0;0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'
    writer = csv.writer(file, delimiter=';', dialect='excel')
    fl = 0
    for f,t in all_combo:
        if not fl:
            first_line = first_line.split(';')
            first_line[3], first_line[6], first_line[8], first_line[11], first_line[12] = f, f, t, t, date_time
            first_line[57], first_line[60], first_line[62], first_line[65], first_line[72] = f, f, t, t, date_time
            writer.writerow(first_line)
            fl += 1
            continue
        if 'TZRU00' in t.upper():
            continue
        last_line2 = last_line.split(';')
        last_line2[3], last_line2[6], last_line2[8], last_line2[11], last_line2[12] = f, f, t, t, date_time
        last_line2[57], last_line2[60], last_line2[62], last_line2[65], last_line2[72] = f, f, t, t, date_time
        writer.writerow(last_line2)