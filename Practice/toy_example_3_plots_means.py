from random import seed,sample,randint,shuffle,choice
from matplotlib import pyplot as plt
#seed(255)

class Student:
    def __init__(self,name,preferences,routes=None,locals=None,SES = None):
        self.name = name
        self.preferences = preferences[:]
        self.routes = routes
        self.locals = locals
        self.SES = SES

    def __repr__(self):
        return self.name

class College:
    def __init__(self,name,capacity,priorities,routes):
        self.name = name
        self.capacity = capacity
        self.priorities = priorities[:]
        self.routes = routes
        self.assigned_students = []

    def __repr__(self):
        return self.name

class Route:
    def __init__(self,name,capacity,college):
        self.name = name
        self.capacity = capacity
        self.college = college

    def __repr__(self):
        return self.name

def initialise(random_seed,
        n_students = 5, n_colleges = 2, n_routes = 1,
        min_students = 10, min_colleges = 2, min_college_capacity = 1, min_route_capacity = 1,
        max_students = 100, max_colleges = 10, max_college_capacity = 30, max_route_capacity = 10,
        verbose = False, randomised = True, restricted = False
):
    """Function to initialise all students and colleges randomly with routes and local students."""
    # Set random seed
    seed(random_seed)

    # Randomly generated number of participants
    n_students = randint(min_students,max_students) if randomised else n_students
    n_colleges = randint(min_colleges,max_colleges) if randomised else n_colleges
    n_routes = randint(1,n_colleges) if randomised else n_routes

    # User-defined college and route capacities
    c_cap = 2 if not randomised else None
    r_cap = 1 if not randomised else None

    # Lists of all participants and routes
    student_names = [f"s_{i+1}" for i in range(n_students)]
    college_names = [f"c_{i+1}" for i in range(n_colleges)]
    route_names = [f"r_{i+1}" for i in range(n_routes)]
    print(f"list of student names: {student_names}",
          f"list of college names: {college_names}",
          f"list of route names: {route_names}",
          "-"*50, sep="\n") if verbose else None

    # Capacities of colleges and routes
    c_caps = {c:randint(min_college_capacity,max_college_capacity) for c in college_names} if randomised else {c:c_cap for c in college_names}
    r_caps = {r:randint(min_route_capacity,max_route_capacity) for r in route_names} if randomised else {r:r_cap for r in route_names}
    print(f"college capacities:",*[f"{k}: {v}" for k,v in c_caps.items()],
          f"route capacities:",*[f"{k}: {v}" for k,v in r_caps.items()],
          "-"*50, sep="\n") if verbose else None

    # Route services
    r_serves = (dict(zip(route_names[:],college_names[:])),
                dict(zip(college_names[:],route_names[:])))

    # Students served by routes - randomly selects a subset of the students to have access to randomly selected routes
    if randomised:
        served_students = sample(student_names,randint(0,len(student_names))) #creates the subset of routed students
        s_served = {s:sample(route_names,randint(1,len(route_names))) for s in served_students} #allocates routes to students
    else:
        served_students = student_names[:3] #creates the subset of routed students
        s_served = {s:route_names[0] for s in served_students} #allocates routes to students
    #unserved_students = [s for s in student_names if s not in served_students]
    print("route services:",*[f"{k}: {v}" for k,v in r_serves[0].items()],
          "served students:",*[f"{k}: {v}" for k,v in s_served.items()],
          "-"*50, sep="\n") if verbose else None

    # Local students - randomly selects a subset of the students to be local to a randomly selected school
    # Also ensures the selected school is valid - a student cannot be local to a college and routed to it
    if randomised:
        local_students = sample(student_names,randint(0,len(student_names))) #creates the subset of local students
        s_local = {s:choice([c for c in college_names if r_serves[1].get(c) != s_served.get(s)] or [None]) for s in local_students} #assigns valid local college to local students
    else:
        local_students = sample(student_names,2)
        s_local = {s:college_names[0] for s in local_students}
    #remaining_students = [s for s in student_names if s not in local_students]
    print(f"local students: {local_students}",*[f"{k}: {v}" for k,v in s_local.items()],
          #f"distant students: {distant_students}",
          "-"*50, sep="\n") if verbose else None

    # Student preferences
    student_preferences = {s:college_names[:] for s in student_names[:]} #colon makes shallow copy to avoid mutation of name
    if randomised:
        for c in student_preferences.values(): shuffle(c)

    # College priorities - assigns student to high and low priority bracket based on locality
    college_priorities = dict()
    low_priority_bracket = {c:[s for s in student_names if s_local.get(s) is not c] for c in college_names} #assigns each college a list of valid, non-local students
    high_priority_bracket = {c:[s for s in student_names if s_local.get(s) is c] for c in college_names} #assigns each college a list of valid, local students
    if randomised:
        for s in low_priority_bracket.values(): shuffle(s)
        for s in high_priority_bracket.values(): shuffle(s)

    # Add routes to preferences and priorities
    for s in sample(student_names,len(student_names)):
        if s in s_served.keys():
            for r in sample(s_served[s],randint(1,len(s_served[s]))):
                #r = choice(s_served[s])
                student_preferences[s].insert(0,(r,r_serves[0][r]))
        for c in sample(college_names,len(college_names)):
            if (c in r_serves[1].keys()) and ((r_serves[1][c],c) in student_preferences[s]):
                high_priority_bracket[c].insert(0,((r_serves[1][c],s)))
            # elif c == s_local.get(s):
            #     high_priority_bracket[c].insert(0,s)
    
    for c in college_names:
        #shuffle(high_priority_bracket[c])
        college_priorities.update({c:(high_priority_bracket[c]+low_priority_bracket[c])})

    # English school choice restriction
    if restricted:
        for s in student_names: student_preferences[s] = student_preferences[s][:3]

    # Check preferences and priorities
    print("student preferences:",*[f"{k}: {v}" for k,v in student_preferences.items()],
          "college priorities:",*[f"{k}: {v}" for k,v in college_priorities.items()],
          "-"*50, sep="\n") if verbose else None

    # Assign class objects
    students = {
        s:Student(
            s,
            student_preferences[s],
            s_served[s] if s in s_served.keys() else None,
            s_local[s] if s in s_local.keys() else None,
            0 if s in s_served.keys() else 1
            ) for s in student_names
            }
    colleges = {
        c:College(
            c,
            c_caps[c],
            college_priorities[c],
            r_serves[1][c] if c in r_serves[1].keys() else None
            ) for c in college_names
            }
    routes = {
        r:Route(
            r,
            r_caps[r],
            r_serves[0][r]
            ) for r in route_names
            }
    # print(f"dictionary of student objects: \n{students}",
    #       f"dictionary of college objects: \n{colleges}",
    #       f"dictionary of route objects: \n{routes}",
    #       "-"*50, sep="\n") if verbose else None

    # Set student SES
    # for k,v in students.items():
    #     if k in s_served.keys(): v.SES = 0
    #     else: v.SES = 1
    
    return student_names, college_names, route_names, student_preferences, college_priorities, students, colleges, routes

