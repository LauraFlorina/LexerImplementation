import sys

class State1:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

class Conf1:
    def __init__(self, state, word):
        self.tuple = (state, word)

class Dfa1:
    def __init__(self, string, priority):
        lines = string.split("\n")

        self.priority = priority
        self.alphabet = list(lines[0])
        self.token = lines[1]
        self.initial_state = State1(lines[2])

        delta = {}
        self.adj = {}
        states_name = set()

        for line in lines[3:len(lines) - 1]:
            elements = line.split(",")
            if elements[1][1:-1] == "\\n":
                symbol = "\n"
            else :
                symbol = elements[1][1:-1]
            delta[(State1(elements[0]), symbol)] = State1(elements[2])
            if (elements[2] in self.adj):
                self.adj[elements[2]].append(elements[0])
            else:
                self.adj[elements[2]] = []
                self.adj[elements[2]].append(elements[0])
            states_name.add(elements[0])
            states_name.add(elements[2])

        self.states_name = list(states_name)
        self.delta = delta
        self.final_states = []

        for element in lines[-1].split(" "):
            self.final_states.append(State1(element))

    def step(self, conf: Conf1) -> Conf1:
        for key, value in self.delta.items():
            if (key[0].name == conf.tuple[0].name) and (key[1] == conf.tuple[1][0]):
                return Conf1(value, (conf.tuple[1])[1:])
        return None

    def accept(self, word: str) -> bool:
        next_conf = Conf1(self.initial_state, word)
        while (len(next_conf.tuple[1]) > 0):
            next_conf = self.step(next_conf)
            if next_conf == None:
                return False
        for final_state in self.final_states:
            if (next_conf.tuple[0].name == final_state.name):
                return True
        return False

    def get_sink_states(self):
        sink_states = []
        q = []
        for state in self.final_states:
            q.append(state.name)

        visited = set()
        while (len(q) > 0):
            node = q.pop(0)
            visited.add(node)
            if node in self.adj:
                for state_name in self.adj[node]:
                    if (state_name not in visited):
                        q.append(state_name)
                        visited.add(state_name)

        visit = list(visited)
        for state_name in self.states_name:
            if state_name not in visit:
                sink_states.append(state_name)

        return sink_states


class Lexer:
    def __init__(self, dfas: [Dfa1]):
        self.dfas = dfas;

    def identify_lexemes(self, word: str, foutput) -> str:
        f = open(foutput, "w")

        lex_found = {}
        lex_found_index = {}
        lex_found_len = {}
        dfa_current_state = {}
        dfa_action = {}
        sink_states_name = {}
        dfa_final_states_name = {}
        i = 0

        for dfa in self.dfas:
            dfa_current_state[dfa] = dfa.initial_state
            sink_states_name[dfa] = dfa.get_sink_states()
            dfa_action[dfa] = "initial"
            for state in dfa.final_states:
                if dfa in dfa_final_states_name :
                    dfa_final_states_name[dfa].append(state.name)
                else :
                    dfa_final_states_name[dfa] = [state.name]

        line = 0
        while i < len(word):
            if word[i] == "\n":
                line += 1
            for dfa in self.dfas:
                if (dfa_action[dfa] != "reject"):
                    next_config = dfa.step(Conf1(dfa_current_state[dfa], word[i]))
                    if (next_config is None):
                        dfa_action[dfa] = "reject"
                        continue
                    dfa_current_state[dfa] = next_config.tuple[0]
                    if (next_config.tuple[0].name in sink_states_name[dfa]):
                        dfa_action[dfa] = "reject"
                    elif (next_config.tuple[0].name in dfa_final_states_name[dfa]):
                        dfa_action[dfa] = "accept"
                        if dfa in lex_found :
                            aux = lex_found[dfa]
                            aux = aux + word[i]
                            lex_found[dfa] = aux
                        else:
                            lex_found[dfa] = word[i]

                        lex_found_index[dfa] = i
                        lex_found_len[dfa] = len(lex_found[dfa])
                    else:
                        dfa_action[dfa] = "seeking"
                        if dfa in lex_found:
                            aux = lex_found[dfa]
                            aux = aux + word[i]
                            lex_found[dfa] = aux
                        else:
                            lex_found[dfa] = word[i]
                # daca am ajuns pe ultimul index din cuvant, se forteaza
                # ca automatul sa respinga, chiar daca el a acceptat anterior
                # pentru a se putea realiza impartirea in tokeni,
                # implementata mai jos

                if i == len(word) - 1:
                    dfa_action[dfa] = "reject"

            i += 1
            ok = 1
            for dfa in self.dfas:
                if dfa_action[dfa] != "reject":
                    ok = 0

            # daca nu au ajuns toate automatele in starea de reject
            # se trece la urmatorul caracter din cuvant
            if (ok == 0):
                continue

            max = -1
            token = None
            lexem = None
            priority = sys.maxsize
            for dfa, index in lex_found_index.items():
                if index > max:
                    max = index
                    # din lexemul gasit se ia pana la indexul unde automatul
                    # a acceptat ultima data
                    lexem = lex_found[dfa][:lex_found_len[dfa]]
                    token = dfa.token
                    priority = dfa.priority
                elif index == max:
                    if dfa.priority < priority:
                        priority = dfa.priority
                        token = dfa.token

            if (lexem == "\n") :
                lexem = "\\n"

            if (token != None) :
                f.write(token + " " + lexem + "\n")
            else :
                f.close()
                f = open(foutput, "w")
                # cand ajung pe ultimul index
                if (i - 1 == len(word) - 1) :
                    # se verifica daca a existat un automat care a ajuns in starea de seeking
                    # caz in care ar mai fi putut continua cautarea, insa se ajunge la EOF
                    if (len(lex_found) > 0) :
                        f.write("No viable alternative at character EOF, line " + str(line))
                        return
                f.write("No viable alternative at character " + str(i - 1) + ", line " + str(line))
                return

            i = max + 1
            lex_found = {}
            lex_found_len = {}
            lex_found_index = {}
            for dfa in self.dfas:
                dfa_action[dfa] = "initial"
                dfa_current_state[dfa] = dfa.initial_state

        f.close()


def runlexer(lexer, finput, foutput):
    f = open(lexer, "r")
    lexer_content = f.read()

    dfas_as_text = lexer_content.split("\n\n")
    dfas = []

    # variabila i retine prioritatea dfa-ului
    # radand ordinea in care apare in fisier
    i = 0
    for dfa_as_text in dfas_as_text:
        dfa = Dfa1(dfa_as_text, i)
        dfas.append(dfa)
        i += 1

    f = open(finput, "r")
    word = f.read()

    lexer = Lexer(dfas)
    lexer.identify_lexemes(word, foutput)

