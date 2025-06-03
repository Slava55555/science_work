import  csv
def read_teachers(file_path='database/teachers.csv'):
    teachers = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['groups'] = row['groups'].split(',')
            row['is_common'] = row['is_common'] == 'True'
            teachers.append(row)
    return teachers

def read_groups(file_path='database/groups.csv'):
    groups = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            groups.append(row['group_id'])
    return groups

def read_classrooms(file_path='database/classrooms.csv'):
    classrooms = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classrooms.append(row['classroom_id'])
    return classrooms

def read_time_slots(file_path='database/time_slots.csv'):
    time_slots = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            time_slots.append({
                'id': row['time_slot_id'],
                'start': row['start_time'],
                'end': row['end_time']
            })
    return time_slots

def read_days(file_path='database/days.csv'):
    days = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            days.append({
                'id': row['day_id'],
                'name': row['day_name']
            })
    return days

def read_all_data():
    return {
        'groups': read_groups(),
        'teachers': read_teachers(),
        'classrooms': read_classrooms(),
        'time_slots': read_time_slots(),
        'days': read_days()
    }