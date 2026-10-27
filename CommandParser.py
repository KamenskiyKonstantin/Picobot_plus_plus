import re
class Parser:

    def __init__(self, program: str):
        # step 1: split into commands:
        commands = program.split('\n')
        self.commands = []
        for i in range(len(commands)):
            command = commands[i]
            try:
                result = self.parse(command)
                if result:
                    self.commands.append(result)
            except ValueError as e:
                print(e, f'at line num: {i} : {command}')
                raise e

    def parse(self, command: str):
        # step 2:
        if '#' in command:
            command = command[:command.index('#')]
        if command == '':
            return None
        literals = command.split()
        try:
            state1 = literals[0]
        except IndexError:
            raise ValueError("Error: no state 1 value provided")
        try:
            state2 = literals[1]
        except IndexError:
            raise ValueError("Error: no state 2 value provided")

        try:
            last_dir = literals[2]
            dir = ''
            for c in last_dir:
                if c not in 'NEWS*X':
                    raise ValueError(f'Invalid direction literal: {c}')
                if c in dir:
                    raise ValueError(f'Duplicate direction literal: {c}')
                dir+=c
        except IndexError:
            raise ValueError("Error: no last direction value provided")
        try:
            surroundings = literals[3]
            regex = re.compile(r'(?:\[\^?[0-9A-F]*?]|[0-9A-F]|\*){4}')
            if not re.match(regex, surroundings):
                raise ValueError(f'Invalid surroundings state: {surroundings}')
            surroundings = surroundings.replace('*', '[0-9A-F]')
            surr = re.compile(rf'{surroundings}')
        except:
            raise ValueError("Error: no surroundings value provided")
        try:
            build = literals[4]
            regex = re.compile(r'X|([NEWS][0-9A-F])')
            if not re.match(regex, build):
                raise ValueError("Error: invalid build value")
        except IndexError:
            raise ValueError("Error: no build value provided")

        try:
            move = literals[5]
            regex = re.compile(r'[XNEWS*]')
            if not re.match(regex, move):
                raise ValueError('Invalid move value')
        except IndexError:
            raise ValueError("Error: no move value provided")

        try:
            state1res = literals[6]
        except IndexError:
            raise ValueError("Error: no resulting state 1 value provided")

        try:
            state2res = literals[7]
        except IndexError:
            raise ValueError("Error: no resulting state 2 value provided")

        return (state1, state2, dir, surr, build, move, state1res, state2res)

    def match(self, state):
        result = []
        for command in self.commands:
            if (command[0]!='*' and command[0]!=state[0]):
                continue # state1 does not match
            if (command[1]!='*' and command[1]!=state[1]):
                continue # state2 does not match
            if (state[2] not in command[2] and command[2]!='*'):
                continue # direction disallowed
            if (not re.match(command[3], state[3])):
                continue #pattern matching for surroundings failed(
            result.append(command)
        return result
