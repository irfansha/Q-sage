#boardsize
3 3
#init
#depth
3
#blackgoal
%each line represents a shape with one orientation
black(?x,?y) black(?x,?y-1)
black(?x,?y) black(?x-1,?y)
#whitegoal
white(?x,?y) white(?x,?y-1)
white(?x,?y) white(?x-1,?y)
