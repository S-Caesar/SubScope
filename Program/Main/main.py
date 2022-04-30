# -*- coding: utf-8 -*-

from Program.Main import UserInterface as ui

from Program.Main import InitialSetup as ins

ins.initialise()

mainMenu = ui.MainMenu()
mainMenu.show()