#blackactions
%action 1
:action forward
:parameters (?x, ?y)
:precondition (black(?x,?y) open(?x,?y-1))
:effect (open(?x,?y) black(?x,?y-1))
%action 2
:action left-diagonal
:parameters (?x, ?y)
:precondition (black(?x,?y) NOT(black(?x-1,?y-1)))
:effect (open(?x,?y) black(?x-1,?y-1))
%action 3
:action right-diagonal
:parameters (?x, ?y)
:precondition (black(?x,?y) NOT(black(?x+1,?y-1)))
:effect (open(?x,?y) black(?x+1,?y-1))
#whiteactions
%action 1
:action forward
:parameters (?x, ?y)
:precondition (white(?x,?y) open(?x,?y+1))
:effect (open(?x,?y) white(?x,?y+1))
%action 2
:action left-diagonal
:parameters (?x, ?y)
:precondition (white(?x,?y) NOT(white(?x-1,?y+1)))
:effect (open(?x,?y) white(?x-1,?y+1))
%action 3
:action right-diagonal
:parameters (?x, ?y)
:precondition (white(?x,?y) NOT(white(?x+1,?y+1)))
:effect (open(?x,?y) white(?x+1,?y+1))
