from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import advanced_brain as ab
import numpy as np


MODEL_NAME = 'bert-base-nli-mean-tokens'
MODEL = SentenceTransformer(MODEL_NAME)
ROB = ab.AdvancedBrain()


class DialogueManager:
    def __init__(self, greetings=None, on_misundertanding=None):
        self.intents = []
        self.greetings = greetings
        self.on_misunderstanding = on_misundertanding

    def add_intent(self, intent):
        self.intents.append(intent)

    def get_intent_from(self, s):
        m = []
        # print(self.intents)
        for i in self.intents:
            sim = i.compute_similarity(s)
            sim_max = sim[np.argmax(sim)]
            m.append(sim_max)
        return self.intents[np.argmax(m)], m[np.argmax(m)], m

    def get_intent_mean_from(self, s):
        m = []
        for i in self.intents:
            sim = i.compute_similarity(s)
            sim_mean = np.mean(sim)
            m.append(sim_mean)
        return self.intents[np.argmax(m)], m[np.argmax(m)], m

    def add_greetings(self, g):
        self.greetings = g

    def execute_intent(self, intent, s):

        request = intent.name + '('
        if intent.has_parameters:
            for i, p in enumerate(intent.parameters):
                #print(p.name)
                param = p.find_parameter(s)
                if param != None:
                    value = '\'' + param  + '\''
                    request += value
                    if i + 1 < len(intent.parameters):
                        request += ', '
        request += ')'
        print('Executing ' + request)
        ROB.process(request)

    def init_console(self, learning=True):
        input_s = None
        if self.greetings != None:
            print(self.greetings)
        while input_s != 'end':
            input_s = input('Request: ')
            intent, sim, all_sim = self.get_intent_from(input_s)
            if sim >= 0.85:
                self.execute_intent(intent, input_s)
            else:
                #print(all_sim)
                if sum((np.array(all_sim) > 0.65)) == 1 and sim < 0.85:
                    if sim > 0.75:

                        self.execute_intent(intent, input_s)

                    if sim > 0.65 and sim <= 0.75:

                        if intent.on_confirmation != None:
                            confirmation = input(
                                intent.on_confirmation + '   (YES/NO)\n')
                            if confirmation.upper() == 'YES':
                                self.execute_intent(intent, input_s)
                                intent.add_example(input_s)
                            else:
                                print('Aborting the request.')
                        else:
                            confirmation = input(
                                'Intent detected: ' + intent.name + '. Do you want me to do that? (YES/NO)\n')
                            if confirmation.upper() == 'YES':

                                self.execute_intent(intent, input_s)
                                intent.add_example(input_s)
                            else:
                                print('Aborting the request.')

                else:
                    if sum(np.array(all_sim) > 0.65) > 1:
                        print(
                            'The request is too ambiguous, did you want to say something similar to:')
                        print(intent.example[0] + '?')
                        confirmation = input('(YES/NO)\n')
                        if confirmation.upper() == 'YES':
                            self.execute_intent(intent, input_s)
                            intent.add_example(input_s)
                        else:
                            print('Aborting the request.')
                    else:
                        print('No intent has been recognized sorry')


class Intent:
    def __init__(self, name, example, func, on_confirmation=None):
        self.name = name
        self.example = example
        self.func = func
        self.example_vec = MODEL.encode(example)
        self.on_confirmation = on_confirmation
        self.parameters = []
        self.has_parameters = False

    def add_example(self, e):
        self.example.append(e)
        self.example_vec = MODEL.encode(self.example)

    def compute_similarity(self, s, verbose=False):
        s_vec = MODEL.encode(s)
        if verbose:
            print('Sentence example:')
        if verbose:
            print(self.example)
        if verbose:
            print('Comparison to:')
        if verbose:
            print(s)
        sim = cosine_similarity(
            [s_vec],
            self.example_vec
        )
        if verbose:
            print('Similarity: ')
        if verbose:
            print(sim)
        return sim[0]

    def add_parameter(self, p):
        self.has_parameters = True
        self.parameters.append(p)

    def __str__(self):
        return self.name


