import sys
import keyword

keyList = [
    "function",
    "integer",
    "boolean",
    "real",
    "if",
    "endif",
    "else",
    "return",
    "put",
    "get",
    "while",
    "true",
    "false",
]
arithOps = ["*", "/"]
assignOps = ["="]
comparOps = [">", "<"]
logOps = ["&", "!"]
seperatorOps = [",", ";", ":", "[", "]", "{", "}", "(", ")", "$"]

global queuedText
global lineCounter
global legalTokens
global outFile
global instructionTable
global symbolTable
global jumpStack
global memoryCounter
global addressCounter
global qualifier
global relatop
global getStack

symbol = [arithOps, assignOps, comparOps, logOps, seperatorOps]

# State Types
STATE_INITIAL = 0
STATE_KEY_IDENT = 1  # Keyword or Identifier
STATE_VALUE_TRANSITION = 2  # + or - transition state
STATE_OPS_SEPS = 3  # Operators or Seporators states
STATE_ERROR = 4  # Error State
STATE_INT = 5  # Integer State
STATE_REAL = 6  # Real State
STATE_KEYWORD = 7
STATE_IDENTIFIER = 8
STATE_SEPERATOR = 9

# State Names
state_names = {
    STATE_INITIAL: "INITIAL STATE (HOW?)",
    STATE_KEY_IDENT: "KEYWORD / IDENTIFIER (HOW x 2?)",
    STATE_VALUE_TRANSITION: "VALUE TRANSITION STATE (HOW x 3?)",
    STATE_OPS_SEPS: "Operator",
    STATE_ERROR: "Error",
    STATE_INT: "Integer",
    STATE_REAL: "Real",
    STATE_KEYWORD: "Keyword",
    STATE_IDENTIFIER: "Identifier",
    STATE_SEPERATOR: "Seperator",
}

# Character Types
CT_ALPHABET = 0
CT_DIGIT = 1
CT_DECIMAL = 2
CT_SPACE = 3
CT_SYMBOL = 4
CT_VALUE = 5
CT_ILLEGAL = 6


transitional_table = {
    STATE_INITIAL: {
        CT_ALPHABET: STATE_KEY_IDENT,
        CT_DIGIT: STATE_INT,
        CT_DECIMAL: STATE_REAL,
        CT_SPACE: STATE_INITIAL,
        CT_SYMBOL: STATE_OPS_SEPS,
        CT_VALUE: STATE_VALUE_TRANSITION,
        CT_ILLEGAL: STATE_ERROR,
    },
    STATE_KEY_IDENT: {
        CT_ALPHABET: STATE_KEY_IDENT,
        CT_DIGIT: STATE_KEY_IDENT,
        CT_DECIMAL: STATE_ERROR,
        CT_SPACE: STATE_INITIAL,
        CT_SYMBOL: STATE_ERROR,
        CT_VALUE: STATE_ERROR,
        CT_ILLEGAL: STATE_ERROR,
    },
    STATE_VALUE_TRANSITION: {
        CT_ALPHABET: STATE_ERROR,
        CT_DIGIT: STATE_INT,
        CT_DECIMAL: STATE_REAL,
        CT_SPACE: STATE_INITIAL,
        CT_SYMBOL: STATE_OPS_SEPS,
        CT_VALUE: STATE_OPS_SEPS,
        CT_ILLEGAL: STATE_ERROR,
    },
    STATE_OPS_SEPS: {
        CT_ALPHABET: STATE_ERROR,
        CT_DIGIT: STATE_ERROR,
        CT_DECIMAL: STATE_OPS_SEPS,
        CT_SPACE: STATE_INITIAL,
        CT_SYMBOL: STATE_OPS_SEPS,
        CT_VALUE: STATE_OPS_SEPS,
        CT_ILLEGAL: STATE_ERROR,
    },
    STATE_ERROR: { 
        CT_ALPHABET: STATE_ERROR,
        CT_DIGIT: STATE_ERROR,
        CT_DECIMAL: STATE_ERROR,
        CT_SPACE: STATE_INITIAL,
        CT_SYMBOL: STATE_ERROR,
        CT_VALUE: STATE_ERROR,
        CT_ILLEGAL: STATE_ERROR,
    },
    STATE_INT: {
        CT_ALPHABET: STATE_ERROR,
        CT_DIGIT: STATE_INT,
        CT_DECIMAL: STATE_REAL,
        CT_SPACE: STATE_INITIAL,
        CT_SYMBOL: STATE_ERROR,
        CT_VALUE: STATE_ERROR,
        CT_ILLEGAL: STATE_ERROR,
    },
    STATE_REAL: {
        CT_ALPHABET: STATE_ERROR,
        CT_DIGIT: STATE_REAL,
        CT_DECIMAL: STATE_ERROR,
        CT_SPACE: STATE_INITIAL,
        CT_SYMBOL: STATE_ERROR,
        CT_VALUE: STATE_ERROR,
        CT_ILLEGAL: STATE_ERROR,
    },
}


