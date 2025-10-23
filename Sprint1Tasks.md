Starting tasks:
1. Create bones of flask app[]
2. Populate database with Patrons, Items & Branches

LIS-001: Checkout Item

A. Write function to check if Patron Account is expired.
B. Write a function to extend Patron Account expiration date
C. Write a function that checks if the number of items a patron has is already at the max
D. Write a function that records the checkout.
E. Write a function that 



##### ------------------------------------------------------------------------------------------------- #####
Logic for user story 1:
1. Library inputs Patron ID
2. System checks if the patrons account is expired
    a. If the patrons account is expired, librarian is prompted to extend the account
3. System checks for late fees on account
4. System will check out one book at a time.
    For every book checked out:
        a. Checks if # of items checked out has been hit.
        b. record checkout in db
        c. display due date

User Story 1 tasks[Check-out]:
1. Function to accept user input of Patron ID
2. Function to check if account is expired
3. Function to extend patron account
4. Function to check for late fees
5. Function to close transaction if there is a late fee
6. Function to check if # of items chekced out has been hit
7. Function to record the checkout in database
8. Function to display the due date


User Story 2 tasks[Check-in]:
1. A function that displays all items Checked out by a patron
2. A function that checks if a book is overdue, calculates the late fee, and updates Patron account
3. A function that records return in the database


User Story 3 tasks[Reshelve]:
1. A function to search items
2. A function to change availability attribute