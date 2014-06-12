The hive system is a system for programming with connected components (nodes). It be used visually or from Python. It can be used with any library or game engine with Python support: currently it has bindings for the Blender Game Engine (BGE) and Panda3D.

The documentation and learning resources for the hive system are:
- The installation instructions
- The Tetris demo
- The tutorial
- The manual

The Tetris demo gives recipe-style instructions for building a Tetris game, but it does not explain the hive system.
The first chapter of the tutorial gives a gentle introduction to the hive system and it concepts. It is mostly at the GUI level, with a bit of Python mixed in.
The second chapter of the tutorial describes a case study: the drawing of 2D shapes. 
 The first part is GUI-oriented, showing how to use various implementations for shape-drawing. 
 The second part is Python-oriented, showing how the various implementations are created.
The third chapter of the tutorial is a detailed explanation of the various layers (visual and Python) in the hive system and how they are relate to each other.
The manual provides a detailed overview of the mechanics of the hive system, principally at the Python level.

Non-programmers are recommended to start with the first chapter of the tutorial together with the Tetris demo.
Programmers are encouraged to start with the third chapter of the tutorial.

For programmers who like to browse the source: dragonfly, the standard node library, is a good place to start. Browsing "bee" or "libcontext" is not recommended.

Additional resources

You can also find an example for Blender here: http://wiki.blender.org/index.php/File:Test-Hivesystem-movingpanda-BGE.tgz
The zipped directory contains a .blend file and several hive maps that you can edit with the GUI. The main game logic is Python-based and involves hive binding, a feature that is not yet available in HiveGUI.
