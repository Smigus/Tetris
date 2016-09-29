import Tkinter as tk
from Tkinter import *
from tkColorChooser import askcolor
import time
import random
import math
import copy

class Rules:
    """ Defines basic Rules of the game
    """
    # not customizable
    defaultRows = 15
    defaultCols = 10
    defaultCellSize = 35
    marginWidth = 30

    # customizable
    rows = 15
    cols = 10
    rotationDirection = -1
    scoringMechanism = "Quadratic"
    scoringLevelDependence = 0

    @staticmethod
    def cellSize():
        """Returns the cell size that fits the current number of rows and cols
        """   
        return float(Rules.defaultCellSize) * Rules.defaultRows / Rules.rows \
            if float(Rules.defaultRows) / Rules.rows < \
            float(Rules.defaultCols) / Rules.cols else \
            float(Rules.defaultCellSize) * Rules.defaultCols / Rules.cols

class Application:
    """Presents different controllers"""
    def __init__(self):
        self.root = Tk()
        
        self.game = Game(self.root)
        self.settings = Settings(self.root)
        self.pieceEditor = PieceEditor(self.root)
        self.main = Main(self.root, [self.game, self.pieceEditor, \
                self.settings])
        self.controllers = [self.main, self.game, self.pieceEditor,
                self.settings]

    def run(self):
        """Presents the active controller"""
        noActive = False
        while True:
            if noActive:
                self.main.isActive = True
            for controller in self.controllers:
                while controller.isActive:
                    controller.run()
                noActive = controller != self.main

class Controller:
    """Base class of all controllers"""
    
    def __init__(self, root):
        self.isActive = False
        self.root = root
        self.frame = Frame(self.root)

    def run():
        pass

class Main(Controller):
    """Controller that allows navigation to different controllers"""
    
    def __init__(self, root, controllers):
        Controller.__init__(self, root)
        self.isActive = True
        self.game = controllers[0]
        self.pieceEditor = controllers[1]
        self.settings = controllers[2]
        self.menu = MainMenu(parent = self.frame)
        self.menu.pack()
        self.root.resizable(width = 0, height = 0)

    def run(self):
        self.frame.grid(sticky = tk.NW + tk.NE + tk.SE + tk.SW)
        self.menu.drawMenu()
        self.bindEvents()
        self.frame.mainloop()

    def bindEvents(self):
        self.menu.tag_bind(self.menu.gameButton, "<Button-1>", self.toGame)
        self.menu.tag_bind(self.menu.gameButtonText, "<Button-1>", self.toGame)
        self.menu.tag_bind(self.menu.settingsButton, "<Button-1>", \
                self.toSettings)
        self.menu.tag_bind(self.menu.settingsButtonText, "<Button-1>", \
                self.toSettings)
        self.menu.tag_bind(self.menu.pieceEditorButton, "<Button-1>", \
                self.toPieceEditor)
        self.menu.tag_bind(self.menu.pieceEditorButtonText, \
                "<Button-1>", self.toPieceEditor)

    def toGame(self, event):
        """Navigates to Game controller."""
        self.isActive = False
        self.game.isActive = True
        self.resetController()

    def toSettings(self, event):
        """Navigates to Settings controller."""
        self.isActive = False
        self.settings.isActive = True
        self.resetController()

    def toPieceEditor(self, event):
        """Navigates to Piece Editor controller"""
        self.isActive = False
        self.pieceEditor.isActive = True
        self.resetController()

    def resetController(self):
        """Resets the Main controller to initial state"""
        self.frame.quit()
        self.frame.destroy()
        self.frame = Frame(self.root)
        self.menu = MainMenu(parent = self.frame)
        self.menu.pack()

