#blackactions
%action 1
:action vertical
:parameters (?x, ?y)
:precondition (open(?x,?y) open(?x,?y+1))
:effect (black(?x,?y) black(?x,?y+1))
#whiteactions
%action 1
:action horizontal
:parameters (?x, ?y)
:precondition (open(?x,?y) open(?x+1,?y))
:effect (white(?x,?y) white(?x+1,?y))
