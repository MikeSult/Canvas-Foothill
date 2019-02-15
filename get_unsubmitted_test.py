# 
# cd ~/Documents/HTML/CanvasAPI/
# python get_unsubmitted_test.py
#
# this script will list students who have not submitted
# a specific (user input) test.
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


# ----------------- functions ----------------------------------------
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

def create_message(assignment_name, student_name):
    message = "Hello {0}, \nYou have not yet submitted the {1}. "
    if "Foothill" in assignment_name: 
        message += "I assume this is simply an oversight.  "
        message += "If you intend on taking this course, please complete the {1}. "
        message += "It is located in the quizzes area as the first item. "
        message += "For the upcoming census I plan on dropping students who have not submitted it."
        message += "\nThank you,\nMike Sult"
    else:
        message += "I want to give you a change to catch up in the course and complete {1}."
        message += " Please communicate via email or Canvas Inbox if you wish to extend the due date."    
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
                 "\n{0}\nprinted on {1}\nget_unsubmitted_test.py\n"
                 "===============================================================================")
print(report_header.format(course.name, str(now)))

# all of the assignments
assignments = course.get_assignments()

# get all of the students
users = course.get_users(enrollment_type=['student'])

# make array of user_ids
a = []
for user in users:
    a.append(user.id)

count = 0

# header for the test report
test_header = ("\n-------------------------------------------------------------------\n"
               "{0}\nid = {1}, lock_at: {2}"
               "\n-------------------------------------------------------------------\n")
for assignment in assignments:
    count = 0

    # look for the Test name input by user
    if input_assignment_name in assignment.name:
        print(test_header.format(assignment.name, assignment.id, assignment.lock_at))
        if assignment.due_at:
            overdue_date = create_date_from_str(assignment.due_at)
        else:
            overdue_date = now
            
        if now > overdue_date:
            print("This assignment is overdue.  Due date: {0}".format(overdue_date))
        else:
            if assignment.due_at == None:
                print("This assignment is open")            
            else:
                print("Upcoming Due date: {0}".format(overdue_date))
        test_submissions = assignment.get_submissions()

        a_copy = a.copy()
        for submission in test_submissions:
            ID = None
            if submission.body == None:
                # count the non submissions
                count += 1
            else: 
                # they've already submitted, so remove them from the user array (a_copy)
                ID = submission.user_id
                if ID in a_copy:
                    a_copy.remove(ID)

        # use correct grammar
        if count == 1:
            word = 'is'
            plural = ''
        else:
            word = 'are'
            plural = 's'
			
		# print out how many unsubmitted tests
        message = 'There '+word
        message += ' {} missing submission'+plural+" for {}"
        print(message.format(count, assignment.name))
		
        # printout users who haven't submitted
        for user in users:
            for item in a_copy:
                if user.id == item:
                    # create message for each who haven't submitted the test
                    print("\n{} id: {}".format(user.name, user.id))
                    print(create_message(assignment.name, user.name))