class ParametersFinder:
    def __init__(self, name, question, n_before_aborting=1, finding_slot=False, force_question=False, raw_answer_as_parameter=False):
        self.intents = []
        self.question = question
        self.n_before_aborting = n_before_aborting
        self.finding_slot = finding_slot
        self.force_question = force_question
        self.raw_answer_as_parameter = raw_answer_as_parameter
        self.name = name

    def add_intent(self, i):
        self.intents.append(i)

    def find_parameter(self, s, k=0):

        if self.force_question:
            s = input(self.question)

        if self.raw_answer_as_parameter:
            return s

        m = []
        i_NAME = []
        for i in self.intents:
            for e in i.example:
                if e.upper() in s.upper():
                    if self.finding_slot:
                        return e
                    else:
                        return i.name
            i_NAME.append(i.name)
            sim = i.compute_similarity(s)
            sim_max = sim[np.argmax(sim)]
            m.append(sim_max)

        if m[np.argmax(m)] > 0.80:

            if self.finding_slot:
                max_sim = 0
                slot_filler = ''
                for w in s.split(' '):
                    for ex in self.intents[np.argmax(m)].example:
                        for exw in ex.split(' '):

                            mem = cosine_similarity(
                                [MODEL.encode(w)], [MODEL.encode(exw)])
                            #print(mem)
                            if max_sim < mem[0]:
                                max_sim = mem[0]
                                slot_filler = exw
                return slot_filler
            else:
                return self.intents[np.argmax(m)].name

        if m[np.argmax(m)] > 0.65 and sum(np.array(m) > 0.65) == 1:
            if self.finding_slot:
                max_sim = 0
                slot_filler = ''
                for w in s.split(' '):
                    for ex in self.intents[np.argmax(m)].example:
                        for exw in ex.split(' '):

                            mem = cosine_similarity(
                                [MODEL.encode(w)], [MODEL.encode(exw)])
                            #print(mem)
                            if max_sim < mem[0]:
                                max_sim = mem[0]
                                slot_filler = exw
                return slot_filler
            else:
                return self.intents[np.argmax(m)].name

        if k >= self.n_before_aborting:
            return None
        else:
            new_s = input(self.question + '\n')
            return self.find_parameter(new_s, k=k+1)

stop = Intent('stop', [
                     'Stop',
                     'Can you stop please?',
                     'Could you please stop?',
                     'Hold on',
                     'Wait',
                     'Dont do that',
                     'Please stop',
                     'Please wait', 
                     'Please hold on'
                     ], None)


help = Intent('help', [
                     'I need some help',
                     'Can you please tell me what you can do?',
                     'What can you do?',
                     'Help please',
                     'Help',
                     'Tell me what you can do',
                     'What can you help me with?',
                     'give me some information',
                     'what do you know?',
                     'which commands do you know?'
                     'which commands do you have?'
                     ], None)


place_block = Intent('place_block', [
                     'Place a block',
                     'Can you place a block please?', 
                     'Could you please place a block?', 
                     'Can you place a wooden block please',
                     'Can you place a stone block please', 
                     'Can you place a dirt block please',
                     'place a wooden block please',
                     'place a stone block please', 
                     'place a dirt block please'
                     ], None)


wood = Intent('default:wood', [
    'Wooden', 'wood', 'planck', 'brown'
],
    None
)

dirt = Intent('default:dirt', [
    'Dirt', 'Grass', 'Green', 'brown'
],
    None
)

stone = Intent('default:cobble', [
    'Stone', 'Grey', 'Cobblestone'
],
    None
)

type = ParametersFinder('type', 'Can you specify the block type?')
type.add_intent(wood)
type.add_intent(dirt)
type.add_intent(stone)
place_block.add_parameter(type)

distance = ParametersFinder(
    'number', 'Can you specify the distance?', finding_slot=True)

distance_i = Intent('distance', [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
],
    None
)

distance.add_intent(distance_i)


# Turn intent
turn = Intent('turn', [
    'Turn around please',
    'Can you turn?',
    'Turn to a direction',
    'Turn left',
    'Turn right',
    'Turn backward',
    'Can you look that way',
    'Can you look',
    'Could you turn right?'
    'Could you turn left?',
    'Could you turn around?',

], None, 'I would like you to confirm that you asked me to change my direction?')


direction = ParametersFinder('direction', 'Can you give me a direction?')

left = Intent('left', [
    'left',
    'turn left',
    'go left'
], None)

