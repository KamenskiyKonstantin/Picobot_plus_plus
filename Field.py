import array

from requests.utils import select_proxy

from CommandParser import Parser
class Bot:
    def __init__(self):
        self.state1 = '0'
        self.state2 = '0'
        self.last_dir = 'X'
        self.position = [1, 1]


class Field:
    def __init__(self):
        self.field = \
            [['0' for _ in range(51)]]+\
            [['0']+ ['1' for _ in range(49)] + ['0'] for _ in range(49)]+ \
            [['0' for _ in range(51)]]

        self.bot = Bot()
        with open('empty.txt', 'r') as f: #prototype
            self.parser = Parser(f.read())

    def copy(self):
        result = Field()
        result.field = [[el for el in l] for l in self.field]
        result.bot = Bot()
        result.bot.position = [self.bot.position[0], self.bot.position[1]]
        result.bot.state1 = self.bot.state1
        result.bot.state2 = self.bot.state2
        result.bot.last_dir = self.bot.last_dir
        result.parser = self.parser
        return result

    def tick(self):
        state = self.generate_state()
        instructions = self.parser.match(state)
        if len(instructions) == 0:
            raise RuntimeError(f"Error: no matching instruction for state: {state}")
        elif len(instructions) > 1:
            print(f"WARN: Error: conflict of instructions for state: {state}. Conflicting instructions: {instructions}")

        instr = instructions[0]
        # print(state, 'executing:', instr)
        j, i = self.bot.position[0], self.bot.position[1]
        self.bot.state1, self.bot.state2 = instr[6] if instr[6]!='*' else self.bot.state1, instr[7] if instr[7]!='*' else self.bot.state2

        build = instr[4]
        if len(build) > 1:
            match build[0]:
                case 'N':
                    self.field[i-1][j] = build[1]
                case 'E':
                    self.field[i][j+1] = build[1]
                case 'W':
                    self.field[i][j-1] = build[1]
                case 'S':
                    self.field[i+1][j] = build[1]

        move = instr[5]
        if move == '*':
            move = state[2] # repeat previous action
        j, i = self.move_pos(move)
        if self.field[i][j] == '1':
            self.bot.position = [j, i]
            if move != 'X':
                self.bot.last_dir = move
        else:
            raise ValueError("Cannot move to that position, blocked")
        if move == build[0] == 'X':
            raise ValueError('Halt instruction detected')



    def generate_state(self):
        state = []
        state.append(self.bot.state1)
        state.append(self.bot.state2)
        state.append(self.bot.last_dir)
        if (self.bot.position[0] <= 0 or self.bot.position[0] >= len(self.field[0])-1 or self.bot.position[1] <= 0 or self.bot.position[1] >= len(self.field)-1 ):
            raise RuntimeError("Error: PBPP out of bounds")
        j, i = self.bot.position[0], self.bot.position[1] # reverse for index access
        state.append(self.field[i-1][j]+self.field[i][j+1]+self.field[i][j-1]+self.field[i+1][j])

        return state

    def move_pos(self, move):
        print(move)
        match move:
            case 'N':
                return self.bot.position[0], self.bot.position[1]-1
            case 'E':
                return self.bot.position[0]+1, self.bot.position[1]
            case 'W':
                return self.bot.position[0]-1, self.bot.position[1]
            case 'S':
                return self.bot.position[0], self.bot.position[1] + 1
            case 'X':
                return (self.bot.position[0], self.bot.position[1])