class PieceEditor(Controller):
    """Controller that manages piece creation and editing"""
    def __init__(self, root):
        Controller.__init__(self, root)

    def run(self):
        self.frame.grid(sticky = tk.NW + tk.NE + tk.SW + tk.SE)
        
        self.buildMenu()
        
        self.frame.mainloop()

    def protectStandardPieces(self):
        """Prevent the 7 standart pieces from being deleted"""
        customizedPieceSet = set(Piece.knownShapes) - set(Piece.standardPieces)
        pieceList = Piece.standardPieces + list(customizedPieceSet)
        for i in xrange(len(self.menu.deleteButtons) - 1, -1, -1):
            if pieceList[i] in Piece.standardPieces:
                self.menu.delete(self.menu.deleteButtons[i])
                self.menu.deleteButtons.pop(i)

    def menuBindEvent(self):
        """Binds events for the basic piece editing menu"""
        self.menu.tag_bind(self.menu.mainMenuButton, \
                "<Button-1>", self.toMainMenu)
        self.menu.tag_bind(self.menu.addPieceButton, \
                "<Button-1>", self.showAddPieceMenu)
        for deleteButton in self.menu.deleteButtons:
            self.menu.tag_bind(deleteButton, "<Button-1>", self.deletePiece)

    def addPieceMenuBindEvents(self):
        """Bind events for the piece creation interface"""
        self.addPieceMenu.tag_bind(self.addPieceMenu.backButton, \
                "<Button-1>", self.backToMenu)
        self.addPieceMenu.tag_bind(self.addPieceMenu.saveButton, \
                "<Button-1>", self.savePiece)
        self.root.bind("<Button-1>", self.selectCell)
        self.root.bind("<Button-2>", self.chooseColor)

    def showAddPieceMenu(self, event):
        """Initializes and shows the piece creation interface"""
        self.addPieceMenu = AddPieceMenu(self.frame)
        self.addPieceMenu.drawMenu()
        self.addPieceMenuBindEvents()
        self.menu.destroy()
        self.vbar.destroy()
        self.addPieceMenu.pack()

    def deletePiece(self, event):
        """Deletes a user-created piece"""
        customizedPieceSet = set(Piece.knownShapes) - set(Piece.standardPieces)
        pieceList = Piece.standardPieces + list(customizedPieceSet)
        hh, uh = self.menu.headerHeight, self.menu.unitHeight
        i = int((self.menu.canvasy(event.y) - hh) / uh)
        Piece.forgetPiece(pieceList[i])
        self.menu.destroy()
        self.vbar.destroy()

        self.buildMenu()

    def selectCell(self, event):
        """Changes the shape of the piece that the user is creating
           and renders the shape to the user
        """
        x, y = event.x, event.y
        rows, cols = self.addPieceMenu.rows, self.addPieceMenu.cols
        mw, sc = self.addPieceMenu.marginWidth, self.addPieceMenu.cellSize
        if mw < x < mw + cols * sc and mw < y < mw + rows * sc:
            j = int(x - self.addPieceMenu.marginWidth) / \
                    self.addPieceMenu.cellSize
            i = int(y - self.addPieceMenu.marginWidth) / \
                    self.addPieceMenu.cellSize
            self.addPieceMenu.itemconfigure(self.addPieceMenu.cells[i][j], \
                    fill = self.addPieceMenu.emptyColor if \
                    self.addPieceMenu.shape[i][j] else self.addPieceMenu.color)
            self.addPieceMenu.shape[i][j] = not self.addPieceMenu.shape[i][j]

    def chooseColor(self, event):
        """Changes the color of the piece that the user is creating
           and renders the color to the user
        """
        color = str(askcolor()).split()[-1][0:-1].strip("\'")
        if color != "None": self.addPieceMenu.color = color
        for i in xrange(len(self.addPieceMenu.shape)):
            for j in xrange(len(self.addPieceMenu.shape[0])):
                if self.addPieceMenu.shape[i][j]:
                    self.addPieceMenu.itemconfigure(\
                        self.addPieceMenu.cells[i][j], \
                        fill = self.addPieceMenu.color)
                    

    def savePiece(self, event):
        """Saves the user-created piece"""
        if self.addPieceMenu.shapeIsRecommended:
            shape = self.addPieceMenu.interpretedShape
            color = self.addPieceMenu.color
            name = str(shape)
            Piece.learnPiece(name, shape, color)
            self.backToMenu(None)
        else:
            self.addPieceMenu.itemconfigure(\
                self.addPieceMenu.warnings, fill = "red")

    def backToMenu(self, event):
        """Dismiss the piece creation interface
           and show the basic piece editor menu"""
        self.addPieceMenu.destroy()
        self.buildMenu()

    def buildMenu(self):
        """Initializes the basic piece editor menu"""
        self.menu = PiecesMenu(self.frame)
        self.vbar = Scrollbar(self.frame, orient = VERTICAL, \
                command = self.menu.yview)
        self.vbar.pack(side = RIGHT, fill = Y)
        self.menu.config(yscrollcommand = self.vbar.set)
        self.menu.drawMenu()
        self.protectStandardPieces()
        self.menuBindEvent()
        self.menu.pack()

    def toMainMenu(self, event):
        """Navigate back to the Main controller"""
        self.isActive = False
        self.frame.quit()
        self.frame.destroy()
        self.root.unbind("<Button-1>")
        self.root.unbind("<KeyPress>")
        self.frame = Frame(self.root)


