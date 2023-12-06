In this Flask Application we create a backend for a ticketing service, and users. this application makes it so a user is able to create an account while passwords are hashed, as well as make sure a user is the correct user logging in. As for our Tickets you are able to create a ticket with an automatic status of 'new', you are able to edit this status, and delete the tickets when needed

Routes:
#/login - used to login user
#/new_user - used to create new user
#/new_ticket -used to make a new ticket
#/edit_ticket/<id> - used to edit ticket status
#/delete_ticket/<id>  - used to delete ticket
#/ticket/<id>  - used to get specific ticket
#/tickets - used to get all tickets

Things I would like to add to this application are:
 -a admin status that can be changed when a user needs to be an admin
 -a way to show all users
 -a way to edit users admin status
 -a way to delete users