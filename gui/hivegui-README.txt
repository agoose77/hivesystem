Navigating the canvas:

Use arrow keys to move along the canvas, or press Shift+LButton
Use mousewheel or + / - keys to zoom in / out

How to create new workers:

Open up the worker tree (e.g. dragonfly => std => variable) 
and drag the label onto the canvas
The "Delete" key removes workers

Copy and paste are implemented as Ctrl+C, Ctrl+V
Undo is not yet implemented.

How to make connections:

Antenna hooks are on the left side of the worker, Output hooks on the right side.
Hooks have two modes  (push and pull), and a type. 
Push hooks are circles, making solid connections. 
Pull hooks are diamonds, making dashed connections.
Mode and type are shown in the status bar when hovering.

To make a new connection, LClick on an Output hook, keep the LButton pressed.
 While LButton is pressed, RClick to make interpolation points (optional).
Then, move the mouse onto an input hook and release the LButton. If the types and modes match, a connection will be established. To force a connection, keep the Ctrl down while releasing.

Managing connections:

Except for pull Antenna, hooks can have multiple connections attached,
To select one connection, hover over the hook and press Tab or Backspace.

To (re)move a connection, LClick on its input hook (end point), and drag. 
This will affect the selected or the most recent connection.

The order of connections is only important in case of push Output hooks.
The connection order can be seen by the initial direction of the connections.
The first connection moves northeast, while the last connection moves southeast.
To change the connection order, select a connection and press + and - or a number.