class Settings(Controller):
    """Controller that allows the user to
       customize board size, piece rotation, and scoring settings
    """
    def __init__(self, root):
        Controller.__init__(self, root)
        self.rowsSet = StringVar()
        self.colsSet = StringVar()
        self.rotationDirectionSet = IntVar()
        self.scoringMechanismSet = StringVar()
        self.scoringLevelDependenceSet = IntVar()

    def run(self):
        self.frame.grid(sticky = tk.NW + tk.NE + tk.SW + tk.SE)
        self.createRotationSettings()
        self.createBoardSizeSettings()
        self.createScoringSettings()
        self.createMainMenuButton()
        self.frame.mainloop()

    def createMainMenuButton(self):
        """Creates the button that navigates to the Main controller"""
        self.mainMenuButton = Button(self.frame, text = "Main Menu", \
                command = self.toMainMenu)
        self.mainMenuButton.grid(rows = 2, sticky = tk.W + tk.E)

    def createRotationSettings(self):
        """Creates the interface that allow the user
           to change piece's rotation direction
        """
        self.rotationSettingsTitle = Label(self.frame, \
                text = """Choose how pieces rotate.""")
        self.rotationSettings = (Radiobutton(self.frame, text = "clockwise", \
                variable = self.rotationDirectionSet, value = 1), \
                Radiobutton(self.frame, text = "counterclockwise", \
                variable = self.rotationDirectionSet, value = -1))
        self.rotationSettingsTitle.grid(row = 0, column = 0, \
                sticky = tk.W + tk.S)
        self.rotationSettings[0].grid(row = 1, column = 0, sticky = tk.W)
        if Rules.rotationDirection == 1:
            self.rotationSettings[0].select()
        else: self.rotationSettings[1].select()
        self.rotationSettings[1].grid(row = 2, column = 0, sticky = tk.W)

    def createBoardSizeSettings(self):
        """Creates the interface that allow the user
           to change number of rows and cols of the game board
        """
        self.rowsSet.set(Rules.rows)
        self.colsSet.set(Rules.cols)
        rowsOptionList = list(xrange(9, 31))
        colsOptionList = list(xrange(6, 21))
        self.boardSizeSettingsTitle = Label(self.frame, justify = tk.LEFT, \
                text = """Choose the game board size.
Recommended: c ≤ r ≤ 2c""")
        self.boardSizeSettings = ((Label(self.frame, text = "Rows"), \
                 OptionMenu(self.frame, self.rowsSet, *rowsOptionList)), \
               (Label(self.frame, text = "Cols"), \
                OptionMenu(self.frame, self.colsSet, *colsOptionList)))
        self.boardSizeSettingsTitle.grid(row = 0, column = 1, \
                sticky = tk.W + tk.S, columnspan = 2)
        self.boardSizeSettings[0][0].grid(row = 1, column = 1, sticky = tk.W)
        self.boardSizeSettings[0][1].grid(row = 1, column = 2)
        self.boardSizeSettings[1][0].grid(row = 2, column = 1, sticky = tk.W)
        self.boardSizeSettings[1][1].grid(row = 2, column = 2)

    def createScoringSettings(self):
        """Creates the interface that allow the user
           to change the scoring rules
        """
        self.scoringSettingsTitle = Label(self.frame, justify = tk.LEFT, \
                text = """Choose scoring mechanism.""")
        self.scoringSettings = (Radiobutton(self.frame, \
            text = "Base-4 exponential", \
            variable = self.scoringMechanismSet, value = "Base-4 exponential"),\
            Radiobutton(self.frame, text = "Quadratic", \
            variable = self.scoringMechanismSet, value = "Quadratic"), \
            Checkbutton(self.frame, variable = self.scoringLevelDependenceSet, \
            text = "Scoring depends on level\t"))
        self.scoringSettingsTitle.grid(row = 0, column = 3, \
                sticky = tk.W + tk.S)
        self.scoringSettings[0].grid(row = 1, column = 3, sticky = tk.W)
        if Rules.scoringMechanism == "Base-4 exponential":
            self.scoringSettings[0].select()
        elif Rules.scoringMechanism == "Quadratic":
            self.scoringSettings[1].select()
        self.scoringSettings[1].grid(row = 2, column = 3, sticky = tk.W)
        self.scoringSettings[2].grid(row = 3, column = 3, sticky = tk.W)
        if Rules.scoringLevelDependence == 1:
            self.scoringSettings[2].select()

    def updateRules(self):
        """Saves the changes that the user makes and updates the rules"""
        Rules.rows = int(self.rowsSet.get())
        Rules.cols = int(self.colsSet.get())
        Rules.rotationDirection = self.rotationDirectionSet.get()
        Rules.scoringMechanism = self.scoringMechanismSet.get()
        Rules.scoringLevelDependence = self.scoringLevelDependenceSet.get()

    @property
    def boardSizeIsRecommended(self):
        """Returns whether the ratio between rows and cols is good"""
        return int(self.rowsSet.get()) >= int(self.colsSet.get()) and \
               int(self.rowsSet.get()) <= int(self.colsSet.get()) * 2

    def toMainMenu(self):
        """Navigates back to the Main controller
           or show warnings if the user makes unrecommended changes"""
        if self.boardSizeIsRecommended:
            self.isActive = False
            self.updateRules()
            self.frame.quit()
            self.frame.destroy()
            self.root.unbind("<Button-1>")
            self.root.unbind("<KeyPress>")
            self.frame = Frame(self.root)
        else:
            self.boardSizeSettings[0][0].configure(foreground = "red")
            self.boardSizeSettings[1][0].configure(foreground = "red")