def getChar(c):
    if c.isspace() or c == "":
        return CT_SPACE
    elif c == "+" or c == "-":
        return CT_VALUE
    elif c == ".":
        return CT_DECIMAL
    elif c.isalpha() or c == "_":
        return CT_ALPHABET
    elif c.isdigit():
        return CT_DIGIT
    else:
        for i in symbol:
            if c in i:
                return CT_SYMBOL
                break
    return CT_ILLEGAL


def getText(file):
    txt = open(file)
    global outFile
    outFile = open(f"out_{file}","w")
    parsedTxt = ""
    c = txt.read(1)
    while c != "":
        parsedTxt += c
        c = txt.read(1)
    return parsedTxt


def removeComments(text):
    newText = ""
    read = True
    i = 0
    while i < len(text) - 1:
        if text[i] == "/" and text[i + 1] == "*":
            read = False
        if text[i] == "*" and text[i + 1] == "/":
            read = True
            i += 2
        if read and i < len(text) - 1:
            newText += text[i]
        i += 1
    if read == True:
        newText += text[i]
    return newText


def spaceOpsandSeps(text):
    newText = ""
    i = 0
    while i < len(text) - 1:
        if getChar(text[i]) != CT_SYMBOL and getChar(text[i + 1]) == CT_SYMBOL:
            if getChar(text[i]) != CT_SPACE:
                newText += text[i]
                newText += " "
            else:
                newText += text[i]
        elif getChar(text[i]) == CT_SYMBOL and getChar(text[i + 1]) != CT_SYMBOL:
            if getChar(text[i + 1]) != CT_SPACE:
                newText += text[i]
                newText += " "
            else:
                newText += text[i]
        else:
            newText += text[i]
        i += 1
    newText += text[i]
    return newText


def lexer():
    global queuedText
    global lineCounter
    token = ""
    char = queuedText[0]
    curState = STATE_INITIAL
    charType = getChar(char)
    nextState = transitional_table[curState][charType]
    while nextState != STATE_INITIAL:
        token += char
        if char in seperatorOps:
            queuedText = queuedText[1:]
            return STATE_SEPERATOR, token
        curState == STATE_SEPERATOR
        curState = nextState
        queuedText = queuedText[1:]
        if len(queuedText) == 0:
            return curState, token
        char = queuedText[0]
        charType = getChar(char)
        nextState = transitional_table[curState][charType]
    queuedText = queuedText[1:]
    if char == "\n":
        lineCounter += 1
    if token in keyList:
        curState = STATE_KEYWORD
    elif curState == STATE_KEY_IDENT:
        curState = STATE_IDENTIFIER
    elif (
        curState == STATE_VALUE_TRANSITION
        and transitional_table[curState][charType] == STATE_INITIAL
    ):
        curState = STATE_OPS_SEPS
    elif curState == STATE_INITIAL:
        if transitional_table[curState][charType] == STATE_INITIAL:
            return None
    return curState, token

def get_address(identifier):
    global symbolTable
    global qualifier
    global memoryCounter
    if identifier[1] not in symbolTable['ident']:
        symbolTable['ident'].append(identifier[1])
        symbolTable['mem'].append(memoryCounter)
        symbolTable['type'].append(qualifier)
        memoryCounter += 1
        return memoryCounter - 1
    return symbolTable['mem'][symbolTable['ident'].index(identifier[1])]

def gen_inst(op, oprnd):
    global instructionTable
    global addressCounter
    instructionTable.append([addressCounter, op, oprnd])
    addressCounter += 1

def backPatch(jumpAddr):
    global jumpStack
    global instructionTable
    address = jumpStack[-1]
    jumpStack = jumpStack[:-1]
    instructionTable[address - 1][2] = jumpAddr

def rat22f():
    global legalTokens
