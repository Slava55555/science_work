
import random
import numpy as np
from collections import defaultdict
from deap import base, creator, tools, algorithms
import read_files as rf

# Загружаем данные из CSV
data = rf.read_all_data()

teachers_data = data['teachers']
groups = data['groups']
classrooms = data['classrooms']
time_slots = [f"{slot['start']}-{slot['end']}" for slot in data['time_slots']]
days = [day['name'] for day in data['days']]

teachers = {}
for teacher_info in teachers_data:
    name = teacher_info['teacher_name']
    if name not in teachers:
        teachers[name] = []
    teachers[name].append((
        teacher_info['lesson_type'],
        teacher_info['subject'],
        int(teacher_info['semester']),
        teacher_info['groups'],
        teacher_info['is_common'] == 'True'
    ))

def generate_lessons():
    lessons = []
    lesson_id = 0
    for teacher, subjects in teachers.items():
        for lesson_type, subject, pairs_per_week, lesson_groups, can_join in subjects:
            if can_join:
                for _ in range(pairs_per_week):
                    lessons.append({
                        'id': lesson_id,
                        'teacher': teacher,
                        'type': lesson_type,
                        'subject': subject,
                        'groups': lesson_groups,
                        'can_join': True
                    })
                    lesson_id += 1
            else:
                for group in lesson_groups:
                    for _ in range(pairs_per_week):
                        lessons.append({
                            'id': lesson_id,
                            'teacher': teacher,
                            'type': lesson_type,
                            'subject': subject,
                            'groups': [group],
                            'can_join': False
                        })
                        lesson_id += 1
    return lessons

all_lessons = generate_lessons()

#Создание индивида (хромосомы)
def create_individual():
    individual = []
    for lesson in all_lessons:
        individual.append({
            'id': lesson['id'],
            'teacher': lesson['teacher'],
            'type': lesson['type'],
            'subject': lesson['subject'],
            'groups': lesson['groups'],
            'can_join': lesson['can_join'],
            'classroom': random.choice(classrooms),
            'time': random.choice(time_slots),
            'day': random.choice(days)
        })
    return individual

#Функция приспособленности
def evaluate(individual):
    conflicts = 0

    teacher_schedule = set()
    classroom_schedule = set()
    group_schedule = set()

    for lesson in individual:
        teacher = lesson['teacher']
        classroom = lesson['classroom']
        time = lesson['time']
        day = lesson['day']
        groups = lesson['groups']
        can_join = lesson['can_join']

        # Проверка конфликтов преподавателей
        teacher_key = (teacher, day, time)
        if teacher_key in teacher_schedule:
            conflicts += 1
        else:
            teacher_schedule.add(teacher_key)

        # Проверка конфликтов аудиторий
        classroom_key = (classroom, day, time)
        if classroom_key in classroom_schedule:
            conflicts += 1
        else:
            classroom_schedule.add(classroom_key)

        # Проверка конфликтов групп
        if not can_join:
            for group in groups:
                group_key = (group, day, time)
                if group_key in group_schedule:
                    conflicts += 1
                else:
                    group_schedule.add(group_key)

    return (conflicts,)

# Настройка генетического алгоритма
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate)

# Оператор мутации
def mutate(individual, indpb=0.1):
    for lesson in individual:
        if random.random() < indpb:
            lesson['classroom'] = random.choice(classrooms)
        if random.random() < indpb:
            lesson['time'] = random.choice(time_slots)
        if random.random() < indpb:
            lesson['day'] = random.choice(days)
    return individual,

# Оператор скрещивания
def cxTwoPointCopy(ind1, ind2):
    size = min(len(ind1), len(ind2))
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    # Создаем копии для скрещивания
    ind1_copy = [dict(lesson) for lesson in ind1]
    ind2_copy = [dict(lesson) for lesson in ind2]

    # Обмен участками
    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] = \
        ind2_copy[cxpoint1:cxpoint2], ind1_copy[cxpoint1:cxpoint2]

    return ind1, ind2

toolbox.register("mate", cxTwoPointCopy)
toolbox.register("mutate", mutate)
toolbox.register("select", tools.selTournament, tournsize=3)


def main():
    random.seed(42)
    population = toolbox.population(n=100)

    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    hof = tools.HallOfFame(1)

    population, logbook = algorithms.eaSimple(
        population, toolbox, cxpb=0.7, mutpb=0.2, ngen=50,
        stats=stats, halloffame=hof, verbose=True
    )

    return population, logbook, hof

population, logbook, hof = main()
best_individual = hof[0]


print("\nЛучшее расписание (количество конфликтов:", evaluate(best_individual)[0], "):")


schedule = defaultdict(lambda: defaultdict(list))
for lesson in best_individual:
    day = lesson['day']
    time = lesson['time']
    schedule[day][time].append(lesson)

for day in days:
    print(f"\n{day}:")
    day_has_lessons = False

    for time in time_slots:
        if time in schedule[day]:
            day_has_lessons = True
            print(f"  {time}:")
            for lesson in schedule[day][time]:
                groups_str = ", ".join(lesson['groups'])
                joint = " (объединенная)" if lesson['can_join'] else ""
                print(f"    {lesson['teacher']}: {lesson['type']} {lesson['subject']} "
                      f"для групп {groups_str} в аудитории {lesson['classroom']}{joint}")

    if not day_has_lessons:
        print("  Нет занятий")