class Game(Controller):
    """The controller that manages the game"""
    def __init__(self, root):
        Controller.__init__(self, root)
        self.root.resizable(width = 0, height = 0)
        self.gameIsOn = True
        self.learnStandardPieces()

    def run(self):
        self.frame = Frame(self.root)
        self.board = Board(parent = self.frame)
        self.board.pack()

        self.frame.grid(sticky = tk.NW + tk.NE + tk.SE + tk.SW)

        self.board.drawButtons()

        self.bindEvents()

        self.startGame()
            
        self.frame.mainloop()

    def learnStandardPieces(self):
        """Save the 7 standard pieces"""
        Piece.learnPiece("iPiece", \
                [[True, True, True, True]], "red")
        Piece.learnPiece("jPiece", \
                [[True, False, False], [True, True, True]], "yellow")
        Piece.learnPiece("lPiece", \
                [[False, False, True], [True, True, True]], "magenta")
        Piece.learnPiece("oPiece", \
                [[True, True], [True, True]], "pink")
        Piece.learnPiece("sPiece", \
                [[False, True, True], [True, True, False]], "cyan")
        Piece.learnPiece("tPiece", \
                [[False, True, False], [True, True, True]], "green")
        Piece.learnPiece("zPiece", \
                [[True, True, False], [False, True, True]], "orange")

    def bindEvents(self):
        self.board.tag_bind(self.board.pauseButton, "<Button-1>", self.pause)
        self.board.tag_bind(self.board.pauseButtonText, \
                "<Button-1>", self.pause)
        self.board.tag_bind(self.board.helpButton, "<Button-1>", self.help)
        self.board.tag_bind(self.board.helpButtonText, \
                "<Button-1>", self.help)
        self.root.bind("<KeyPress>", self.keyPressed)

    def keyPressed(self, event):
        """Handles key presses"""
        if event.keysym == "Left":
            self.moveFallingPiece(0, -1)
            if self.gameIsOn: self.redrawAll()
        elif event.keysym == "Right":
            self.moveFallingPiece(0, 1)
            if self.gameIsOn: self.redrawAll()
        elif event.keysym == "Down":
            self.moveFallingPiece(1, 0)
            if self.gameIsOn: self.redrawAll()
        elif event.keysym == "Up":
            self.rotateFallingPiece(Rules.rotationDirection)
            if self.gameIsOn: self.redrawAll()
        elif event.keysym == "Escape":
            self.pause(event)
        elif event.keysym == "Return":
            self.hardDrop()

    def timerFired(self):
        """Moves the falling piece 1 step down
           and schedules itself for the next call
        """
        if self.gameIsOn:
            self.moveFallingPiece(1, 0)
            if self.gameIsOn: self.redrawAll()
            delay = int(7500. / Rules.rows - self.board.level * 50)
            if delay < 750. / Rules.rows: delay = int(delay = 750. / Rules.rows)
            self.board.after(delay, self.timerFired)
            self.frame.update()

    def newFallingPiece(self):
        """Creates a new falling piece.
           Ends game if it cannot be legally created.
        """
        if not self.gameIsOn: return
        pieceList = list(Piece.knownShapes)
        self.board.fallingPiece = self.board.nextPiece
        self.board.nextPiece = Piece(pieceList[ \
            random.randint(0, len(pieceList) - 1)], Rules.cols)
        if not self.board.isLegal:
            self.endGame()
        
    def moveFallingPiece(self, drow, dcol):
        """Move the falling piece down. Creates a new falling piece if
           the current one can't move or does not exist.
        """
        if not self.gameIsOn: return
        fallingPiece = self.board.fallingPiece
        if fallingPiece == None:
            self.newFallingPiece()
            return
        fallingPiece.position[0] += drow
        fallingPiece.position[1] += dcol
        if not self.board.isLegal:
            fallingPiece.position[0] -= drow
            fallingPiece.position[1] -= dcol
            if drow == 1:
                self.putPieceOnBoard()
                self.removeFullRows()
                self.newFallingPiece()
                return False
        else: return True

    def hardDrop(self):
        """Moves the falling piece down as far as possible"""
        while self.moveFallingPiece(1, 0):
            pass
        if self.gameIsOn: self.redrawAll()

    def rotateFallingPiece(self, direction):
        """Rotates the falling piece about its upperleft corner
           by changing the orientation variable of the piece object
        """
        if not self.gameIsOn: return
        initialOrientation = self.board.fallingPiece.orientation
        self.board.fallingPiece.orientation = \
                (initialOrientation + direction) % 4
        if not self.board.isLegal:
            self.board.fallingPiece.orientation = initialOrientation

    def putPieceOnBoard(self):
        """Put the falling piece on the board as it can't move down"""
        for cell in self.board.fallingPieceCells:
            self.board.colorContent[cell[0]][cell[1]] = \
                    self.board.fallingPiece.color
        
    def redrawAll(self):
        """Redraws the game board"""
        self.board.drawGame()

    def startGame(self):
        """Starts the game by creating the falling piece and the next piece
           and starting the timer"""
        pieceList = list(Piece.knownShapes)
        self.board.nextPiece = Piece(pieceList[ \
            random.randint(0, len(pieceList) - 1)], Rules.cols)
        self.redrawAll()
        self.frame.after(int(7500. / Rules.rows), self.timerFired())

    def endGame(self):
        """Ends the game by unbinding all buttons and stopping the timer"""
        self.gameIsOn = False
        self.board.drawGameOverMenu()
        self.board.tag_unbind(self.board.pauseButton, "<Button-1>")
        self.board.tag_unbind(self.board.pauseButtonText, "<Button-1>")
        self.board.tag_unbind(self.board.helpButton, "<Button-1>")
        self.board.tag_unbind(self.board.helpButtonText, "<Button-1>")
        self.root.unbind("<KeyPress>")
        self.board.tag_bind(self.board.restartButton, \
                "<Button-1>", self.restart)
        self.board.tag_bind(self.board.mainMenuButton, \
                "<Button-1>", self.toMainMenu)

    def pause(self, event):
        """Makes a pause by stopping the timer and shows the pause menu"""
        if self.gameIsOn:
            self.gameIsOn = False
            self.board.drawPauseMenu()
            self.board.tag_bind(self.board.resumeButton, \
                    "<Button-1>", self.resume)
            self.board.tag_bind(self.board.restartButton, \
                    "<Button-1>", self.restart)
            self.board.tag_bind(self.board.mainMenuButton, \
                    "<Button-1>", self.toMainMenu)
        else: self.resume(event)

    def help(self, event):
        """Makes a pause by stopping the timer and shows the help menu"""
        if self.gameIsOn:
            self.gameIsOn = False
            self.board.drawHelpMenu()
        else: self.resume(event)

    def resume(self, event):
        """Resumes the game by calling the timerFired method"""
        self.gameIsOn = True
        self.timerFired()

    def restart(self, event):
        """Restart the game by returning to the initial state"""
        self.gameIsOn = True
        self.resetBoard()
        self.board.drawButtons()
        self.bindEvents()
        self.startGame()

    def resetBoard(self):
        """Resets the board to the initial state"""
        self.board.destroy()
        self.board = Board(parent = self.frame)
        self.board.pack()

    def removeFullRows(self):
        """Removes full rows and updates score and level"""
        fullRowCount = 0
        sm, sld = Rules.scoringMechanism, Rules.scoringLevelDependence
        for i in xrange(len(self.board.colorContent)):
            if self.board.emptyColor not in self.board.colorContent[i]:
                fullRowCount += 1
                self.board.colorContent[0] = \
                        [self.board.emptyColor] * Rules.cols
                for k in xrange(i, 0, -1):
                    self.board.colorContent[k] = \
                            copy.copy(self.board.colorContent[k - 1])
        if fullRowCount != 0:
            if sm == "Base-4 exponential": s = 4 ** (fullRowCount - 1)
            elif sm == "Quadratic": s = fullRowCount ** 2
            if sld == 1: s *= (self.board.level + 1)
            self.board.score += s
        self.board.fallingPiece = None
        self.redrawAll()

    def toMainMenu(self, event):
        """Navigates back to the Main controller"""
        self.gameIsOn = False
        self.resetBoard()
        self.isActive = False
        self.frame.quit()
        self.frame.destroy()
        self.root.unbind("<Button-1>")
        self.root.unbind("<KeyPress>")
        self.gameIsOn = True

