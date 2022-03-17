import sys

class State:
    def __init__(self, list):
        self.list = list

    def __hash__(self):
        tuple1 = tuple(self.list)
        return hash(tuple1)

    def __str__(self):
        return self.list

class Conf:
    def __init__(self, state, word):
        self.state = state
        self.word = word

    def __str__(self):
        result = "Stare: "
        for elem in self.state:
            result += str(elem)
            result += " "
        result += "Caracter: "
        result += self.word
        return result

class Nfa:
    def __init__(self):
        self.alphabet = []
        self.initial_state = None
        self.delta = {}
        self.final_state = None
        self.states = []

    def get_epsilon_closure(self, state):
        epsilon_closure = set()
        epsilon_closure.add(state.list[0])

        q = []
        q.append(state.list[0])
        visited = []
        visited.append(state.list[0])

        while len(q) > 0:
            state = q.pop()
            for key, value in self.delta.items():
                if (key.state.list[0] == state) and (key.word == "epsilon"):
                    epsilon_closure.add(value.list[0])
                    if value.list[0] not in visited:
                        q.append(value.list[0])
                        visited.append(value.list[0])


        return list(epsilon_closure)

    def print_nfa(self):
        print("Alphabet: ")
        print(self.alphabet)
        print("Initial state: ")
        print(self.initial_state.list)
        print("Final state: ")
        print(self.final_state.list)
        print("States: ")
        for state in self.states:
            print(state.list)
        print("Delta: ")
        for key, value in self.delta.items():
            print(key.state.list)
            print(key.word)
            print(value.list)
            print(" ")

class Dfa:
    def __init__(self):
        self.alphabet = []
        self.initial_state = None
        self.delta = {}
        self.final_state = None
        self.states = []

    def print_dfa(self, output_file):
        f = open(output_file, "w")
        for elem in self.alphabet:
            f.write(elem)
        f.write("\n")

        f.write(str(len(self.states)))
        f.write("\n")

        f.write(str(self.initial_state.list[0]))
        f.write("\n")

        for state in self.final_state:
            f.write(str(state.list[0]))
            if self.final_state[-1] != state:
                f.write(" ")
        f.write("\n")

        i = 0
        delta_len = len(self.delta)
        for key, value in self.delta.items():
            f.write(str(key.state.list[0]))
            f.write(",")
            f.write("\'")
            f.write(key.word)
            f.write("\'")
            f.write(",")
            f.write(str(value.list[0]))
            if i != delta_len - 1:
                f.write("\n")
            i += 1
        f.close()

    def complete_dfa(self):
        max = 0
        for state in self.states:
            if state.list[0] > max:
                max = state.list[0]

        self.states.append(State([max + 1]))

        for char in self.alphabet:
            for state in self.states:
                if self.conf_exists_in_delta(state, char) == 0:
                    self.delta[Conf(state, char)] = State([max + 1])


    def conf_exists_in_delta(self, state, char):
        for key, value in self.delta.items():
            if state.list[0] == key.state.list[0] and key.word == char:
                return 1

        return 0

def Character(elem, count):
    nfa = Nfa()
    nfa.states = [State([count]), State([count + 1])]
    nfa.initial_state = State([count])
    nfa.final_state = State([count + 1])
    nfa.alphabet = [elem]
    nfa.delta[Conf(State([count]), elem)] = State([count + 1])

    return nfa

def Star(nfa, count):
    new_nfa = Nfa()
    new_nfa.states = nfa.states
    new_nfa.states.append(State([count]))
    new_nfa.states.append(State([count + 1]))
    new_nfa.initial_state = State([count])
    new_nfa.final_state = State([count + 1])
    new_nfa.alphabet = nfa.alphabet
    new_nfa.delta = nfa.delta
    new_nfa.delta[Conf(new_nfa.initial_state, "epsilon")] = nfa.initial_state
    new_nfa.delta[Conf(nfa.final_state, "epsilon")] = new_nfa.final_state
    new_nfa.delta[Conf(nfa.final_state, "epsilon")] = nfa.initial_state
    new_nfa.delta[Conf(new_nfa.initial_state, "epsilon")] = new_nfa.final_state

    return new_nfa

def Concat(nfa1, nfa2):
    new_nfa = Nfa()
    new_nfa.states = nfa1.states
    for state in nfa2.states:
        new_nfa.states.append(state)
    new_nfa.alphabet = nfa1.alphabet
    for elem in nfa2.alphabet:
        new_nfa.alphabet.append(elem)
    new_nfa.initial_state = nfa1.initial_state
    new_nfa.final_state = nfa2.final_state
    new_nfa.delta = nfa1.delta
    for key, value in nfa2.delta.items():
        new_nfa.delta[key] = value
    new_nfa.delta[Conf(nfa1.final_state, "epsilon")] = nfa2.initial_state

    return new_nfa