right = Intent('right', [
    'right',
    'turn right',
    'go right'
], None)

backward = Intent('backward', [
    'backward',
    'turn backward',
    'go backward'
], None)

forward = Intent('forward', [
    'forward',
    'go forward for 3 block',
    'can you go forward please'
], None)


direction.add_intent(left)
direction.add_intent(right)
direction.add_intent(backward)
direction.add_intent(forward)
turn.add_parameter(direction)

# Move intent

move = Intent('move', [
    'Move',
    'walk',
    'can you walk please',
    'walk to the',
    'walk forward',
    'Can you move',
    'Move five block forward',
    'Go forward',
    'Go',
    'Go forward',
    'Go backward please',
    'can you move for 5 blocks?'

], None, 'I\'m not sure, should I move?')


move.add_parameter(direction)
move.add_parameter(distance)

# Build wall intent


width = Intent('width', [
    'Number', 'amount', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
],
    None,
    'Can you specify the width? '
)

width_parameter = ParametersFinder(
    'width', 'Can you specify the width?', finding_slot=True, force_question=True)
width_parameter.add_intent(width)

height = Intent('height', [
    'Number', 'amount', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
],
    None,
    'Can you specify the height? '
)

height_parameter = ParametersFinder(
    'height', 'Can you specify the height?', finding_slot=True, force_question=True)
height_parameter.add_intent(height)


build_wall = Intent('build_wall', [
    'Can you build a wall?',
    'Could you please build a wall?',
    'Build a wall',
    'A wall please',
    'Can you build a wood wall?',
    'Can you build a wooden wall?',
    'Can you build a dirt wall?',
    'Can you build a stone wall?',
], None, 'You asked me to build a wall, right? ')


build_wall.add_parameter(width_parameter)
build_wall.add_parameter(height_parameter)
build_wall.add_parameter(type)


place_stairs = Intent('build_stairs', [
                      'place stairs',
                      'build stairs',
                      'Place a stair tile please',
                       'Could you please place some stair?'], None)

place_stairs.add_parameter(height_parameter)

# Make window Intent
place_window = Intent('make_window', [
                    'Place a window', 'can you please make a window', 'A window here please', 'make a window please'], None)


# Make door Intent
place_door = Intent('make_door', [
                    'Place a door', 'can you please place a door', 'A door here please', 'place one door please'], None)

greetings = Intent('greeting', [
                   'Hi !', 'Hello, how are you', 'Greetings', 'Nice to meet you'], None)


build_roof = Intent('build_roof', [
    'Can you build a roof?',
    'Could you please build a roof?',
    'Build a roof',
    'A a roof please',
    'Can you build a wood roof?',
    'Can you build a stone roof?',
    'Can you build a stone roof?',
    'Build a wood roof?',
    'Build stone roof?',
    'Build a stone roof?',

], None, 'You asked me to build a roof, right? ')


build_roof.add_parameter(height_parameter)
build_roof.add_parameter(width_parameter)
build_roof.add_parameter(type)


build_floor = Intent('build_floor', [
    'Can you build a floor?',
    'Could you please build a floor?',
    'Build a floor',
    'A a floor please',
    'Can you build a wood floor?',
    'Can you build a stone floor?',
    'Can you build a floor floor?',
    'Build a wood floor?',
    'Build stone floor?',
    'Build a stone floor?',

], None, 'You asked me to build a floor, right? ')

build_floor.add_parameter(width_parameter)
build_floor.add_parameter(type)

destroy_block = Intent('destroy_block', [
                     'Destroy a block',
                     'Can you destroy a block please?', 
                     'Could you remove a block?',
                     'destroy that block',
                     'take away that block',
                     'remove this again',
                     'destroy the block at height five',
                     'destroy the fourth block'
                     ], None)

destroy_block.add_parameter(height_parameter)

d = DialogueManager()

d.add_intent(stop)
d.add_intent(help)
d.add_intent(place_block)
d.add_intent(destroy_block)
d.add_intent(place_stairs)
d.add_intent(place_door)
d.add_intent(greetings)
d.add_intent(build_wall)
d.add_intent(move)
d.add_intent(turn)
d.add_intent(build_roof)
d.add_intent(build_floor)


d.init_console()