class MainMenu(Canvas):
    """The view that renders the Main controller"""
    def __init__(self, parent = None):
        rows, cols = Rules.defaultRows, Rules.defaultCols
        cellSize, marginWidth = Rules.defaultCellSize, Rules.marginWidth
        self.width = cols * cellSize + 2 * marginWidth
        self.height = rows * cellSize + 4 * marginWidth
        Canvas.__init__(self, parent, width = self.width, height = self.height)
        self.background, self.lineColor = "gray", "black"
        self.lineWidth, self.buttonFont = 3, ("Copperplate", "16", "bold")

    def drawMenu(self):
        self.create_rectangle(0, 0, self.width, self.height, \
                width = 0, fill = self.background)
        self.drawTitle()
        self.drawGameButton()
        self.drawPieceEditorButton()
        self.drawSettingsButton()

    def drawTitle(self):
        x, y = self.width * 0.5, self.height * 0.175
        self.create_text(x, y, text = "T e t r i s", font = ("Copperplate", 48))

    def drawGameButton(self):
        x, y = self.width * 0.5, self.height * 0.35
        self.gameButton = self.createButtonRect(x, y)
        self.gameButtonText = self.createButtonText(x, y, "START GAME")

    def drawPieceEditorButton(self):
        x, y = self.width * 0.5, self.height * 0.5
        self.pieceEditorButton = self.createButtonRect(x, y)
        self.pieceEditorButtonText = self.createButtonText(x, y, \
                "PIECE EDITOR")

    def drawSettingsButton(self):
        x, y = self.width * 0.5, self.height * 0.65
        self.settingsButton = self.createButtonRect(x, y)
        self.settingsButtonText = self.createButtonText(x, y, "SETTINGS")

    def createButtonRect(self, x, y):
        return self.create_rectangle(x - 75, y - 20, \
                x + 75, y + 20, fill = self.background, \
                outline = self.lineColor, width = self.lineWidth)

    def createButtonText(self, x, y, text):
        return self.create_text(x, y, text = text, font = self.buttonFont)

class PiecesMenu(Canvas):
    """The view that renders the Piece Editor controller's basic menu"""
    def __init__(self, parent = None):
        self.headerHeight = 40
        self.unitHeight, self.units = 80, len(Piece.knownShapes)
        self.displayUnits, self.unitWidth = 7, 400
        self.backgroundColor, self.lineColor = "white", "black"
        self.pieceCellSize = self.unitHeight / 4.
        Canvas.__init__(self, parent, background = self.backgroundColor, \
            height = self.headerHeight + self.unitHeight * self.displayUnits, \
            width = self.unitWidth, scrollregion = (0, 0, self.unitWidth, \
            self.headerHeight + self.unitHeight * self.units))
        self.lineWidth = self.pieceCellSize / 15

    def drawMenu(self):
        self.drawHeader()
        unitRow = 0
        self.deleteButtons = []
        for name in Piece.standardPieces:
            self.drawUnit(name, unitRow)
            unitRow += 1
        for name in set(Piece.knownShapes) - set(Piece.standardPieces):
            self.drawUnit(name, unitRow)
            unitRow += 1

    def drawHeader(self):
        hh = self.headerHeight
        x1, y1 = self.unitHeight * 0.25, hh * 0.5
        x2, y2 = self.unitWidth - self.unitHeight * 0.25, hh * 0.5
        self.create_text(x1 - 10, y1, text = "<")
        self.mainMenuButton = self.create_text(x1, y1, \
                text = "Main Menu", anchor = tk.W)
        self.addPieceButton = self.create_text(x2, y2, \
                text = "+", font = ("Helvetica", 26, "bold"), anchor = tk.E)

    def drawUnit(self, name, row):
        hh = self.headerHeight
        self.create_line(0, hh + row * self.unitHeight, self.unitWidth, \
                hh + row * self.unitHeight, width = self.lineWidth)
        self.create_line(0, hh + (row + 1) * self.unitHeight, self.unitWidth, \
                hh + (row + 1) * self.unitHeight, width = self.lineWidth)
        shape = Piece.knownShapes[name]
        color = Piece.knownColors[name]
        size = self.pieceCellSize
        xStart = 0.25 * self.unitHeight
        yStart = hh + (row + 0.5) * self.unitHeight - len(shape) * size * 0.5
        for i in xrange(len(shape)):
            for j in xrange(len(shape[0])):
                if shape[i][j]:
                    self.create_rectangle(xStart + j * size, yStart + i * size,\
                            xStart + (j + 1) * size, yStart + (i + 1) * size, \
                            fill = color, width = self.lineWidth)
        self.deleteButtons.append(\
            self.create_text(self.unitWidth - 0.25 * self.unitHeight, \
                hh + (row + 0.5) * self.unitHeight, anchor = tk.E, text = "×", \
                    font = ("Helvetica", 20)))

