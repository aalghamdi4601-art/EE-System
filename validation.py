# Validation module for the Graduation Project Registration System.

# Checks the number of team members.
def check_team_size(team):

    if len(team.members) == 3:
        return True , " "
    
    return False , "The team must consist of 3 members."

# Ensures the members' specializations are suitable for the project.
def check_specialization(team , project):
    for member in team.members:
        if member.program != project.specialization:
           return False, f"Student {member.student_id} program '{member.program}' is not allowed for this project."
    return True , " "
        
# Verifies that members have passed the required courses.
def check_prerequisites(team, project):
    for member in team.members:
        for course in project.prerequisites:
            if course not in member.completed_courses:
                return False, f"Student {member.student_id} did not pass the required course '{course}'."
    return True, ""

# Checks the available seats in the project.
def check_slots(db, project_id):
    if db.check_project_capacity(project_id):
        return True, ""
    return False, "No seats available for this project."

# Checks the supervisor's availability.
def check_supervisor(faculty):
    if faculty.current_supervisions < faculty.max_supervisions:
        return True , " "
    return False, f"Supervisor {faculty.name} has reached the maximum supervision load."


# Checks if the team is already registered in another project.
def check_team_already_registered(db, team_id):
    if db.check_team_registered(team_id):
        return False, "This team is already registered in a project."
    return True, ""


# Runs all validation checks before registering a team for a project.
def validate_registration(team, project, faculty, db, project_id, team_id):
    errors = []
    
    ok, msg = check_team_size(team)
    if not ok:
        errors.append(msg)
    
    ok, msg = check_specialization(team , project)
    if not ok:
        errors.append(msg)
    
    ok, msg = check_prerequisites(team , project)
    if not ok:
        errors.append(msg)

    ok, msg = check_slots(db, project_id)
    if not ok:
        errors.append(msg)

    ok, msg = check_supervisor(faculty)
    if not ok:
        errors.append(msg)

    ok, msg = check_team_already_registered(db, team_id)
    if not ok:
        errors.append(msg)
    
    if len(errors) == 0:
        return True, "Registration successful."
    return False, "\n".join(errors)
