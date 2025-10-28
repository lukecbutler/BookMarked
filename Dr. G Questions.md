## Meeting 2 Questions ##
1. How & where would you like the notification to appear if the patron cannot checkout an item in the library due to current fines?
1A:

Priority of checks in checkout:
    1. Check the library card expiration date first
        if expired - create new expiration date [have an option for extending expiration date given to the user]
    2. Check fine balance second
        if fines - if the patron can pay, set fine amount to 0, then continue
        else: the patron cannot pay, close the transaction
    3. Check number of books
        if 20 or more books - prompt saying 'patron has exceeded number of checkouts, please check in a book to checkout another one'
        then button that say's 'close transaction'

**always give note of entire process to the user, 
as if they have never used the system before**

Checkin & Reshelve are high priority

The client just tells you what they want
The team decides what to actually work on, to have a finished project. e.g. if there are 100 wishes, and we can only do 10, we need to decide which 10 provide the most value. 


2. Personal Q - From what you have seen so far, what are points of what I should be focused on improving personally?
    1. She would like to see the flow from the client -> product owner -> analysts -> developers

* Create mockup of designs/ flow and bring to dr. G

* groups should be confirming with client (dr. G) about flow of process in web application before developing, as she is the client and needs to like it.


Patrons should be getting late fees based on every single late book they return. 


e.g. Patron returns a book late, they are charged for every day late for that book. If they turn in a different book a different amount of days late, they are charged that amount of days late feee for that book.


late fees are added to their account for each late book for each day late

------------------------------
Dr. G decides the rules
We decide what we can build
------------------------------
# Improve task board - make tasks smaller - everyone needs tasks

# Use Trello board more & properly

# Dr. G really think we need to work on team workflow & trello board

# Include wireframe of user stories before you build it. -> Then run it by the client

# Design in figma/justinmind before building
# Don't run to far if you don't know what they want




Possible Qs / Ideas

- The per-day fine for an item is calculated based on its cost; for example, if the fine is one-tenth of the cost, a $10 item would have a $1 per-day fine.

per_day_fine_in_cents=(item.cost_in_cents // 100)