class AddPieceMenu(Canvas):
    """The view that renders the piece creation interface"""
    def __init__(self, parent = None):
        self.cellSize, self.rows, self.cols, self.marginWidth = 60, 2, 4, 90
        self.width = self.cellSize * self.cols + 2 * self.marginWidth
        self.height = self.cellSize * self.rows + 2 * self.marginWidth
        self.shape = [[False for j in xrange(self.cols)] \
                for i in xrange(self.rows)]
        self.cells = list()
        self.emptyColor = "blue"
        self.color = "red"
        self.font = ("Helvetica", 16)
        Canvas.__init__(self, parent, height = self.height, width = self.width)

    @property
    def interpretedShape(self):
        """Parse the user-created shape to the right format"""
        result = copy.deepcopy(self.shape)
        for i in xrange(len(result) - 1, -1, -1):
            if True not in result[i]: result.pop(i)
        for j in xrange(len(result[0]) - 1, -1, -1):
            if True not in [result[i][j] for i in xrange(len(result))]:
                for i in xrange(len(result)): result[i].pop(j)
        return result

    @property
    def shapeIsRecommended(self):
        """Returns whether the user-created shape is recommended"""
        if sum([row.count(True) for row in self.shape]) < 3: return False
        shape = self.interpretedShape
        for i in xrange(len(shape)):
            for j in xrange(len(shape[0]) - 1):
                if shape[i][j] and not (shape[i - 1][j] or shape[i][j + 1]):
                    return False
        for name in Piece.knownShapes:
            if Piece.knownShapes[name] == shape or \
               Piece.knownShapes[name] == list(reversed(shape)):
                return False
        return True

    def drawMenu(self):
        self.drawCells()
        self.drawBackButton()
        self.drawSaveButton()
        self.drawInstructions()

    def drawCells(self):
        size = self.cellSize
        xStart, yStart = self.marginWidth, self.marginWidth
        for i in xrange(self.rows):
            subCells = list()
            for j in xrange(self.cols):
                subCells.append(self.create_rectangle(\
                        xStart + j * size, yStart + i * size, \
                        xStart + (j + 1) * size, yStart + (i + 1) * size, \
                        fill = self.emptyColor))
            self.cells.append(subCells)
                
    def drawBackButton(self):
        x, y = self.marginWidth * 0.5, self.marginWidth * 0.5
        self.create_text(x - 10, y, text = "<", font = self.font)
        self.backButton = self.create_text(x, y, text = "Back", anchor = tk.W, \
                font = self.font)

    def drawSaveButton(self):
        x, y = self.width - self.marginWidth * 0.5, self.marginWidth * 0.5
        self.saveButton = self.create_text(x, y, text = "Save", anchor = tk.E, \
                font = self.font)
    
    def drawInstructions(self):
        x, y = self.width * 0.5, self.marginWidth + 2 * self.cellSize + 30
        self.instruction = self.create_text(x, y, text = \
"""Click on the blocks to create piece. Right-click to choose color.""", \
font = ("Helvetica", 12))
        self.warnings = self.create_text(x, y + 30, text = \
"""The piece should be continuous, has at least 3 cells, and differ from \
existing pieces.""", font = ("Helvetica", 10))
        
