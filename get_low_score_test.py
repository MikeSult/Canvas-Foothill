# 
# cd ~/Documents/HTML/CanvasAPI/
# python get_low_score_test.py
#
# this script will show the scores for a single test
# and it will highlight (with borders) the scores 
# that are below 70%
#
# Import the Canvas class
from canvasapi import Canvas

import time
import datetime
import re
import json

now = datetime.datetime.utcnow()

# ---------- load user specific data from json file ------------------
path = "../../HTML/CanvasAPI/"
with open(path+'my_info.json') as data:
  my_data = json.load(data)
  
API_URL = my_data['API_URL']
API_KEY = my_data['API_KEY']
INSTRUCTOR_ID = my_data['INSTRUCTOR_ID']
COURSE_ID = my_data['COURSE_ID']
#---------------------------------------------------------------------


#-------------- functions --------------------------------------------
def create_message(assignment_name, student_name):
    message = "Hello {0}, \nThis message is in regards to {1}. "
    message += "Your score on {1} was below 70% and I wanted to check-in with you. "
    message += " Please communicate via email or Canvas Inbox if you have questions about the material."    
    message += "\nThank you,\nMike Sult"
    return message.format(student_name, assignment_name)

#------------------ the main script -----------------------------
# User input at the Command line
input_assignment_name = input('input the test name: ')

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

# get course with course_id
course = canvas.get_course(COURSE_ID)

# Make header for the report
report_header = ("\n==============================================================================="
                 "\n{0}\nprinted on {1}\nget_low_score_test.py\n{2}\n"
                 "===============================================================================")
# all of the assignments
assignments = course.get_assignments()

for assignment in assignments:
    if input_assignment_name in assignment.name:
        # get the assignment
        my_assignment = course.get_assignment(assignment.id)

print( report_header.format(course.name, str(now), my_assignment.name) )

total_points_possible = my_assignment.points_possible

# get submission for an ASSIGNMENT_ID
submissions = my_assignment.get_submissions()

# get all of the students
users = course.get_users(enrollment_type=['student'])

# make array of user_ids
a = []
for user in users:
    a.append(user.id)

report = "------------------------------------------------------------------------\n"
report += "{0} submitted with a score of {1}/{2} = {3} %"
report += "\n------------------------------------------------------------------------\n"

report2 = "{0} submitted with a score of {1}/{2} = {3} %"

full_report = "\ntotal submissions: {4}\n{0} below 70 % grades, "
full_report += "\n{1} 70-79 % grades \n{2} 80-89 % grades \n{3} 90+ % grades\n"

count = 0;
count_70 = 0;
count_80 = 0;
count_90 = 0;
for submission in submissions:
    if submission.score != None:
        percentage = (float(submission.score)/total_points_possible)
        if  0.7 > percentage:
            count += 1
            print(report.format(course.get_user(submission.user_id), submission.score, total_points_possible, percentage*100) )
        elif  0.8 > percentage:
            count_70 += 1
            print(report2.format(course.get_user(submission.user_id), submission.score, total_points_possible, percentage*100) )
        elif  0.9 > percentage:
            count_80 += 1
            print(report2.format(course.get_user(submission.user_id), submission.score, total_points_possible, percentage*100) )
        else:
            count_90 += 1
            print(report2.format(course.get_user(submission.user_id), submission.score, total_points_possible, percentage*100) )

total_count = count + count_70 + count_80 + count_90
print(full_report.format(count, count_70, count_80, count_90, total_count))
