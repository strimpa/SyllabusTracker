# SyllabusTracker
A simple application to register users and track their progress through a syllabus with additional student management systems.
The logic is done as a server-side web-application with minimal client side logic for maximum device accessibilty.
Written with the beautiful [Django framework](https://www.djangoproject.com/)

[Website linking to this repository](http://www.SyllabusTracker.club)

mail@SyllabusTracker.club

Main contributor: [Strimpa](https://github.com/strimpa)

## What does this do?
- Upload a syllabus with n-to-n grouping of exercises
- Syllabus display can be filtered - URLs contain filters and ankers
- Sessions can be stored with attendees and exercise groups to be revised by users
- Self-rating of exercise proficiency
- Instructors can then see summaries of that data to decide on training contents
- Fee payments can be set-up
- Email reminders for session revision and fee expiries

This is primarily for local clubs to manage typical chores that don't require personal data or additional intelligence for processing the stored information.

## This doesn't work!
Please (please!) send any bugs to https://freedcamp.com/Web__Django_OF4/SyllabusTracker_f7V/todos

## How to set this up
Dependencies are kept minimal

- Django
- pillow for images
- jquery
- jquery-ui with calender/datepicker/accordion
- timepicker jquery-ui plugin

1. Install Django, MySQL backend recommended
2. Clone or download repository
3. Setup server for django publishing
4. Run migrations
5. Setup per-club data
   - Kyu-grade structure
   - Fee definitions
   - Upload syllabus and/or manually edit on dedicated page
6. Ensure email backend is working
7. Send us any bugs!

## License
Sharing is caring!
GNU General Public License v3.0
See LICENSE.txt or https://choosealicense.com/licenses/gpl-3.0/#