class Board(Canvas):
    """The view that renders the game"""
    def __init__(self, parent = None):
        rows, cols, cellSize = Rules.rows, Rules.cols, Rules.cellSize()
        marginWidth = Rules.marginWidth
        self.masterWidth = cols * cellSize + 2 * marginWidth
        self.masterHeight = rows * cellSize + 4 * marginWidth
        Canvas.__init__(self, parent, \
                width = self.masterWidth, height = self.masterHeight)
        self.background, self.lineColor, self.score = "orange", "black", 0
        self.lineWidth, self.emptyColor = cellSize / 15, "blue"
        self.colorContent = [[self.emptyColor for j in xrange(cols)] \
                for i in xrange(rows)]
        self.fallingPiece, self.nextPiece = None, None
        self.buttonColor = "gray"

    @property
    def level(self):
        """Returns the user's current level"""
        return 0 if self.score / 5 == 0 else int(math.log(self.score / 5., 2))
    
    def drawGame(self):
        for tag in self.find_all():
            if tag != self.pauseButton and tag != self.pauseButtonText\
               and tag != self.helpButton and tag != self.helpButtonText:
                self.delete(tag)
        self.create_rectangle(0, 0, self.masterWidth, \
                self.masterHeight, width = 0, \
                fill = self.background)
        self.drawBoard()
        self.drawFallingPiece()
        self.drawNextPiece()
        self.drawScore()
        self.drawLevel()
        self.tag_raise(self.pauseButton)
        self.tag_raise(self.pauseButtonText)
        self.tag_raise(self.helpButton)
        self.tag_raise(self.helpButtonText)
        
    def drawBoard(self):
        for i in xrange(len(self.colorContent)):
            for j in xrange(len(self.colorContent[0])):
                self.create_rectangle(Rules.marginWidth + j * Rules.cellSize(),\
                        Rules.marginWidth * 3 + i * Rules.cellSize(), \
                        Rules.marginWidth + (j + 1) * Rules.cellSize(), \
                        Rules.marginWidth * 3 + (i + 1) * Rules.cellSize(), \
                        outline = self.lineColor, \
                        width = self.lineWidth, \
                        fill = self.colorContent[i][j])

                    
    def drawFallingPiece(self):
        fallingPieceCells = self.fallingPieceCells
        startX = Rules.marginWidth
        startY = Rules.marginWidth * 3
        cellSize = Rules.cellSize()
        for cell in fallingPieceCells:
            self.create_rectangle(startX + cell[1] * cellSize, \
                    startY + cell[0] * cellSize, \
                    startX + (cell[1] + 1) * cellSize, \
                    startY + (cell[0] + 1) * cellSize, \
                    outline = self.lineColor, \
                    width = self.lineWidth, \
                    fill = self.fallingPiece.color)

    def drawNextPiece(self):
        if self.nextPiece == None: return
        shape = self.nextPiece.shape
        scale = 0.75 * Rules.marginWidth / Rules.cellSize()
        scaledLineWidth = self.lineWidth * scale
        scaledCellSize = Rules.cellSize() * scale
        pieceHeight = len(shape) * scaledCellSize
        pieceWidth = len(shape[0]) * scaledCellSize
        startX = Rules.marginWidth + Rules.cols / 2. \
                 * Rules.cellSize() - 0.5 * pieceWidth
        startY = 1.5 * Rules.marginWidth - 0.5 * pieceHeight
        for i in xrange(len(shape)):
            for j in xrange(len(shape[0])):
                if shape[i][j] == True:
                    self.create_rectangle(\
                        startX + j * scaledCellSize, \
                        startY + i * scaledCellSize,\
                        startX + (j + 1) * scaledCellSize, \
                        startY + (i + 1) * scaledCellSize, \
                        outline = self.lineColor, width = scaledLineWidth, \
                        fill = self.nextPiece.color)


    def drawScore(self):
        self.create_text(Rules.marginWidth, Rules.marginWidth * 0.75, \
                anchor = tk.NW, text = "Score: {0}".format(self.score))

    def drawLevel(self):
        self.create_text(Rules.marginWidth, Rules.marginWidth * 1.5, \
                anchor = tk.NW, text = "Level: {0}".format(self.level))

    def drawButtons(self):
        buttonRadius = Rules.marginWidth / 2.
        x = Rules.marginWidth + Rules.cols * Rules.cellSize() - buttonRadius
        y = 1.5 * Rules.marginWidth
        self.pauseButton = self.create_rectangle(x - buttonRadius, \
                y - buttonRadius, x + buttonRadius, y + buttonRadius, \
                width = 0, fill = self.buttonColor)
        self.pauseButtonText = self.create_text(x, y, text = "| |", \
                font = ("Helvetica", int(1.5 * buttonRadius)))
        self.helpButton = self.create_rectangle(x - 3 * buttonRadius - 10, \
                y - buttonRadius, x - buttonRadius - 10, y + buttonRadius, \
                width = 0, fill = self.buttonColor)
        self.helpButtonText = self.create_text(x - 2 * buttonRadius - 10, \
                y, text = "?", font = ("Helvetica", int(1.5 * buttonRadius)))

    def drawPauseMenu(self):
        x = Rules.marginWidth + 0.5 * Rules.cols * Rules.cellSize()
        y = 2 * Rules.marginWidth + 0.5 * Rules.rows * Rules.cellSize()
        menuWidth, menuHeight = 175, 262.5
        self.pauseMenu = self.create_rectangle(\
                x - menuWidth * 0.5, y - menuHeight * 0.5, \
                x + menuWidth * 0.5, y + menuHeight * 0.5,\
                outline = self.lineColor, width = self.lineWidth, \
                fill = self.buttonColor)
        self.resumeButton = self.create_text(x, y - menuHeight * 0.25, \
                text = "RESUME", font = ("Helvetica", \
                int(menuWidth / 10.5625 if menuWidth < menuHeight else \
                menuHeight / 10)))
        self.restartButton = self.create_text(x, y, text = "RESTART", \
                font = ("Helvetica", int(menuWidth / 10.5625 \
                if menuWidth < menuHeight else menuHeight / 10)))
        self.mainMenuButton = self.create_text(x, y + menuHeight * 0.25, \
                text = "MAIN MENU", font = ("Helvetica", \
                int(menuWidth / 10.5625 if menuWidth < menuHeight else \
                menuHeight / 10)))

    def drawGameOverMenu(self):
        x = Rules.marginWidth + 0.5 * Rules.cols * Rules.cellSize()
        y = 2 * Rules.marginWidth + 0.5 * Rules.rows * Rules.cellSize()
        menuWidth, menuHeight = 175, 262.5
        self.gameOverMenu = self.create_rectangle(\
                x - menuWidth * 0.5, y - menuHeight * 0.5, \
                x + menuWidth * 0.5, y + menuHeight * 0.5, \
                outline = self.lineColor, width = self.lineWidth, \
                fill = self.buttonColor)
        self.create_text(x, y - menuHeight * 0.5 + menuHeight / 13.125, \
                text = "GAME OVER", font = ("Helvetica", \
                int(menuWidth / 8.75 if menuWidth < menuHeight else \
                menuHeight / 7)), anchor = tk.N, fill = "red")
        self.restartButton = self.create_text(x, y - menuHeight * 0.125, \
                text = "RESTART", font = ("Helvetica", \
                int(menuWidth / 10.5625 if menuWidth < menuHeight else \
                menuHeight / 10)))
        self.mainMenuButton = self.create_text(x, y + menuHeight * 0.125, \
                text = "MAIN MENU", font = ("Helvetica", \
                int(menuWidth / 10.5625 if menuWidth < menuHeight else \
                menuHeight / 10)))

    def drawHelpMenu(self):
        x = Rules.marginWidth + 0.5 * Rules.cols * Rules.cellSize()
        y = 2 * Rules.marginWidth + 0.5 * Rules.rows * Rules.cellSize()
        menuWidth, menuHeight = 300, 250
        self.helpMenu = self.create_rectangle(\
                x - menuWidth * 0.5, y - menuHeight * 0.5, \
                x + menuWidth * 0.5, y + menuHeight * 0.5, \
                outline = self.lineColor, width = self.lineWidth, \
                fill = self.buttonColor)
        self.create_text(x, y, text = \
"""\
- Press "Left"/"Right"/"Down" to move piece.

- Press "Up" to rotate piece.

- Press "Enter" to play hard drop.

- Press "esc" to pause/resume.

- Go to Main Menu > Settings to change
board size, rotating direction of pieces
and scoring mechanism.

- Go to Main Menu > Piece Editor to create
pieces (user-created pieces can be deleted).\
""")        

    @property
    def fallingPieceCells(self):
        """Returns the indexes of cells occupied by the falling piece"""
        fallingPieceCells = []
        if self.fallingPiece == None: return fallingPieceCells
        shape = self.fallingPiece.shape
        position = self.fallingPiece.position
        for i in xrange(len(shape)):
            for j in xrange(len(shape[0])):
                if shape[i][j] == True:
                    fallingPieceCells.append((i + position[0], j + position[1]))
        return fallingPieceCells

    @property
    def isLegal(self):
        """Returns whether the falling piece does not overlap
           with pieces already put on the board"""
        fallingPieceCells = self.fallingPieceCells
        for cell in fallingPieceCells:
            if cell[0] >= Rules.rows or cell[1] < 0 or cell[1] >= Rules.cols:
                return False
            if self.colorContent[cell[0]][cell[1]] != self.emptyColor:
                return False
        return True
        