##    if legalTokens[0][1] == "function":
##        optFuncDefs()
##        print(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Rat22F>  ::=   <Opt Function Definitions>   $  <Opt Declaration List>  <Statement List>  $")
    if legalTokens[0][1] == "$":
        legalTokens = legalTokens[1:]
        while legalTokens[0][1] != "$":
            if legalTokens[0][1] == "integer" or legalTokens[0][1] == "boolean":
                optDecList()
            stateList()
        if legalTokens[0][1] == "$":
            empty()
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected $ #1")
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected $ #2")


##def optFuncDefs():
##    global legalTokens
##    print(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Opt Function Definitions> ::= <Function Definitions>  |  <Empty>")
##    funcDefs()
##
##
##def funcDefs():
##    global legalTokens
##    print(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Function Definitions>  ::= <Function>  <Function Definitions’>")
##    func()
##    funcDefsPrime()
##
##
##def funcDefsPrime():
##    global legalTokens
##    if legalTokens[0][1] == "function":
##        print(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Function Definitions’> ::= <Functions Definitions>")
##        funcDefs()
##    else:
##        print(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Function Definitions’> ::= <Empty>")
##        empty()
##
##def func():
##    global legalTokens
##    if legalTokens[0][1] == "function":
##        legalTokens = legalTokens[1:]
##    else:
##        return empty()
##    if legalTokens[0][0] == STATE_IDENTIFIER:
##        legalTokens = legalTokens[1:]
##        if legalTokens[0][1] == "(":
##            legalTokens = legalTokens[1:]
##            if legalTokens[0][1] != ")":
##                print(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Opt Parameter List> ::=  <Parameter List>  |   <Empty>")
##                paramList()
##            if legalTokens[0][1] == ")":
##                legalTokens = legalTokens[1:]
##                if legalTokens[0][1] != "{":
##                    decList()
##                if legalTokens[0][1] == "{":
##                    body()
##                    print(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Function> ::= function  <Identifier>   ( <Opt Parameter List> )  <Opt Declaration List>  <Body>")
##                else:
##                    raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'{'}")
##            else:
##                raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
##        else:
##            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
##    else:
##        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Identifier>")

def paramList():
    global legalTokens
    param()
    paramListPrime()


def paramListPrime():
    global legalTokens
    if legalTokens[0][1] == ",":
        legalTokens = legalTokens[1:]
        paramList()
    else:
        empty()


def param():
    global legalTokens
    ids()
    qual()


def qual():
    global legalTokens
    global qualifier
    if legalTokens[0][1] == "boolean":
        qualifier = legalTokens[0][1]
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "integer":
        qualifier = legalTokens[0][1]
        legalTokens = legalTokens[1:]
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Qualifier>")


def body():
    global legalTokens
    if legalTokens[0][1] == "{":
        legalTokens = legalTokens[1:]
        stateList()
        if legalTokens[0][1] == "}":
            legalTokens = legalTokens[1:]
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'{'}")


def optDecList():
    global legalTokens
    decList()
    


def decList():
    global legalTokens
    dec()
    if legalTokens[0][1] == ";":
        legalTokens = legalTokens[1:]
        decListPrime()
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")


def decListPrime():
    global legalTokens
    if (
        legalTokens[0][1] == "integer"
        or legalTokens[0][1] == "boolean"
    ):
        decList()
    else:
        empty()


def dec():
    global legalTokens
    qualif = qual()
    identif = ids()


def ids():
    global getStack
    global legalTokens
    if legalTokens[0][0] == STATE_IDENTIFIER:
        getStack.append(get_address(legalTokens[0]))
        legalTokens = legalTokens[1:]
        idsPrime()
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Identifier>")


def idsPrime():
    global legalTokens
    if legalTokens[0][1] == ",":
        legalTokens = legalTokens[1:]
        ids()
    else:
        empty()


def stateList():
    global legalTokens
    statement()
    stateListPrime()


def stateListPrime():
    global legalTokens
    if(
        legalTokens[0][0] == STATE_IDENTIFIER
        or legalTokens[0][1] == "{"
        or legalTokens[0][1] == "if"
        or legalTokens[0][1] == "return"
        or legalTokens[0][1] == "put"
        or legalTokens[0][1] == "get"
        or legalTokens[0][1] == "while"
    ):
        statement()
    else:
        empty()