def dissimilarity_index(students, colleges):
    """Calculates the college's diversity index from student SES values."""
    L = len([student for student in students.values() if student.SES == 0])
    H = len(students)-L
    c_divs = [] #;print("L and H",L,H) # bugfixing print statement
    for k,v in colleges.items():
        h = l = 0
        for s in v.assigned_students:
            if students[extract_student(s)].SES == 1: h+=1
            else: l+=1
        c_divs.append(abs(h/H - l/L)) if L and H else c_divs.append(0)
    return 0.5*sum(c_divs)

def extract_route(matching_preference):
    """Extract route from preference."""
    if isinstance(matching_preference,tuple): return matching_preference[0]
    else: return None

def extract_college(matching_preference):
    """Extract college from preference."""
    if isinstance(matching_preference,tuple): return matching_preference[1]
    else: return matching_preference

def extract_student(assigned_object):
    """Extract student from assigned tuple."""
    if isinstance(assigned_object,tuple): return assigned_object[1]
    else: return assigned_object

def match_to_priority(student, preference):
    """Convert matching item to college priority."""
    if isinstance(preference, tuple):
        route = preference[0]
        return (route, student)
    else:
        return student

def college_oversubscription(students,colleges,free,matching,unassigned,c,verbose=False):
    """Run if current college capacity reaches 0."""
    if verbose: print(f"{c} has reached capacity!")
    if verbose: print(f"current priority list for {c}: {colleges[c].priorities}")

    # need to change this to check ONLY the students who are matched to college c

    ranking = {student:rank for rank,student in enumerate(college_priorities[c])}
    lowest_priority = max((student for student in colleges[c].assigned_students),
                        key=lambda student: ranking[student],default=None)
    
    if verbose: print(f"lowest priority in the matching for {c} is {lowest_priority}")
    
    lowest_priority_student = extract_student(lowest_priority)
    if verbose: print(f"{lowest_priority_student} unmatched with {matching[lowest_priority_student]}")

    students[lowest_priority_student].preferences.remove(matching[lowest_priority_student])
    if verbose: print(f"reduced preference list for {lowest_priority_student}: {students[lowest_priority_student].preferences}")

    colleges[c].priorities.remove(lowest_priority)
    if verbose: print(f"reduced priority list for {c}: {colleges[c].priorities}")

    colleges[c].assigned_students.remove(lowest_priority)
    if verbose: print(f"reduced assignments to {c}: {colleges[c].assigned_students}")

    matching.pop(lowest_priority_student)

    if students[lowest_priority_student].preferences:
        free.append(lowest_priority_student)
    else:
        unassigned.append(lowest_priority_student)
        if verbose: print(f"{lowest_priority_student} has emptied their preference list and is unassigned")
    
    if verbose: print("new list of free students:",free)

