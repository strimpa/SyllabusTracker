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
        if len(csvalues) < 2:
            return ("Line contains less comma-separated values than 2 or more than maximum:"+line)
        #try:
        ex, created = Exercise.objects.get_or_create(name=csvalues[0].strip())
        if created:
            ex.description = csvalues[1].strip()
            ex.save()

        if len(csvalues)>2:
            gradeGroup, created = ExerciseGroup.objects.get_or_create(name=csvalues[2].strip())
            gradeGroup.exercises.add(ex)
            gradeGroup.save()

        if len(csvalues)>3:
            wazaGroup, created = ExerciseGroup.objects.get_or_create(name=csvalues[3].strip())
            wazaGroup.exercises.add(ex)
            wazaGroup.save()

        #except:
        #    return traceback.format_exc()
    return None

def handle_uploaded_file_csv(f):
    #with open(f.read(), 'rb') as csvfile:
    spamreader = csv.reader(f, delimiter=' ', quotechar='|')
    print(str(spamreader))
    for row in spamreader:
        print (', '.join(row))