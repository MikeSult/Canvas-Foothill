# 
# cd ~/Documents/HTML/CanvasAPI/
# python get_overdue_grace_period.py
#
# this script will scan all of the tests and make a report
# of late tests on a per student basis.
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

def create_message(user_with_tests):
    name = user_with_tests[0]
    tests = user_with_tests[1]
    testmessage = ""
    count = 0
    for test in tests:
        if(count>0):
            testmessage += ", "
        testmessage += test
        count += 1
        
    message = "\nHello {}, you have missed the due date for {}."
    message += " Please communicate via email or Canvas Inbox if you wish to extend the due date."
    message += " Also if you haven't already read it, please see "
    message += "<a href='https://www.guitarland.com/Music10/Mus10discussion.html'>Discussion about the Tests</a>"
    message += " It gives some strategies for answering these specific test questions."
    message += "\nMike Sult\n"
    
    return message.format(name, testmessage)

def create_message2(user_with_tests):
    name = user_with_tests[0]
    tests = user_with_tests[1]
    testmessage = ""
    count = 0
    for test in tests:
        if(count>0):
            testmessage += ", "
        testmessage += test
        count += 1

    message = "\nHello {}, you have missed the due date for {}."
    message += " There is a grace period through Friday during which you can still submit for full credit.  "
    message += " Please feel free to contact me regarding any questions or concerns you might have."
    message += "\nMike Sult\n"
    
    return message.format(name, testmessage)

def makeReport(list_of_users, list_of_tests):
    unique_users = []
    tests = []
    users_and_tests = []
    for user in list_of_users:
        if user not in unique_users:
            unique_users.append(user)
            
    for a_user in unique_users:
        for user, test in zip(list_of_users, list_of_tests):
            if user == a_user:
                tests.append(test)
        one_record = [a_user, tests]
#        print(create_message(one_record))
        print(create_message2(one_record))
        users_and_tests.append(one_record)
        tests = []
        one_record = []


#------------------ the main script -----------------------------
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

# get course with course_id
course = canvas.get_course(COURSE_ID)

# Access the course's name
header = ("\n==============================================================================="
           "\n{}\nprinted on {}\nget_overdue_grace_period.py\n"
           "===============================================================================")
 
print(header.format(course.name, str(now)))

assignments = course.get_assignments()
users = course.get_users(enrollment_type=['student'])
a = []
list_of_overdue_users = []
list_of_overdue_tests = []

# make array of user_ids
for user in users:
    a.append(user.id)

count = 0
for assignment in assignments:
    count = 0    
    if 'Test' in assignment.name or 'Midterm' in assignment.name or "Final" in assignment.name or 'Foothill College Academic Integrity Pledge' in assignment.name:
        print("\n---------------------------\n{0}, id = {1}, lock_at: {2}".format(assignment.name, assignment.id, assignment.lock_at))
        overdue_date = create_date_from_str(assignment.due_at)
        lock_date = create_date_from_str(assignment.lock_at)
        if now > overdue_date:
            print("This assignment is overdue.  Due date: {0}".format(overdue_date))
        else:
            print("Upcoming Due date: {}".format(overdue_date))

        if now > lock_date:
            print("This assignment is locked.  Lock date: {0}".format(lock_date))


        test_submissions = assignment.get_submissions()

        a_copy = a.copy()
        for submission in test_submissions:
            ID = None
            if submission.body == None:
                count += 1
            else:
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
			
        message = 'There '+word
        message += ' {} missing submission'+plural+" for {}"
        print(message.format(count, assignment.name))
		
        if now > overdue_date:
            for user in users:
                for item in a_copy:
                    if user.id == item:
                        list_of_overdue_users.append(user.name)
                        list_of_overdue_tests.append(assignment.name)

makeReport(list_of_overdue_users, list_of_overdue_tests)

        