#blackactions
%action 1
:action occupy
:parameters (?x, ?y)
:precondition (open(?x,?y) (NOT(open(?x,?y+1))))
:effect (black(?x,?y))
%action 2
:action occupy-bottom
:parameters (?x, ?y)
:precondition (open(?x,ymax))
:effect (black(?x,ymax))
#whiteactions
%action 1
:action occupy
:parameters (?x, ?y)
:precondition (open(?x,?y) (NOT(open(?x,?y+1))))
:effect (white(?x,?y))
%action 2
:action occupy-bottom
:parameters (?x, ?y)
:precondition (open(?x,ymax) open(?x,ymax))
:effect (white(?x,ymax))