def route_oversubscription(students,colleges,free,matching,unassigned,s,c,r,verbose=False):
    """Run if current route capacity reaches 0."""
    if verbose: print(f"{r} has reached capacity!", f"{r} serves {c}", f"current priority list for {c}: {colleges[c].priorities}", sep="\n")

    ranking = {student:rank for rank,student in enumerate([p for p in colleges[c].priorities if isinstance(p,tuple) and r in p])}
    lowest_priority = max((student for student,preference in matching.items() if match_to_priority(student,preference) in ranking),
                        key=lambda student: ranking[match_to_priority(student,matching[student])],
                        default=None)
    if verbose: print(f"lowest priority routed student assigned to {c} is {lowest_priority}")
    if verbose: print(f"{lowest_priority} unmatched with {matching[lowest_priority]}")

    students[lowest_priority].preferences.remove(matching[lowest_priority])
    if verbose: print(f"reduced preference list for {lowest_priority}: {students[lowest_priority].preferences}")

    colleges[c].priorities.remove((r,lowest_priority))
    if verbose: print(f"reduced priority list for {c}: {colleges[c].priorities}")

    colleges[c].assigned_students.remove((r,lowest_priority))
    if verbose: print(f"reduced assignments to {c}: {colleges[c].assigned_students}")

    matching.pop(lowest_priority)

    if students[lowest_priority].preferences:
        free.append(lowest_priority)
    else:
        unassigned.append(s)
        if verbose: print(f"{lowest_priority} has emptied their preference list and is unassigned")
    
    if verbose: print("new list of free students:",free)

def greedy_matching(student_names, students, colleges, routes, verbose=False):
    """Greedy matching algorithm"""
    free = student_names.copy()
    matching = {}
    unassigned = []

    while free:
        print(free) if verbose else None

        # pop the first student in the list
        s = free.pop(0)

        # handle empty preference lists
        if not students[s].preferences:
            unassigned.append(s)
            print(f"student {s} has emptied their preference list and is unassigned", "-"*50, sep="\n") if verbose else None
            continue

        # pop the top college on s's preference list and handle empty preference lists
        p = students[s].preferences.pop(0)

        #handle oversubscription
        r = extract_route(p)
        c = extract_college(p)

        if r:
            if routes[r].capacity and colleges[c].capacity:
                matching.update({s:p})
                colleges[c].assigned_students.append(match_to_priority(s,p))
                routes[r].capacity -= 1 ;colleges[c].capacity -= 1
            elif routes[r].capacity and not colleges[c].capacity:
                print("COLLEGE CAPACITY") if verbose else None
                free.append(s)
                continue
            else:
                print("ROUTE CAPACITY") if verbose else None
                free.append(s)
                continue
        
        else:
            if colleges[c].capacity:
                matching.update({s:p})
                colleges[c].assigned_students.append(match_to_priority(s,p))
                colleges[c].capacity -= 1
            else:
                print("COLLEGE CAPACITY") if verbose else None
                free.append(s)
                continue
    
    di = dissimilarity_index(students, colleges)
    print(di) if verbose else None

    print("END") if verbose else None

    return students, colleges, routes, matching, unassigned, di

