# GroupMe
Ever been a lonely soul in elective classes? Need to find a group but don't know any other person? 
Use GroupMe to find your groupmates easy-peasy! No more hassle to individually DM your classmates!

## What you can do?
1. Creating shareable class codes.
2. Joining classes.
3. Setting your schedule.
4. Find your best fit groupmates.

## Tech-Stack
- Frontend - Javascript
- Backend API - FastAPI

## File Structure
```bash
├── app
│   ├── templates      # HTML and svg files.
│   ├── main.py        # FastAPI functions, algorithms, routes.
│   ├── models.py      # Pydantic models.
│   ├── passcodes.py   # Function for obtaining passcodes.
│   ├── tests.py       # Unit tests for API functions.
├── README.md
└── requirements.txt   # Required versions, libraries for project.
```

## Instructions for Users

A. Creating shareable class codes
- In the home page, click on 'or create a new class'.
- In the create class page, enter the class name, description, and maximum member count.
- Once submitted, a class code will be displayed in the same page that you need to remember (the code will look something like this: 'ABC123').

![Screenshot](https://github.com/Pardigle/groupme/blob/main/demo/DEMO2.png)

B. Joining classes
- In the home page, enter a valid passcode (if you have no passcode, see steps for A).
- Once submitted, you will be prompted to create a student profile.
- Once necessary student profile information is filled up, you will be redirected to the class view where you are able to see the details and members of the class.

![Screenshot](https://github.com/Pardigle/groupme/blob/main/demo/DEMO1.png)

C. Setting your schedule
- Once joined in a class (see steps for B), you will be presented a table which contains timeslots for the days of the week.
- To set your schedule, click and drag on the timeslots in which you consider as free-time or times which are most amicable for you to work with your group.
- To save your schedule, remember to click on the save button on the top-right of the page.

![Screenshot](https://github.com/Pardigle/groupme/blob/main/demo/DEMO3.png)

D. Find your best fit groupmates
- Once joined in a class (see steps for B) and set your schedule (see steps for C), on the top-right of the class view, click the 'Group Me' button.
- Once clicked, you will be redirected to the view groupmates page.
- In the page, you need to specify whether you want your groupmates to be found through the cumulative or consecutive hours you have in common with them.
- Once specified, you can press the search icon button which will display on a table the ranking of members that fit your schedule.

![Screenshot](https://github.com/Pardigle/groupme/blob/main/demo/DEMO4.png)
![Screenshot](https://github.com/Pardigle/groupme/blob/main/demo/DEMO5.png)