class Piece:
    """Class that stores properties of piece instants and
       manages the piece database"""
    knownShapes = dict()
    knownColors = dict()
    knownShortcuts = dict()
    standardPieces = \
        ["iPiece", "jPiece", "lPiece", "oPiece", "sPiece", "tPiece", "zPiece"]

    def __str__(self):
        return """Piece name: {0};
Piece color: {1};
Piece position: {2};
Piece shape: {3}.""".format(self.name, self.color, self.position, self.shape)

    def __init__(self, name, boardCols):
        self.name = name
        self._shape = Piece.knownShapes[name]
        self.color = Piece.knownColors[name]
        self.orientation = 0
        
        self.position = [0, boardCols / 2 - len(self._shape[0]) / 2]

    @staticmethod
    def learnPiece(name, shape, color):
        """Add a piece to the piece database"""
        Piece.knownShapes[name] = shape
        Piece.knownColors[name] = color

    @staticmethod
    def forgetPiece(name):
        """Removes a piece from the piece database"""
        Piece.knownShapes.pop(name)
        Piece.knownColors.pop(name)

    @property
    def shape(self):
        """Returns the piece shape under global coordinate
           given the piece's orientation
        """
        if self.orientation == 0:
            return self._shape
        elif self.orientation == 1:
            return self.getShapeCase1()
        elif self.orientation == 2:
            return self.getShapeCase2()
        elif self.orientation == 3:
            return self.getShapeCase3()
        else:
            return self._shape

    def getShapeCase1(self):
        """Returns the piece shape under global coordinate when the piece
           is 90 degrees clockwise from the initial state
        """
        result = []
        for j in xrange(len(self._shape[0])):
            subResult = []
            for i in xrange(len(self._shape) - 1, -1, -1):
                subResult.append(self._shape[i][j])
            result.append(subResult)
        return result

    def getShapeCase2(self):
        """Returns the piece shape under global coordinate when the piece
           is 180 degrees clockwise from the initial state
        """
        result = []
        for i in xrange(len(self._shape) - 1, -1, -1):
            subResult = []
            for j in xrange(len(self._shape[0]) - 1, -1, -1):
                subResult.append(self._shape[i][j])
            result.append(subResult)
        return result

    def getShapeCase3(self):
        """Returns the piece shape under global coordinate when the piece
           is 90 degrees counterclockwise from the initial state
        """
        result = []
        for j in xrange(len(self._shape[0]) - 1, -1, -1):
            subResult = []
            for i in xrange(len(self._shape)):
                subResult.append(self._shape[i][j])
            result.append(subResult)
        return result

class Test:

    timesOfMovePiece = 0
    
    @staticmethod
    def testlearnPiece(name, board):
        print "--------------------testing learnPiece"
        print "sPiece"
        sPiece = Piece("sPiece", board.cols)
        print "\t", sPiece.shape, sPiece.color
        print name
        specifiedPiece = Piece(name, board.cols)
        print "\t", specifiedPiece.shape, specifiedPiece.color
        print "--------------------test end\n"

    @staticmethod
    def testDrawBoard(application, rows, cols):
        print "--------------------testing drawBoard"
        application.board.colorContent[0][0] = "red"
        application.board.colorContent[0][cols - 1] = "white"
        application.board.colorContent[rows - 1][0] = "green"
        application.board.colorContent[rows - 1][cols - 1] = "gray"
        print "--------------------test end\n"

    @staticmethod
    def logProperty(message, aProperty):
        print "--------------------logging property"
        print message
        print aProperty
        print "--------------------test end\n"

    @staticmethod
    def testNewFallingPiece(board):
        print "--------------------testing newFallingPiece"
        print "New piece instantiated."
        print board.fallingPiece
        print board.fallingPieceCells
        print "--------------------test end\n"

    @staticmethod
    def testDrawFallingPiece(application):
        print "--------------------testing drawFallingPiece"
        application.newFallingPiece()
        application.redrawAll()
        print "--------------------test end\n"


# The run method in Application has no parameter.
# To change the board size, go to Main Menu > Settings.
Application().run()
