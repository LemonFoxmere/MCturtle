from mcpi.minecraft import Minecraft
from math import *
import time
import enum

# ----enums----


class direction(enum.Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    KEEP_SAME = 4


class heading(enum.Enum):
    DOWN = 0
    UP = 1
    NORTH = 2
    SOUTH = 3
    WEST = 4
    EAST = 5


class MCTurtle:

    def __init__(self, mc, pos):
        self.mc = mc

        self.lifted = False
        self.yawDirections = [5, 3, 4, 2]  # list of turn faces
        self.yaw = 0  # current pointer of yaw
        # v This you have to multiply by the current yaw direction v
        self.pitch = 1  # 1 = neural; 1/yaw = up; 0 = down
        self.rotation = self.yawDirections[self.yaw] * self.pitch
        self.strokeBlock = 0
        self.isDown = True
        self.x = 0
        self.y = 0
        self.z = 0
        self.homeX = 0
        self.homeY = 0
        self.HomeZ = 0
        self.speed = 0.25
        self.incomeStorage = None
        self.trailStorage = None

        self.createPen(pos.x, pos.y, pos.z)

    def headingToString(self, heading):
        if heading == 0 or heading == heading.UP:
            return "Facing Down"
        if heading == 1 or heading == heading.DOWN:
            return "Facing Up"
        if heading == 2 or heading == heading.NORTH:
            return "Facing North"
        if heading == 3 or heading == heading.SOUTH:
            return "Facing South"
        if heading == 4 or heading == heading.WEST:
            return "Facing West"
        if heading == 5 or heading == heading.EAST:
            return "Facing East"

    def createPen(self, cx, cy, cz):
        # make a pen facing east
        self.x = int(cx)
        self.y = int(cy)
        self.z = int(cz)
        self.rotation = 5
        self.trailStorage = self.mc.getBlockWithData(cx, cy, cz)
        self.incomeStorage = self.__get_block_on_side(self.rotation)
        self.homeX = self.x
        self.homeY = self.y
        self.homeZ = self.z
        self.mc.setBlock(cx, cy, cz, 33, 5)

    def updatePos(self, ux, uy, uz):
        self.x = ux
        self.y = uy
        self.z = uz

    def updateStroke(self, block):
        self.strokeBlock = block

    def __cycle_yaw(self, direction):
        if direction == direction.RIGHT:
            # cycle it to the RIGHT
            if self.yaw == 3:  # reached end, reset
                self.yaw = 0
            else:
                self.yaw += 1
        elif direction == direction.LEFT:
            # cycle to left
            if self.yaw == 0:  # reached end, reset
                self.yaw = 3
            else:
                self.yaw -= 1
        elif direction == direction.KEEP_SAME:
            pass
        else:
            print("error: illegal direction argument " +
                  direction + ". Direction can only be left/right")

    def __update_rotation(self, yawDirection, pitchDirection):
        # based on the yaw*pitch formula, update the master rotation value

        # first, we update the yaw
        self.__cycle_yaw(yawDirection)

        # second, we update the pitch
        if self.pitch == 1:  # normal state
            if pitchDirection == direction.DOWN:  # if user wants to face down
                self.pitch = 0
            elif pitchDirection == direction.UP:  # if user wants to face up
                self.pitch = 1/self.yawDirections[self.yaw]
            elif pitchDirection == direction.KEEP_SAME:
                pass
            else:
                print("illegal pitch direction statement. Pitch can only be UP or DOWN")
        elif self.pitch == 0:  # if it is currently facing down
            if pitchDirection == direction.UP:  # then make it face up
                self.pitch = 1
            # these won't be able to do anything
            elif pitchDirection == direction.DOWN or pitchDirection == direction.KEEP_SAME:
                pass
            else:
                print("illegal pitch direction statement. Pitch can only be UP or DOWN")
        else:  # then it must be facing up, as it its not down or neutral
            if pitchDirection == direction.DOWN:
                self.pitch = 1
            elif pitchDirection == direction.UP or pitchDirection == direction.KEEP_SAME:  # these won't do anything either
                pass
            else:
                print("illegal pitch direction statement. Pitch can only be UP or DOWN")

        # third, we update the master rotational value
        self.rotation = self.yawDirections[self.yaw] * self.pitch
        # end of rotation update

    def __getBlockWithData(self, dx, dy, dz):
        return self.mc.getBlockWithData(self.x + dx, self.y + dy, self.z + dz)

    def __get_block_on_side(self, direction, onBack=False):
        # onBack's function serves to reverse the direction of where it is getting the block from.
        # Ex: direction = UP, onBack = True --> blockData(DOWN)

        if direction == 5 or direction == heading.EAST:
            if not onBack:
                return self.__getBlockWithData(1, 0, 0)
            else:
                return self.__getBlockWithData(-1, 0, 0)
        if direction == 4 or direction == heading.WEST:
            if not onBack:
                return self.__getBlockWithData(-1, 0, 0)
            else:
                return self.__getBlockWithData(1, 0, 0)
        if direction == 3 or direction == heading.SOUTH:
            if not onBack:
                return self.__getBlockWithData(0, 0, 1)
            else:
                return self.__getBlockWithData(0, 0, -1)
        if direction == 2 or direction == heading.NORTH:
            if not onBack:
                return self.__getBlockWithData(0, 0, -1)
            else:
                return self.__getBlockWithData(0, 0, 1)
        if direction == 1 or direction == heading.UP:
            if not onBack:
                return self.__getBlockWithData(0, 1, 0)
            else:
                return self.__getBlockWithData(0, -1, 0)
        if direction == 0 or direction == heading.DOWN:
            if not onBack:
                return self.__getBlockWithData(0, -1, 0)
            else:
                return self.__getBlockWithData(0, 1, 0)

    def home(self, offsetX=0, offsetY=0, offsetZ=0):
        self.mc.setBlock(self.homeX + offsetX, self.homeY +
                         offsetY, self.homeZ + offsetZ, 33, self.rotation)
        self.mc.setBlock(self.x, self.y, self.z, self.strokeBlock)
        self.updatePos(self.homeX + offsetX, self.homeY +
                       offsetY, self.homeZ + offsetZ)

    def __setTurtle(self, dx, dy, dz):
        self.mc.setBlock(self.x + dx, self.y + dy,
                         self.z + dz, 33, self.rotation)
        self.updatePos(dx, dy, dz)

    def __setBlock(self, dx, dy, dz, id):
        self.mc.setBlock(self.x + dx, self.y + dy, self.z + dz, id)

    def forward(self, amount):
        self.incomeStorage = self.__get_block_on_side(self.rotation)
        for i in range(0, amount):
            # move the piston in the specified rotation
            if not self.isDown:
                # store the block data infront into "incomeStorage"
                # move forward and place block in "trailStorage"
                # transfer the block data in "incomeStorage" into "trailStorage"
                self.updateStroke(self.trailStorage)

            self.__setBlock(0, 0, 0, self.strokeBlock)

            if self.rotation == 0:
                # down
                self.__setTurtle(0, -1, 0)
            if self.rotation == 1:
                # up
                self.__setTurtle(0, 1, 0)
            if self.rotation == 2:
                # north
                self.__setTurtle(0, 0, -1)
            if self.rotation == 3:
                # south
                self.__setTurtle(0, 0, 1)
            if self.rotation == 4:
                # west
                self.__setTurtle(-1, 0, 0)
            if self.rotation == 5:
                # east
                self.__setTurtle(1, 0, 0)

            time.sleep(self.speed)
            self.trailStorage = self.incomeStorage
            self.incomeStorage = self.__get_block_on_side(self.rotation)

    def fd(self, amount):
        self.forward(amount)

    def backward(self, amount):
        self.incomeStorage = self.__get_block_on_side(self.rotation, True)
        for i in range(0, amount):
            if not self.isDown:
                # store the block data infront into "incomeStorage"
                # move forward and place block in "trailStorage"
                # transfer the block data in "incomeStorage" into "trailStorage"
                self.updateStroke(self.trailStorage)
            # move the piston in the specified rotation

            self.__setBlock(0, 0, 0, self.strokeBlock)

            if self.rotation == 0:
                # down
                self.__setTurtle(0, 1, 0)
            if self.rotation == 1:
                # up
                self.__setTurtle(0, -1, 0)
            if self.rotation == 2:
                # north
                self.__setTurtle(0, 0, 1)
            if self.rotation == 3:
                # south
                self.__setTurtle(0, 0, -1)
            if self.rotation == 4:
                # west
                self.__setTurtle(1, 0, 0)
            if self.rotation == 5:
                # east
                self.__setTurtle(-1, 0, 0)
            time.sleep(self.speed)
            self.trailStorage = self.incomeStorage
            self.incomeStorage = self.__get_block_on_side(self.rotation, True)

    def bk(self, amount):
        self.backward(amount)

    def setx(self, newX):
        if newX > int(self.x):
            self.incomeStorage = self.__get_block_on_side(heading.EAST)
            for i in range(int(abs(newX-self.x))):
                if not self.isDown:
                    self.updateStroke(self.trailStorage)
                self.mc.setBlock(0, 0, 0, self.strokeBlock)
                self.__setTurtle(1, 0, 0)
                self.trailStorage = self.incomeStorage
                self.incomeStorage = self.__get_block_on_side(heading.EAST)
                time.sleep(self.speed)
        else:
            self.incomeStorage = self.__get_block_on_side(heading.EAST, True)
            for i in range(int(abs(newX-self.x))):
                if not self.isDown:
                    self.updateStroke(self.trailStorage)
                self.mc.setBlock(0, 0, 0, self.strokeBlock)
                self.__setTurtle(-1, 0, 0)
                self.trailStorage = self.incomeStorage
                self.incomeStorage = self.__get_block_on_side(
                    heading.EAST, True)
                time.sleep(self.speed)

    def sety(self, newY):
        if newY > int(self.y):
            self.incomeStorage = self.__get_block_on_side(heading.UP)
            for i in range(int(abs(newY-self.y))):
                if not self.isDown:
                    self.updateStroke(self.trailStorage)
                self.mc.setBlock(0, 0, 0, self.strokeBlock)
                self.__setTurtle(0, 1, 0)
                self.trailStorage = self.incomeStorage
                self.incomeStorage = self.__get_block_on_side(heading.UP)
                time.sleep(self.speed)
        else:
            self.incomeStorage = self.__get_block_on_side(heading.UP, True)
            for i in range(int(abs(newY-self.y))):
                if not self.isDown:
                    self.updateStroke(self.trailStorage)
                self.mc.setBlock(0, 0, 0, self.strokeBlock)
                self.__setTurtle(0, 1, 0)
                self.trailStorage = self.incomeStorage
                self.incomeStorage = self.__get_block_on_side(heading.UP, True)
                time.sleep(self.speed)

    def setz(self, newZ):
        if newZ > int(self.z):
            self.incomeStorage = self.__get_block_on_side(heading.SOUTH)
            for i in range(int(abs(newZ-self.z))):
                if not self.isDown:
                    self.updateStroke(self.trailStorage)
                self.mc.setBlock(0, 0, 0, self.strokeBlock)
                self.__setTurtle(0, 0, 1)
                self.trailStorage = self.incomeStorage
                self.incomeStorage = self.__get_block_on_side(heading.SOUTH)
                time.sleep(self.speed)
        else:
            self.incomeStorage = self.__get_block_on_side(heading.SOUTH, True)
            for i in range(int(abs(newZ-self.z))):
                if not self.isDown:
                    self.updateStroke(self.trailStorage)
                self.mc.setBlock(0, 0, 0, self.strokeBlock)
                self.__setTurtle(0, 0, -1)
                self.trailStorage = self.incomeStorage
                self.incomeStorage = self.__get_block_on_side(
                    heading.SOUTH, True)
                time.sleep(self.speed)

    def goto(self, newX, newY, newZ):
        # reference: https://en.wikipedia.org/wiki/Line_drawing_algorithm
        staticx = self.x
        staticy = self.y
        staticz = self.z

        deltax = newX - self.x
        deltay = newY - self.y
        deltaz = newZ - self.z

        for i in range(1, abs(newX - self.x)+1):
            if (newX-self.x) > 0:
                self.setx(staticx+i)
                self.sety(staticy+round(i*(deltay/deltax)))
                self.setz(staticz+round(i*(deltaz/deltax)))
            else:
                self.setx(staticx-i)
                self.sety(staticy-round(i*(deltay/deltax)))
                self.setz(staticz-round(i*(deltaz/deltax)))

    def setSpeed(self, newSpeed):
        # x blocks per second
        self.speed = 1/newSpeed

    def __rotate_turtle(self):
        mc.setBlock(x, y, z, 33, self.rotation)

    def turn(self, direction):  # turn based on a circle of rotation
        if direction == direction.RIGHT or direction == direction.LEFT:
            self.__update_rotation(direction, direction.KEEP_SAME)
            self.__rotate_turtle()
        elif direction == direction.UP or direction == direction.DOWN:
            self.__update_rotation(direction.KEEP_SAME, direction)
            self.__rotate_turtle()
        elif direction == direction.KEEP_SAME:
            pass
        else:
            print(
                "illegal turn direction argument. Direction can only be LEFT, RIGHT, UP, or DOWN")

    def xcor(self):
        return self.x

    def ycor(self):
        return self.y

    def zcor(self):
        return self.z

    def isDown(self):
        return self.isDown

    def penUp(self):
        self.isDown = False

    def penDown(self):
        self.isDown = True

    def facing(self):
        return self.headingToString(self.rotation)

    def position(self):
        return (self.x, self.y, self.z)

    def setHeading(self, direction):
        if isinstance(direction, self.heading):
            self.rotation = direction.value()
            return
        if type(direction) != int:
            print('Error: direcction can only be integer or a heading enum. You passed in a ', type(
                direction), '. This step will not run due to the error.')
            return TypeError
        self.rotation = direction
