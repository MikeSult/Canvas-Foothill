# 
# cd ~/Documents/HTML/CanvasAPI/
# python get_current_percentage.py
#
# this script will scan all of the tests and make a report
# of current score percentage on a per student basis.
#
# Import the Canvas class
from canvasapi import Canvas

import time
import datetime
import re
import json

now = datetime.datetime.utcnow()

# ---------- load user specific data from json file ------------------
with open('./my_info.json') as data:
  my_data = json.load(data)
  
API_URL = my_data['API_URL']
API_KEY = my_data['API_KEY']
INSTRUCTOR_ID = my_data['INSTRUCTOR_ID']
COURSE_ID = my_data['COURSE_ID']
#---------------------------------------------------------------------


# ---------------- functions -----------------------------------------
def create_date_from_str(date_string):
    time_array =  filter(None, re.split("[T: Z\-]+", date_string) )
    count = 0
    for item in time_array:
        if(count==0):
            year = int(item)
        if(count==1):
            month = int(item)
        if(count==2):
            day = int(item)
        if(count==3):
            hour = int(item)
        if(count==4):
            minute = int(item)
        if(count==5):
            second = int(item)        
        count += 1
    
    return datetime.datetime(year, month, day, hour, minute, second)

def create_message(name, percent):
        
    message = "\nHello {},\n"
    message += "In reviewing your overall test scores, I see that your cumulative total is at {:.2f}%."
    message += "  I want to give you a chance to get back on track towards a better grade."
    message += "  I'm going open up test XXX.  If you have questions about the topics or any other issues, "
    message += "please communicate with via inbox at Canvas or email (mikesult@guitarland.com)"
    message += "\n\nAlso if you haven't already read it, please see "
    message += "<a href='https://www.guitarland.com/Music10/Mus10discussion.html'>Discussion about the Tests</a>."
    message += "  It gives some strategies for answering the specific test questions for each test."
    message += "\nMike Sult\n"
    return message.format(name,(percent*100))

def makeReport(user, report, percent):
    below_threshold = False
    if(percent < 0.7):
        message = '\n\n==================\n=================='
        message += create_message(user.name, percent)
        below_threshold = True
    else:
        message = '\n=================='
    message += "\n{}: total percentage: {:.2f}".format(user.name,(percent*100))
    message += report
    if(below_threshold):
        messages_to_students.append(message)
    print(message)

#------------------ the main script -----------------------------
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

# get course with course_id
course = canvas.get_course(COURSE_ID)

# Access the course's name
header = ("\n==============================================================================="
           "\n{0}\nprinted on {1}\nget_current_percentage.py\n"
           "===============================================================================")
 
print(header.format(course.name, str(now)))

assignments = course.get_assignments()
users = course.get_users(enrollment_type=['student'])

total_points_possible = 0
one_users_points = 0;
student_report = ''
messages_to_students = []
found_submission = False
count = 0
for user in users:
    student_report = "\n---------------------------\n"
    for assignment in assignments:
        if 'Test' in assignment.name or 'Midterm' in assignment.name or "Final" in assignment.name or 'Foothill College Academic Integrity Pledge' in assignment.name:
            overdue_date = create_date_from_str(assignment.due_at)
            lock_date = create_date_from_str(assignment.lock_at)

            if now < lock_date:
                continue
            
            total_points_possible += assignment.points_possible

            test_submissions = assignment.get_submissions()
            
            for submission in test_submissions:
                if submission.body == None:
                    continue
                if(submission.user_id == user.id):
                    found_submission = True
                    one_users_points += submission.score
                    student_report += assignment.name+": Score = "+str(submission.score)+"/"+str(assignment.points_possible)+"\n"
                

            if(not found_submission):
                student_report += assignment.name+": Score = 0/"+str(assignment.points_possible)+" (not submitted)\n"
            
        found_submission = False

    percentage = (float(one_users_points)/total_points_possible)
    makeReport(user, student_report, percentage)
    total_points_possible = 0
    one_users_points = 0;
    student_report = ''
    found_submission = False
    count += 1

print("------------------------------------")
print("This class has {} students".format(str(count)))
print("------------------------------------")
for msg in messages_to_students:
   print(msg)
        