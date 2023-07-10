import os
import shutil


dirWork = 'D:/Projects/InsiTech/botProject/Adminka/LecalaConverter/fed/'
f = open(dirWork + 'validator_report.txt', encoding='utf-8', mode='r')
# работа с файлом
all = f.readlines() 
counter = 0
counterBad = 0
for index in range(len(all)):
    if 'No errors detected' in all[index]:
        str = all[index-1]
        start = str.find('INFO:')
        if start > 0 :
            name = str[start + 6:-1]
            try:            
                shutil.copy(
                    os.path.join(dirWork + 'outSvgDemo', name),
                    os.path.join(dirWork + 'out')
                )
                counter = counter + 1
            except:
                counterBad = counterBad + 1
f.close()