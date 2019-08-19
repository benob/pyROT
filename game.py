# pyROT: brython+rot.js to make roguelikes with python in the browser.
# example based on http://www.roguebasin.roguelikedevelopment.org/index.php?title=Rot.js_tutorial

from browser import window, document
ROT = window.ROT


class Game:
    def __init__(self):
        # we use a retro ascii tileset instead of the default monospace font
        tileSet = document.createElement('img')
        tileSet.src = 'ascii_8x8.png'

        options = {
            'layout': 'tile-gl' if ROT.Display.TileGL.isSupported() else 'tile',
            'bg': 'black',
            'tileWidth': 8,
            'tileHeight': 8,
            'tileSet': tileSet,
            'tileMap': {chr(i): [8 * (i % 16), 8 * (i // 16)] for i in range(256)},
            'width': 80,
            'height': 50,
            'tileColorize': True,
        }

        # init display and add it to the page
        self.display = ROT.Display.new(options)
        document.body.appendChild(self.display.getContainer())

        # constructor called when tileset is loaded
        def ready(*args):
            self.messages = Messages()
            self.generateMap()
            scheduler = ROT.Scheduler.Simple.new()
            scheduler.add(window.wrap_actor(self.pedro), True)
            scheduler.add(window.wrap_actor(self.player), True)
            self.engine = ROT.Engine.new(scheduler)
            alert('Can you find the ananas before Pedro catches you?')
            self.engine.start()

        tileSet.onload = ready

    def generateMap(self):
        # dungeon map is a dictionary indexed by (x, y) tuples of tile coordinates
        self.map = {}

        freeCells = []
        def digCallback(x, y, value):
            if value:
                return False
            key = x, y
            self.map[key] = '.'
            freeCells.append(key)

        digger = ROT.Map.Digger.new()
        digger.create(digCallback)

        self.generateBoxes(freeCells)
        self.drawWholeMap()

        self.player = self.createBeing(Player, freeCells)
        self.pedro = self.createBeing(Pedro, freeCells)

    def drawWholeMap(self):
        for (x, y), value in self.map.items():
            self.display.draw(x, y, value)
    
    def generateBoxes(self, freeCells):
        # add 10 boxes, first one is the ananas
        for i in range(10):
            index = int(ROT.RNG.getUniform() * len(freeCells))
            key = freeCells.pop(index)
            self.map[key] = '*'
            if i == 0:
                self.ananas = key

    def createBeing(self, what, freeCells):
        index = int(ROT.RNG.getUniform() * len(freeCells))
        x, y = freeCells.pop(index)
        return what(x, y)


class Player:
    def __init__(self, x, y):
        # wrap object so that handleEvent() can be called from js event listener 
        self.listener = window.wrap_event_handler(self)
        self.x = x
        self.y = y
        self.draw()

    def draw(self):
        game.display.draw(self.x, self.y, '@', '#ff0')

    def act(self):
        game.engine.lock()
        window.addEventListener('keydown', self.listener)

    def handleEvent(self, e):
        keyMap = {
                38: 0,
                33: 1,
                39: 2,
                34: 3,
                40: 4,
                35: 5,
                37: 6,
                36: 7
                }
     
        # get id of pressed key from js event
        code = e['keyCode']

        if code in [13, 32]:
            self.checkBox()
            e.preventDefault() # prevent browser from handling key
            return

        if code not in keyMap:
            return

        e.preventDefault() # prevent browser from handling key
     
        diff = ROT.DIRS[8][keyMap[code]]
        newX = self.x + diff[0]
        newY = self.y + diff[1]
     
        if (newX, newY) not in game.map:
            return

        game.display.draw(self.x, self.y, game.map[(self.x, self.y)])
        self.x = newX
        self.y = newY
        self.draw()
        window.removeEventListener('keydown', self.listener)
        game.engine.unlock()

    def checkBox(self):
        key = self.x, self.y
        if game.map[key] != '*':
            alert('There is no box here!')
        elif key == game.ananas:
            alert('Hooray! You found an ananas and won this game.')
            game.engine.lock();
            window.removeEventListener('keydown', self.listener)
        else:
            alert('This box is empty :-(')

class Pedro:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.draw()
 
    def draw(self):
        game.display.draw(self.x, self.y, "P", "red")

    def act(self):
        x = game.player.x
        y = game.player.y
        def passableCallback(x, y):
            return (x, y) in game.map
        
        astar = ROT.Path.AStar.new(x, y, passableCallback, {'topology': 4})
     
        path = []
        def pathCallback(x, y):
            path.append((x, y))
        
        astar.compute(self.x, self.y, pathCallback)

        path.pop(0) # remove Pedro's position
        if len(path) == 1:
            game.engine.lock()
            alert("Game over - you were captured by Pedro!")
        elif len(path) > 0:
            x, y = path[0]
            game.display.draw(self.x, self.y, game.map[(self.x, self.y)])
            self.x = x
            self.y = y
            self.draw()


class Messages:
    def __init__(self, shown=6):
        self.shown = shown
        self.lines = []
        self.draw()

    def add(self, line):
        self.erase()
        self.lines.append(line)
        self.draw()

    def erase(self):
        for y in range(self.shown):
            for x in range(80):
                game.display.draw(x, 50 - self.shown + y, ' ')

    def draw(self):
        for y, line in enumerate(self.lines[-self.shown:]):
            game.display.drawText(0, 50 - self.shown + y, line)

    def act(self):
        self.draw()
        

def alert(*args):
    game.messages.add(' '.join([str(x) for x in args]))

game = Game()