def statement():
    global legalTokens
    if legalTokens[0][1] == "{":
        comp()
    elif legalTokens[0][0] == STATE_IDENTIFIER:
        assign()
    elif legalTokens[0][1] == "if":
        implication()
    elif legalTokens[0][1] == "return":
        ret()
    elif legalTokens[0][1] == "put":
        printPut()
    elif legalTokens[0][1] == "get":
        scanGet()
    elif legalTokens[0][1] == "while":
        condLoop()
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Statement>")


def comp():
    global legalTokens
    if legalTokens[0][1] == "{":
        legalTokens = legalTokens[1:]
        while legalTokens[0][1] != "}":
            stateList()
        if legalTokens[0][1] == "}":
            legalTokens = legalTokens[1:]
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'}'}")
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'{'}")


def assign():
    global legalTokens
    if legalTokens[0][0] == STATE_IDENTIFIER:
        save = legalTokens[0]
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "=":
            legalTokens = legalTokens[1:]
            exp()
            gen_inst("POPM", get_address(save))
            if legalTokens[0][1] == ";":
                legalTokens = legalTokens[1:]
            else:
                raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected =")
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Identifier>")
			


def implication():
    global legalTokens
    if legalTokens[0][1] == "if":
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "(":
            legalTokens = legalTokens[1:]
            cond()
            if legalTokens[0][1] == ")":
                legalTokens = legalTokens[1:]
                statement()
                backPatch(addressCounter)
                implicationPrime()
                if legalTokens[0][1] == "endif":
                    legalTokens = legalTokens[1:]
                    if legalTokens[0][1] == ';':
                        gen_inst("LABEL", "NIL")
                        legalTokens = legalTokens[1:]
                        stateListPrime()
                    else:
                        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
                else:
                    raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [endif]")
            else:
                raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [if]")


def implicationPrime():
    global legalTokens
    if legalTokens[0][1] == "else":
        legalTokens = legalTokens[1:]
        statement()
        backPatch(addressCounter)
    elif legalTokens[0][1] == "endif":
        empty()
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected else <statement> or endif")


def ret():
    global legalTokens
    if legalTokens[0][1] == "return":
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] != ";":
            retPrime()
        if legalTokens[0][1] == ";":
            legalTokens = legalTokens[1:]
            empty()
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Return>")


def retPrime():
    exp()


def printPut():
    global legalTokens
    if legalTokens[0][1] == "put":
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "(":
            legalTokens = legalTokens[1:]
            exp()
            gen_inst("STDOUT", "NIL")
            if legalTokens[0][1] == ")":
                legalTokens = legalTokens[1:]
                if legalTokens[0][1] == ";":
                    legalTokens = legalTokens[1:]
                else:
                    raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
            else:
                raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [put]")


def scanGet():
    global legalTokens
    global getStack
    getStack = []
    if legalTokens[0][1] == "get":
        gen_inst("STDIN", "NIL")
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "(":
            legalTokens = legalTokens[1:]
            ids()
            for stack in getStack[::-1]:
                gen_inst("POPM", stack)
            if legalTokens[0][1] == ")":
                legalTokens = legalTokens[1:]
                if legalTokens[0][1] == ";":
                    legalTokens = legalTokens[1:]
                else:
                    raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
            else:
                raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [get]")

def condLoop():
    global legalTokens
    if legalTokens[0][1] == "while":
        addr = addressCounter
        gen_inst("LABEL", "NIL")
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "(":
            legalTokens = legalTokens[1:]
            cond()
            if legalTokens[0][1] == ")":
                legalTokens = legalTokens[1:]
                statement()
                gen_inst("JUMP", addr)
                backPatch(addressCounter)
            else:
                raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [While]")

def cond():
    global legalTokens
    global relatop
    global jumpStack
    exp()
    relop()
    exp()
    if relatop[1] == "==":
        gen_inst("EQU", "NIL")
        jumpStack.append(addressCounter)
        gen_inst("JUMPZ", "NIL")
    elif relatop[1] == "!=":
        gen_inst("NEQ", "NIL")
        jumpStack.append(addressCounter)
        gen_inst("JUMPZ", "NIL")
    elif relatop[1] == ">":
        gen_inst("GRT", "NIL")
        jumpStack.append(addressCounter)
        gen_inst("JUMPZ", "NIL")
    elif relatop[1] == "<":
        gen_inst("LES", "NIL")
        jumpStack.append(addressCounter)
        gen_inst("JUMPZ", "NIL")
    elif relatop[1] == "<=":
        gen_inst("LEQ", "NIL")
        jumpStack.append(addressCounter)
        gen_inst("JUMPZ", "NIL")
    elif relatop[1] == "=>":
        gen_inst("GEQ", "NIL")
        jumpStack.append(addressCounter)
        gen_inst("JUMPZ", "NIL")



