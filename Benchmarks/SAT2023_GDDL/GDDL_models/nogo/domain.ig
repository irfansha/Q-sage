#blackactions
%action 1
:action occupy
:parameters (?x, ?y)
:precondition (open(?x,?y))
:effect (black(?x,?y))
%-------------------------------
#whiteactions
%action 1
:action occupy
:parameters (?x, ?y)
:precondition (open(?x,?y))
:effect (white(?x,?y))