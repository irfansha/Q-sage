%===============================================================
#blackactions
%action 1
:action down
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x,?y+1))
:effect (open(?x,?y) black(?x,?y+1))
%action 2
:action down-two
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x,?y+1) open(?x,?y+2))
:effect (open(?x,?y) black(?x,?y+2))
%action 3
:action up
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x,?y-1))
:effect (open(?x,?y) black(?x,?y-1))
%action 4
:action up-two
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x,?y-1) open(?x,?y-2))
:effect (open(?x,?y) black(?x,?y-2))
%action 5
:action right
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x+1,?y))
:effect (open(?x,?y) black(?x+1,?y))
%action 6
:action right-two
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x+1,?y) open(?x+2,?y))
:effect (open(?x,?y) black(?x+2,?y))
%action 7
:action left
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x-1,?y))
:effect (open(?x,?y) black(?x-1,?y))
%action 8
:action left-two
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x-1,?y) open(?x-2,?y))
:effect (open(?x,?y) black(?x-2,?y))
%action 9
:action left-diagonal-up
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x-1,?y-1))
:effect (open(?x,?y) black(?x-1,?y-1))
%action 10
:action right-diagonal-up
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x+1,?y-1))
:effect (open(?x,?y) black(?x+1,?y-1))
%action 11
:action left-diagonal-down
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x-1,?y+1))
:effect (open(?x,?y) black(?x-1,?y+1))
%action 12
:action right-diagonal-down
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x+1,?y+1))
:effect (open(?x,?y) black(?x+1,?y+1))
%action 13
:action stay
:parameters (?x, ?y)
:precondition (black(?x,?y))
:effect (black(?x,?y))
%===============================================================
#whiteactions
%action 1
:action down
:parameters (?x, ?y)
:precondition (white(?x,?y))
:effect (open(?x,?y) white(?x,?y+1))
%action 2
:action up
:parameters (?x, ?y)
:precondition (white(?x,?y))
:effect (open(?x,?y) white(?x,?y-1))
%action 3
:action right
:parameters (?x, ?y)
:precondition (white(?x,?y))
:effect (open(?x,?y) white(?x+1,?y))
%action 4
:action left
:parameters (?x, ?y)
:precondition (white(?x,?y))
:effect (open(?x,?y) white(?x-1,?y))
%action 5
:action stay
:parameters (?x, ?y)
:precondition (white(?x,?y))
:effect (white(?x,?y))
%===============================================================
