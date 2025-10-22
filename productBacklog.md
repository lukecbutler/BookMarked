Product Backlog
SPRINT 0
As a librarian, I want to add a new patron's details (name, address, contact) into the system.
As a librarian, I want to be able to view existing patron's.

SPRINT 1
As a librarian, I am able to checkout a book in the system to a selected patron.
As a librarian I am able to check back in a book
As a librarian, I am able to add books to the library
As a librarian I am able to create an new patron account at the library.
As a librarian, I can check if I owe a patrons owes any fines

SPRINT 2
As a librarian, I can see if a patron has checked out more than the maximum amount allowed
As a librarian, I am able to add a fine to a patron account indicating an overdue library book
As a librarian, I am able to add different items for checkout (e.g. electronic media)

SPRINT 3
As a libarian, I can check which branch the book belongs to
As a librarian I am able to renew a patrons library card / membership 
As a librarian, I can ensure the patron's membership is active 
As a librarian, I am able to change a books location from one branch to another 
As a librarian, I want to view reports on checkouts, returns, fines, and patron activity. 


Product Backlog:
https://docs.google.com/spreadsheets/d/1PP7BaWFrvVPpQxypPUI-oNMLrsI0S1pPE7Cr69k_eeM/edit?gid=0#gid=0


Dr. g meeting notes:
## highest priority user stories: ##
SPRINT 1 USER STORIES:
1. Checkout Item [items: movie's, books, newMovies's] (available)
there are three conditoins to which not to checkout item
    1. card expired (if expired extend patrons library card)
    2. fine on account (off of system - will be done manually)
    3. too many books checke dout (20 book limit)
        If too many books - notify & automatically close transaction
    4. Each item has it's own due date - each item will maintain it's state

    Due date is attached to the Book, which is attached to the patron

2. Check in Item: (unavailable) - book should be able to be returned to any branch
    1. Item is checked for due date return, if the item is passed due date, assign patron a late fee, remove from patron account
    2. If damaged, give status 'unavailable'
    3. Check Items location

3. Reshelf Item: (Book is available in )
    1. Here's the book, make it available