def routed_acceptance(student_names, college_names, students, colleges, routes, verbose=False):
    """Modified Deferred Accepance algorithm."""

    free = student_names.copy()
    matching = {}
    unassigned = []
    n_proposals = 0

    print(f"\n{"-"*50}\nBEGIN MATCHING\n{"-"*50}\n") if verbose else None

    while free:
        # Display remaining free students and available college/route capacity
        print(f"list of free students:\n {free}", "-"*50,
              *[f"remaining {c} capacity is {c.capacity}" for c in colleges.values()], "-"*50,
              *[f"remaining {r} capacity is {r.capacity}" for r in routes.values()], "-"*50,
              sep="\n") if verbose else None

        # assign first student in the list of free students
        s = free.pop(0) # argument selects the first student in the list
        print(f"assigning student {s}",
              f"{s} has preferences:\n {students[s].preferences}" if students[s].preferences else f"{s} has emptied their preference list",
              sep="\n") if verbose else None

        # handle empty preference lists
        if not students[s].preferences:
            unassigned.append(s)
            print(f"student {s} has emptied their preference list and is unassigned",
                  "-"*50, sep="\n") if verbose else None
            continue

        # Update the number of proposals
        n_proposals += 1

        # identify first student's top preference
        p = students[s].preferences[0]
        print(f"{s}'s top preference is {p}", "-"*50, sep="\n") if verbose else None

        # extract route and college from s's top preference
        r = extract_route(p)
        c = extract_college(p)

        # tentative matching
        matching.update({s:p})
        print(f"tentative matching:\n {matching}", "-"*50, sep="\n") if verbose else None

        # update assigned students
        colleges[c].assigned_students.append(match_to_priority(s,p))
        print("assigned students:", *[f" {x}, {y.assigned_students}" for x,y in colleges.items()], "-"*50, sep="\n") if verbose else None

        # handle oversubscription
        if r:
            if routes[r].capacity and colleges[c].capacity:
                routes[r].capacity -= 1; colleges[c].capacity -= 1
                continue
            elif routes[r].capacity and not colleges[c].capacity:
                college_oversubscription(students,colleges,free,matching,unassigned,c)
                continue
            else:
                route_oversubscription(students,colleges,free,matching,unassigned,s,c,r)
                continue
        else:
            if colleges[c].capacity:
                colleges[c].capacity -= 1
                continue
            else:
                college_oversubscription(students,colleges,free,matching,unassigned,c)
                continue

    print(f"final number of proposals: {n_proposals}",
          f"maximum number of proposals: {len(students)*len(colleges)}",
          f"ratio: {100*n_proposals/(len(students)*len(colleges))}",
          sep="\n") if verbose else None
    print(f"\n{"-"*50}\nEND MATCHING\n{"-"*50}\n") if verbose else None

    di = dissimilarity_index(students, colleges)

    return students, colleges, routes, matching, unassigned, di

