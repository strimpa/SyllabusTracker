import csv
from .models import Exercise, ExerciseGroup
import sys, traceback

import io  # python 3 only

def handle_csv_data(csv_file):
    csv_file = io.TextIOWrapper(csv_file)  # python 3 only
    dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=";,")
    csv_file.seek(0)
    reader = csv.reader(csv_file, dialect)
    return list(reader)
    
def handle_uploaded_file(f):
    file_data = f.read().decode("utf-8")		
    lines = file_data.split("\n")
    for line in lines:
        csvalues = str(line).split(',')
        num_cols = len(csvalues)
        if num_cols < 2:
            return ("Line contains less comma-separated values than 2 or more than maximum:"+line)
        #try:
        ex, created = Exercise.objects.get_or_create(name=csvalues[0].strip())
        if created:
            ex.description = csvalues[1].strip()
            ex.save()

        last_group = None
        if num_cols>2:
            for group_name_index in range(2, num_cols):
                group_string = csvalues[group_name_index].strip()
                group_name = group_string
                group_description = ""
                if(":" in group_name):
                    group_values = group_name.split(":")
                    group_name = group_values[0]
                    group_description = group_values[1]
                is_last_group = group_name == "<end>"
                if(is_last_group and last_group!=None):
                    last_group.exercises.add(ex)
                    last_group.save()
                    last_group = None
                else:
                    wazaGroup, created = ExerciseGroup.objects.get_or_create(name=group_name)
                    wazaGroup.description = group_description
                    if last_group!=None:
                        wazaGroup.parent_group = last_group
                    wazaGroup.save()
                    last_group = wazaGroup

        #except:
        #    return traceback.format_exc()
    return None

def handle_uploaded_file_csv(f):
    #with open(f.read(), 'rb') as csvfile:
    spamreader = csv.reader(f, delimiter=' ', quotechar='|')
    print(str(spamreader))
    for row in spamreader:
        print (', '.join(row))