def Union(nfa1, nfa2, count):
    new_nfa = Nfa()
    new_nfa.states = nfa1.states
    for state in nfa2.states:
        new_nfa.states.append(state)
    new_nfa.alphabet = nfa1.alphabet
    for elem in nfa2.alphabet:
        new_nfa.alphabet.append(elem)
    new_nfa.states.append(State([count]))
    new_nfa.states.append(State([count + 1]))
    new_nfa.initial_state = State([count])
    new_nfa.final_state = State([count + 1])
    new_nfa.delta = nfa1.delta
    for key, value in nfa2.delta.items():
        new_nfa.delta[key] = value
    new_nfa.delta[Conf(new_nfa.initial_state, "epsilon")] = nfa1.initial_state
    new_nfa.delta[Conf(new_nfa.initial_state, "epsilon")] = nfa2.initial_state
    new_nfa.delta[Conf(nfa1.final_state, "epsilon")] = new_nfa.final_state
    new_nfa.delta[Conf(nfa2.final_state, "epsilon")] = new_nfa.final_state

    return new_nfa

def Plus(nfa, count):
    new_nfa = Nfa()
    new_nfa.states = nfa.states
    new_nfa.states.append(State([count]))
    new_nfa.states.append(State([count + 1]))
    new_nfa.initial_state = State([count])
    new_nfa.final_state = State([count + 1])
    new_nfa.alphabet = nfa.alphabet
    new_nfa.delta = nfa.delta
    new_nfa.delta[Conf(new_nfa.initial_state, "epsilon")] = nfa.initial_state
    new_nfa.delta[Conf(nfa.final_state, "epsilon")] = new_nfa.final_state
    new_nfa.delta[Conf(new_nfa.final_state, "epsilon")] = new_nfa.initial_state

    return new_nfa

def nfa_to_dfa(nfa):
    dfa = Dfa()
    dfa.alphabet = nfa.alphabet

    epsilon_closure = {}
    for state in nfa.states:
        epsilon_closure[state.list[0]] = nfa.get_epsilon_closure(state)

    stack = []
    stack.append(State(epsilon_closure[nfa.initial_state.list[0]]))
    index = 0
    dfa.initial_state = State(epsilon_closure[nfa.initial_state.list[0]])
    dfa.states.append(State(epsilon_closure[nfa.initial_state.list[0]]))

    while len(stack) > 0:
        state = stack.pop(index)
        index -= 1
        for character in nfa.alphabet:
            new_state = set()
            for elem in state.list:
                for key, value in nfa.delta.items():
                    if (key.state.list[0] == elem) and (key.word == character):
                        for el in epsilon_closure[value.list[0]]:
                            new_state.add(el)

            if len(new_state) == 0:
                continue;

            state_already_exists = 0
            for st in dfa.states:
                if list(new_state) == st.list:
                    state_already_exists = 1

            if state_already_exists == 0:
                dfa.states.append(State(list(new_state)))
                stack.append(State(list(new_state)))
                index += 1

            dfa.delta[Conf(state, character)] = State(list(new_state))


    f_states = set()
    for state in dfa.states:
        if nfa.final_state.list[0] in state.list:
            f_states.add(state)
    dfa.final_state = list(f_states)

    new_states = {}
    new_dfa_states = []
    count = 0
    for state in dfa.states:
        new_states[str(state.list)] = State([count])
        new_dfa_states.append(State([count]))
        count += 1

    dfa.states = new_dfa_states

    initial_state = new_states[str(dfa.initial_state.list)]
    dfa.initial_state = initial_state

    new_final_states = []
    for final_state in dfa.final_state:
        new_final_state = new_states[str(final_state.list)]
        new_final_states.append(new_final_state)
    dfa.final_state = new_final_states

    new_delta = {}
    for key, value in dfa.delta.items():
        state1 = new_states[str(key.state.list)]
        character = key.word
        state2 = new_states[str(value.list)]
        new_delta[Conf(state1, character)] = state2
    dfa.delta = new_delta

    return dfa

def prenex_to_dfa(prenex_input):
    stack = []
    count = 0
    index = -1

    prenex_regex = prenex_input
    if (prenex_input != " "):
        prenex_regex = prenex_input.split(" ")
        prenex_regex.reverse()

    i = 0
    for elem in prenex_regex:
        if elem == "STAR":
            nfa = stack.pop(index)
            stack.append(Star(nfa, count))
            count += 2
        elif elem == "CONCAT":
            nfa1 = stack.pop(index)
            index -= 1
            nfa2 = stack.pop(index)
            index -= 1
            stack.append(Concat(nfa1, nfa2))
            index += 1
        elif elem == "UNION":
            nfa1 = stack.pop(index)
            index -= 1
            nfa2 = stack.pop(index)
            index -= 1
            stack.append(Union(nfa1, nfa2, count))
            index += 1
            count += 2
        elif elem == "PLUS":
            nfa = stack.pop(index)
            stack.append(Plus(nfa, count))
            count += 2
        elif elem == "'":
            if i % 2 == 0:
                stack.append(Character(" ", count))
                index += 1
                count += 2
            i += 1
        else:
            stack.append(Character(elem, count))
            index += 1
            count += 2

    nfa = stack.pop()
    dfa = nfa_to_dfa(nfa)
    dfa.complete_dfa()
    return dfa