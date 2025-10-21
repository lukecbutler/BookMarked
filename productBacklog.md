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
for sprint 0 - project setup, ie. how do we coordinate, frontend, backend, db technology
priorities on backlog items
you need to know the due date as soon as it gets checked out
due dates vary depending on the type of item


highest priority items:


1. patron can check out a book
    check if the card is available
    be able to update the card


1. Checkout Item [items: movie's, books, newMovies's]
there are three conditoins to which not to checkout item
    1. card expired (if expired extend patrons library card)
    2. fine on account (off of system - will be done manually)
    3. too many books checke dout (20 book limit)
        If too many books - notify & automatically close transaction
    4. Each item has it's own due date

AC:
- track when book was checked out, how long it can be rented for


2. Checkout Item - 2 phases,
    1. patron drops off book, check date from book and if the date is late, there will be a fine
    2. check

branches will be from the start
2 branches

high priority:
checkout items 1. 
return items 2. 
reshelving 3. 

(populate database with books, other items and patrons)
low:
?

Sprint 1 user stories:
1. Checkout Item
2. Check in Item
3. Reshelve Item



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

(what happens between 2 and 3 is outside of the system)
after check in, books go into bin's, into damaged bin, different branch bin, my library bin - all three cases the book is still unavailable

3. Reshelf Item: (Book is available in )
    1. Here's the book, make it available



prompt user book is unavailable at some point
EACH ITEM SHOULD HAVE IT'S OWN STATE


BACKEND ONLY: add books and add patrons (these will be added in sprint 2 or 3)
Adding books & patrons

model THESE 3 - CLARIFY FOR TEAM