def relop():
    global legalTokens
    global relatop
    if (
        legalTokens[0][1] == "=="
        or legalTokens[0][1] == "!="
        or legalTokens[0][1] == ">"
        or legalTokens[0][1] == "<"
        or legalTokens[0][1] == "<="
        or legalTokens[0][1] == "=>"
    ):
        relatop = legalTokens[0]
        legalTokens = legalTokens[1:]
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Relop>")

def exp():
    global legalTokens
    term()
    expPrime()

def expPrime():
    global legalTokens
    if legalTokens[0][1] == "+":
        legalTokens = legalTokens[1:]
        term()
        gen_inst("ADD", "NIL")
        expPrime()
    elif legalTokens[0][1] == "-":
        legalTokens = legalTokens[1:]
        term()
        gen_inst("SUB", "NIL")
        expPrime()
    else:
        empty()


def term():
    global legalTokens
    factor()
    termPrime()

def termPrime():
    global legalTokens
    if legalTokens[0][1] == "*":
        legalTokens = legalTokens[1:]
        factor()
        gen_inst("MUL", "NIL")
        termPrime()
    elif legalTokens[0][1] == "/":
        legalTokens = legalTokens[1:]
        factor()
        gen_inst("DIV", "NIL")
        termPrime()
    else:
        empty()


def factor():
    global legalTokens
    if legalTokens[0][1] == "-":
        legalTokens = legalTokens[1:]
    if legalTokens[0][0] == STATE_INT:
        gen_inst("PUSHI", legalTokens[0][1])
    else:
        gen_inst("PUSHM", get_address(legalTokens[0]))
    primary()


def primary():
    global legalTokens
    if legalTokens[0][0] == STATE_IDENTIFIER:
        legalTokens = legalTokens[1:]
        primaryPrime()
    elif legalTokens[0][0] == STATE_INT:
        legalTokens = legalTokens[1:]
    elif legalTokens[0][0] == STATE_REAL:
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "true":
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "false":
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "(":
        legalTokens = legalTokens[1:]
        exp()
        if legalTokens[0][1] == ")":
            legalTokens = legalTokens[1:]
    else:
        raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Primary>")


def primaryPrime():
    global legalTokens
    if legalTokens[0][1] == "(":
        legalTokens = legalTokens[1:]
        ids()
        if legalTokens[0][1] == ")":
            legalTokens = legalTokens[1:]
        else:
            raise Exception(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
    else:
        empty()


def empty():
    global legalTokens
    return None


if __name__ == "__main__":
    state = True
    while state:
        source = input("Please enter file name or Return 1 to finish.\n")
        print()
        if source == "1":
            state = False
            break
        t = getText(source)
        f = removeComments(t)
        global queuedTextpi
        global legalTokens
        global instructionTable
        global symbolTable
        global jumpStack
        global lineCounter
        global memoryCounter
        global addressCounter
        global getStack
        queuedText = spaceOpsandSeps(f)
        getStack = []
        addressCounter = 1
        legalTokens = []
        illegalTokens = []
        symbolTable = {
            "ident": [],
            "mem": [],
            "type": []
        }
        jumpStack = []
        instructionTable = []
        lineCounter = 1
        memoryCounter = 5000
        while len(queuedText) > 0:
            t = lexer()
            if t is not None:
                if t[0] == STATE_ERROR:
                    illegalTokens.append([t[0], t[1], lineCounter])
                else:
                    legalTokens.append([t[0], t[1], lineCounter])
        if len(illegalTokens) != 0:
            for i in illegalTokens:
                print(f"Unrecognized Token: {i[1]}, {i[2]}\n")
            break
        rat22f()
        for row in instructionTable:
            if row[2] != "NIL":
                print(f"{row[0]}:\t{row[1]}\t{row[2]}")
                outFile.write(f"{row[1]} {row[2]}\n")
            else:
                print(f"{row[0]}:\t{row[1]}")
                outFile.write(f"{row[1]}\n")
        print()
        outFile.close()
