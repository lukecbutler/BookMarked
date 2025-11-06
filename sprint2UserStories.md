Product Backlog:
https://docs.google.com/spreadsheets/d/1PP7BaWFrvVPpQxypPUI-oNMLrsI0S1pPE7Cr69k_eeM/edit?gid=0#gid=0

Sprint 1 User Stories & Explaination:
https://docs.google.com/document/d/1E6apVPr4awMuaj2UDfg5xsIbd9r3mprfmUElRIJyR3Y/edit?usp=sharing

The goal of sprint 2 is to polish our application to ensure all acceptance criteria is met within our applicaiton
Also:
1. State machine diagram of the Item needs to be redone
2. The activity diagrams for the different user stories should not have more than one end point, and should not leave the user in an ending state unless it is the very end of the diagram. Every failure to checkout should loop back to the start.

# 1. Checkout
## As a librarian, I am able to checkout an item to a patron ##
1. Patron is found by their patron ID
2. Item to checkout is added by the itemID
3. Item is checked out on a certain date
4. If the Item is checked back in after the due date, $1 for every number of days it was late is added to that patrons fees, up to the value of that Item
5. Patron is checked for an active membership
6. If the patron does not have an active membership, the system has the capability to:
    1. Extend membership to a certain date
    2. Abort the checkout
7. The patron cannot checkout a book if they do not have an active membership.
8. No patron can exceed 20 checkouts at any given time.
9. No patron can checkout more than one of the exact same item.

# 2. Checkin
## As a librarian, I am able to check back in an item based on its item ID
1. Librarian is able to check back in an item based on an itemID
2. Librarian is able to check back in an item on a specific date
3. If the checkin date of an item is past the due date, the patron that checked out the item has a charge added to their account equal to $1/day past the due date up to the price of the item on their account
4. Item is able to be checked back in to either of the branches
5. An item cannot be checked in more than one time.

# 3. Resheve
## As a librarian I am able to reshelve an Item
1. Item is set to Available again, from the checked=in state.
2. An Item cannot be reshelved more than once.
