from main import *
from Lexer import *

def reverse(my_word):
    word = list(my_word)
    aux = None
    start = 0
    end = len(word) - 1

    while (start < end):
        aux = word[start]
        word[start] = word[end]
        word[end] = aux
        start += 1
        end -= 1

    my_word_reversed = ''.join(word)
    return my_word_reversed

def get_priority(operator):
    if operator == '*':
        return 3
    elif operator == '+':
        return 3
    elif operator == '|':
        return 2
    else:
        return 1 # concatenation

def infix_to_postfix(infix):
    q = []
    operator_stack = []

    for i in range(len(infix)):
        if infix[i] == "'":
            q.append(infix[i])
            # if (len(q) > 0) and (q.pop() == "' '"):
            #     continue
            # print("Urmeaza spatiu")
            # q.append("\' \'")
            # i += 2
        elif infix[i] == " ":
            q.append(infix[i])
            #continue
        elif infix[i] == '(':
            operator_stack.append(infix[i])
        elif infix[i] == ')':
            operator_on_top = operator_stack.pop()
            while operator_on_top != '(':
                q.append(operator_on_top)
                if len(operator_stack) <= 0:
                    break
                operator_on_top = operator_stack.pop()
        elif (infix[i] == '*' or infix[i] == '+' or infix[i] == '|' or infix[i] == '.'):
            if len(operator_stack) > 0:
                operator_on_top = operator_stack.pop()
                if (operator_on_top == '*' or operator_on_top == '+' or operator_on_top == '|' or operator_on_top == '.'):
                    if (get_priority(operator_on_top) < get_priority(infix[i])):
                        operator_stack.append(operator_on_top)
                    while ((get_priority(operator_on_top) >= get_priority(infix[i]))):
                        q.append(operator_on_top)
                        if len(operator_stack) <= 0:
                            break
                        operator_on_top = operator_stack.pop()
                        if operator_on_top == "(":
                            operator_stack.append("(")
                            break
                elif operator_on_top == '(':
                    operator_stack.append("(")
            operator_stack.append(infix[i])
        else:
            q.append(infix[i])

    while len(operator_stack) > 0:
        operator_on_top = operator_stack.pop()
        q.append(operator_on_top)

    postfix = ""
    for elem in q:
        postfix += elem

    return postfix

def infix_to_prefix(infix):
    regex = reverse(infix)
    aux_regex = list(regex)
    for i in range(len(aux_regex)):
        if aux_regex[i] == "(":
            aux_regex[i] = ")"
        elif aux_regex[i] == ")":
            aux_regex[i] = "("
    regex = ''.join(aux_regex)
    prefix = infix_to_postfix(regex)
    return reverse(prefix)

def get_prenex_form(regex):
    if regex == "' '":
        return " "
    if regex == "'\\n'":
        return "\\n"

    prenex_form = ""
    for i in range(len(regex)):
        if (regex[i] == "'"):
            # daca marcheaza sfarsitul
            if i >= 2 and regex[i - 2] == "'":
                prenex_form += regex[i]
                if i < len(regex) - 1:
                    prenex_form += " "
                continue
            # daca e prima '
            else:
                prenex_form += regex[i]
                continue

        if (regex[i] == " ") or (regex[i] == "\\") or (regex[i] == "n" and regex[i - 1] == "\\"):
            prenex_form += regex[i]
            continue

        if regex[i] == "*":
            prenex_form += "STAR"
        elif regex[i] == "+":
            prenex_form += "PLUS"
        elif regex[i] == "|":
            prenex_form += "UNION"
        elif regex[i] == ".":
            prenex_form += "CONCAT"
        else:
            prenex_form += regex[i]
        if i < len(regex) - 1:
            prenex_form += " "

    return prenex_form

def concatenation_highlight(regex):
    if regex == "' '":
        return regex
    if regex == "'\\n'":
        return regex

    new_regex = ""
    i = 0
    for i in range(len(regex) - 1):
        if (regex[i] == "'"):
            if i >= 2 and regex[i - 2] == "'":
                if regex[i + 1] != "*" and regex[i + 1] != "+" and regex[i + 1] != "|" and regex[i + 1] != ")":
                    new_regex += regex[i]
                    new_regex += "."
                else:
                    new_regex += regex[i]
            else:
                new_regex += regex[i]
            continue

        if (regex[i] == " "):
            new_regex += regex[i]
            continue


        if regex[i] != "*" and regex[i] != "+" and regex[i] != "|" and regex[i] != "(" and regex[i] != ")":
            if regex[i + 1] != "*" and regex[i + 1] != "+" and regex[i + 1] != "|" and regex[i + 1] != "(" and regex[i + 1] != ")":
                new_regex += regex[i]
                new_regex += '.'
            elif regex[i + 1] == "(":
                new_regex += regex[i]
                new_regex += '.'
            else:
                new_regex += regex[i]
        elif regex[i] == "*" or regex[i] == "+":
            if regex[i + 1] != ")" and regex[i + 1] != "|":
                new_regex += regex[i]
                new_regex += '.'
            else:
                new_regex += regex[i]
        elif regex[i] == ")":
            if regex[i + 1] != "|" and regex[i + 1] != "*" and regex[i + 1] != "+" and regex[i + 1] != ")":
                new_regex += regex[i]
                new_regex += '.'
            else:
                new_regex += regex[i]
        else:
            new_regex += regex[i]

    new_regex += regex[len(regex) - 1]
    return new_regex

def dfa_to_string_etapa1(dfa, token):
    string = ""
    for elem in dfa.alphabet:
        string += elem
    string += "\n"
    string += token
    string += "\n"
    string += str(dfa.initial_state.list[0])
    string += "\n"

    for key, value in dfa.delta.items():
        string += str(key.state.list[0])
        string += ",'"
        string += key.word
        string += "',"
        string += str(value.list[0])
        string += "\n"

    for final_state in dfa.final_state:
        string += str(final_state.list[0])
        string += " "

    return string[0: len(string) - 1]

def runcompletelexer(lexer, finput, foutput):
    f = open(lexer, "r")
    lexer_content = f.read()

    tokens_lexemes = lexer_content.split(";\n")
    priority = 0
    dfas = []
    for elem in tokens_lexemes[0:len(tokens_lexemes) - 1]:
        index = elem.find(" ")
        token = elem[0:index]
        regex = elem[index + 1:]

        new_regex = concatenation_highlight(regex)
        prefix = infix_to_prefix(new_regex)
        prenex_form = get_prenex_form(prefix)

        dfa = prenex_to_dfa(prenex_form)
        dfa.print_dfa("my_dfa.txt")
        dfa_string_etapa1 = dfa_to_string_etapa1(dfa, token)
        final_dfa = Dfa1(dfa_string_etapa1, priority)
        dfas.append(final_dfa)
        priority += 1

    lexer = Lexer(dfas)
    f_input = open(finput, "r")
    word = f_input.read()
    lexer.identify_lexemes(word, foutput)

def runparser():
    return
