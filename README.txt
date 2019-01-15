'KetchUp!' 

A game created by Wei Xin Lee for 15-112 (Fundamentals of Programming and Computer Science) Fall '17 Term Project.

Link to demo video: https://youtu.be/PZKkppOiAN8

Note: Although these files are now on GitHub, when I first developed this, I did not yet have a GitHub account. As
      such, all version control is stored in ProjectCodebase/VersionControl

____________________________________________________________________________________________________________________
********************************************************************************************************************

The game has two gamemodes:

	1. Chase Mode
	   Players chase each other around the map on a time-based rotation. This mode is played by two
	   players on the same keyboard and two computer characters.
	   
	   Power ups included:
		- Boots
		- Snail
		- Shield

	2. Shoot Mode:
	   Players pick up weapons along the way which can be used to shoot each other and gain points.
	   This mode is played by four players across multiple computers.
	   
	   Power ups included:
		- Gun
		- Laser
		

Settings included:

	1. Board Size
	   There are three different board sizes - small, medium and large.

	2. Number Of Points To Win
	   There are three different options - 3, 5 and 7.
	
	3. Show/Hide Timer (for Chase Mode)
	   You can choose to show or hide the 10 second timer for each turn in chase mode.

	4. Computer Difficulty (for Chase Mode)
	   There are two difficulties for the AIs - easy and hard.
	   

How to run the game:

	1. Install Pygame on your computer
	   Download Pygame from this website: http://www.pygame.org/download.shtml
	   If you experience difficulty, instructions can be found here: (Courtesy of Lukas Peraza)
	   https://qwewy.gitbooks.io/pygame-module-manual/content/installation.html

	2. Find your IP address on Google and update the following files:
	   a) 'server' - line 13
	   b) 'MAIN_player1_client' - line 19
	   c) 'player2_client' - line 18
	   d) 'player3_client' - line 18
	   e) 'player4_client' - line 18
	
	3. Run the 'server' file on your computer's terminal.
	   - Navigate to the directory containing your files using 'cd <path>'
	   - Run the file using 'py server.py'

	4. Run the 'MAIN_player1_client' file as script in any Python IDE.

	5. If playing Shoot Mode multiplayer across computers,
	   - Each player would have to download Pygame
	   - Each player must input the IP address used by player 1 to start the server in their client file
	   - On each computer, run the player client file as script in any Python IDE.

	   !!IMPORTANT!!
	   You MUST run the player files IN ORDER. Meaning player 1 will start the server, then run his/her client file. 
	   Then player 2 will run his/her client file, then player 3 and so on. Not following the order exactly will cause
	   the game to be undefined and it will not work properly.
	   