def check_stability(student_preferences, college_priorities, colleges, routes, matching, unassigned, verbose=False):
    """Checks the stability of the matching."""
    if verbose: print(f"\n{"-"*50}\nCHECKING MATCHED STUDENTS\n{"-"*50}\n")
    blocking_pairs = []
    for s,mp in matching.items():
        if verbose: print(f"\nstudent {s} has preferences {student_preferences[s]} and was matched to {mp}\n")
        for p in student_preferences[s]:
            if p is mp: break
            else: # p in matching.values():
                c = extract_college(p)
                r = extract_route(p)
                spr = match_to_priority(s,p)
                assigned_student_priority_indices = [college_priorities[c].index(i) for i in colleges[c].assigned_students]
                if colleges[c].capacity and r:
                    if routes[r].capacity: blocking_pairs.append((s,p)) ;print(f"blocking pair found: {s,p}") if verbose else None
                    else: print(f"{c} has spare capacity but {r}'s route capacity reached so {spr} was rejected during matching so\nno blocking pairs\n") if verbose else None
                elif colleges[c].capacity:
                    blocking_pairs.append((s,p)) ;print(f"college {c} has spare capacity so blocking pair found: {s,p}\n") if verbose else None
                    continue
                if verbose: print(
                    f"{s} not matched to top choice!\n",
                    f"college {c} from preference {p} has priorities {college_priorities[c]}\n",
                    f"and was assigned: {colleges[c].assigned_students}\n",
                    f"{c}'s assigned student priority indices: {assigned_student_priority_indices}\n",
                    f"{spr}'s priority index: {college_priorities[c].index(spr)}\n"
                    )
                #print(f"{college_priorities[c].index(match_to_priority(s,mp))} {assigned_student_priority_indices}")
                if college_priorities[c].index(spr) <= max(assigned_student_priority_indices): 
                    if r:
                        if routes[r].capacity: blocking_pairs.append((s,p)) ;print(f"blocking pair found: {s,p}") if verbose else None
                        else: print(f"{r}'s route capacity reached so {spr} was rejected during matching so\nno blocking pairs\n") if verbose else None
                    else: print(f"{s}'s routed preferences have reached route capacity so {spr} rejected\nno blocking pairs\n") if verbose else None
                else: print("no blocking pairs\n") if verbose else None

    if verbose: print(f"\n{"-"*50}\nCHECKING UNASSIGNED STUDENTS\n{"-"*50}\n")
    for s in unassigned:
        if verbose: print(f"\nstudent {s} has preferences: {student_preferences[s]}\n")
        for p in student_preferences[s]:
            if verbose: print(f"checking preference {p}:")
            if p in matching.values():
                c = extract_college(p)
                r = extract_route(p)
                spr = match_to_priority(s,p)
                assigned_student_priority_indices = [college_priorities[c].index(i) for i in colleges[c].assigned_students]
                if colleges[c].capacity and r:
                    if routes[r].capacity: blocking_pairs.append((s,p)) ;print(f"blocking pair found: {s,p}") if verbose else None
                    else: print(f"{c} has spare capacity but {r}'s route capacity reached so {spr} was rejected during matching so\nno blocking pairs\n") if verbose else None
                elif colleges[c].capacity:
                    blocking_pairs.append((s,p)) ;print(f"college {c} has spare capacity so blocking pair found: {s,p}\n") if verbose else None
                    continue
                if verbose: print(
                    f"{c} is already matched!\n",
                    f"{c} has priorities: {college_priorities[c]}\n",
                    f"and was assigned: {colleges[c].assigned_students}\n",
                    f"{c}'s assigned student priority indices: {assigned_student_priority_indices}\n",
                    f"{spr}'s priority index: {college_priorities[c].index(spr)}\n"
                    )
                if max(assigned_student_priority_indices) >= college_priorities[c].index(spr):
                    if r:
                        if routes[r].capacity: blocking_pairs.append((s,p)) ;print(f"blocking pair found: {s,p}\n") if verbose else None
                        else: print(f"{r}'s route capacity reached so {spr} was rejected during matching so\nno blocking pairs\n") if verbose else None
                    else: print(f"{s}'s routed preferences have reached route capacity so {spr} rejected\nno blocking pairs\n") if verbose else None
                else: print(f"no blocking pairs\n") if verbose else None
    return blocking_pairs


greedy_dis = []
routey_dis = []

for i in range(10):

    student_names, college_names, route_names, student_preferences, college_priorities, students, colleges, routes = initialise(i)

    greed_students, greed_colleges, greed_routes, greed_matching, greed_unassigned, greed_di = greedy_matching(student_names, students, colleges, routes)

    greed_blocking_pairs = check_stability(
        student_preferences, college_priorities,
        greed_colleges, greed_routes,
        greed_matching, greed_unassigned,
        verbose=False)
    
    student_names, college_names, route_names, student_preferences, college_priorities, students, colleges, routes = initialise(i)

    route_students, route_colleges, route_routes, route_matching, route_unassigned, route_di = routed_acceptance(student_names, college_names, students, colleges, routes)
    
    route_blocking_pairs = check_stability(
        student_preferences, college_priorities,
        route_colleges, route_routes,
        route_matching, route_unassigned,
        verbose=False)

    greedy_dis.append(greed_di)
    routey_dis.append(route_di)

    # print(100*"-",
    #       f"greedy diversity index: {greed_di}",
    #       f"greedy blocking pairs:\n{greed_blocking_pairs}",
    #       100*"-",
    #       f"new algorithm diversity index: {route_di}",
    #       f"new algorithm blocking pairs: {route_blocking_pairs}",
    #       100*"-",
    #       sep="\n")

print(greedy_dis,routey_dis)
plt.plot(greedy_dis)
plt.plot(routey_dis)
plt.show()