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
    exercise_counter = 0
    group_counter = 0

    for line in lines:
        csvalues = str(line).split(',')
        num_cols = len(csvalues)
        if num_cols < 2:
            return ("Line contains less comma-separated values than 2 or more than maximum:"+line)
        ex = Exercise.objects.create(name=csvalues[0].strip(), description=csvalues[1].strip(), list_order_index=exercise_counter)
        exercise_counter += 1

        # Afterwards go over each column in the row and add and/or link the group until <end> is reached
        # group cells can have a colon to add a description
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

                if last_group==None:
                    print("Starting group chain "+group_name)

                is_last_group = (group_name == "" or group_name == "<end>" or group_name_index == num_cols-1)
                if(is_last_group and last_group!=None):
                    last_group.exercises.add(ex)
                    last_group.save()
                    last_group = None
                else:
                    wazaGroup, created = ExerciseGroup.objects.get_or_create(name=group_name)
                    if created:
                        wazaGroup.list_order_index = group_counter
                        group_counter += 1
                    wazaGroup.description = group_description
                    if last_group!=None:
                        wazaGroup.parent_group = last_group
                    wazaGroup.save()
                    last_group = wazaGroup
    return None

def handle_uploaded_file_csv(f):
    #with open(f.read(), 'rb') as csvfile:
    spamreader = csv.reader(f, delimiter=' ', quotechar='|')
    print(str(spamreader))
    for row in spamreader:
        print (', '.join(row))