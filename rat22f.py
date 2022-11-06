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


def rat22f():
    global legalTokens
    if legalTokens[0][1] == "function":
        optFuncDefs()
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Rat22F>  ::=   <Opt Function Definitions>   $  <Opt Declaration List>  <Statement List>  $")
    if legalTokens[0][1] == "$":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Rat22F>  ::=   <Opt Function Definitions>   $  <Opt Declaration List>  <Statement List>  $")
        legalTokens = legalTokens[1:]
        optDecList()
        stateList()
        if legalTokens[0][1] == "$":
            empty()
            outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Rat22F>  ::=   <Opt Function Definitions>   $  <Opt Declaration List>  <Statement List>  $")
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected $")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected $")


def optFuncDefs():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Opt Function Definitions> ::= <Function Definitions>  |  <Empty>")
    funcDefs()


def funcDefs():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Function Definitions>  ::= <Function>  <Function Definitions’>")
    func()
    funcDefsPrime()


def funcDefsPrime():
    global legalTokens
    if legalTokens[0][1] == "function":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Function Definitions’> ::= <Functions Definitions>")
        funcDefs()
    else:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Function Definitions’> ::= <Empty>")
        empty()

def func():
    global legalTokens
    if legalTokens[0][1] == "function":
        legalTokens = legalTokens[1:]
    else:
        return empty()
    if legalTokens[0][0] == STATE_IDENTIFIER:
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "(":
            legalTokens = legalTokens[1:]
            if legalTokens[0][1] != ")":
                outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Opt Parameter List> ::=  <Parameter List>  |   <Empty>")
                paramList()
            if legalTokens[0][1] == ")":
                legalTokens = legalTokens[1:]
                if legalTokens[0][1] != "{":
                    decList()
                if legalTokens[0][1] == "{":
                    body()
                    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Function> ::= function  <Identifier>   ( <Opt Parameter List> )  <Opt Declaration List>  <Body>")
                else:
                    outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'{'}")
            else:
                outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Identifier>")

def paramList():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Parameter List>  ::=  <Parameter><Parameter List’>")
    param()
    paramListPrime()


def paramListPrime():
    global legalTokens
    if legalTokens[0][1] == ",":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Parameter List’> ::= <Parameter List>")
        legalTokens = legalTokens[1:]
        paramList()
    else:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Parameter List’> ::= <Empty>")
        empty()


def param():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Parameter> ::=  <IDs >  <Qualifier>")
    ids()
    qual()


def qual():
    global legalTokens
    if legalTokens[0][1] == "boolean":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Qualifier> ::= boolean")
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "integer":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Qualifier> ::= integer")
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "real":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Qualifier> ::= real")
        legalTokens = legalTokens[1:]
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Qualifier>")


def body():
    global legalTokens
    if legalTokens[0][1] == "{":
        legalTokens = legalTokens[1:]
        stateList()
        if legalTokens[0][1] == "}":
            outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Body>  ::=  {'{'}  < Statement List>  {'}'}")
            legalTokens = legalTokens[1:]
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'}'}")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'{'}")


def optDecList():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Opt Function Definitions> ::= <Function Definitions>")
    decList()
    


def decList():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Declaration List> ::= <Declaration> ; <Declaration List’>")
    dec()
    if legalTokens[0][1] == ";":
        legalTokens = legalTokens[1:]
        decListPrime()
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")


def decListPrime():
    global legalTokens
    if (
        legalTokens[0][1] == "integer"
        or legalTokens[0][1] == "boolean"
        or legalTokens[0][1] == "real"
    ):
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Declaration List’> ::= <Declaration List>")
        decList()
    else:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Declaration List’> ::= <Empty>")
        empty()


def dec():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Declaration> ::=   <Qualifier > <IDs> ")
    qual()
    ids()


def ids():
    global legalTokens
    if legalTokens[0][0] == STATE_IDENTIFIER:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <IDs> ::= 	<Identifier><IDs’>")
        legalTokens = legalTokens[1:]
        idsPrime()
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Identifier>")


def idsPrime():
    global legalTokens
    if legalTokens[0][1] == ",":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <IDs’> ::= ,<IDs>")
        legalTokens = legalTokens[1:]
        ids()
    else:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <IDs’> ::= <Empty>")
        empty()


def stateList():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement List> ::=   <Statement><Statement List’>")
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
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement List’> ::=  <Statement List>")
        statement()
    else:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement List’> ::=  <Empty>")
        empty()


def statement():
    global legalTokens
    if legalTokens[0][1] == "{":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement> ::=   <Compound> ")
        comp()
    elif legalTokens[0][0] == STATE_IDENTIFIER:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement> ::=   <Assign> ")
        assign()
    elif legalTokens[0][1] == "if":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement> ::=   <If> ")
        implication()
    elif legalTokens[0][1] == "return":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement> ::=   <Return> ")
        ret()
    elif legalTokens[0][1] == "put":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement> ::=   <Print> ")
        printPut()
    elif legalTokens[0][1] == "get":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement> ::=   <Scan> ")
        scanGet()
    elif legalTokens[0][1] == "while":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Statement> ::=   <While> ")
        condLoop()
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Statement>")


def comp():
    global legalTokens
    if legalTokens[0][1] == "{":
        legalTokens = legalTokens[1:]
        stateList()
        if legalTokens[0][1] == "}":
            outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Compound> ::=   {'{'}  <Statement List>  {'}'}")
            legalTokens = legalTokens[1:]
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'}'}")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected {'{'}")


def assign():
    global legalTokens
    if legalTokens[0][0] == STATE_IDENTIFIER:
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "=":
            legalTokens = legalTokens[1:]
            exp()
            if legalTokens[0][1] == ";":
                outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Assign> ::= <Identifier> = <Expression> ;")
                legalTokens = legalTokens[1:]
                stateListPrime()
            else:
                outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected =")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Identifier>")
			


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
                implicationPrime()
                if legalTokens[0][1] == "endif":
                    legalTokens = legalTokens[1:]
                    if legalTokens[0][1] == ';':
                        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <If> ::=     if  ( <Condition>  ) <Statement><If ’> endif;")
                        legalTokens = legalTokens[1:]
                    else:
                        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
                else:
                    outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [endif]")
            else:
                outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [if]")


def implicationPrime():
    global legalTokens
    if legalTokens[0][1] == "else":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <If’> ::= else  <Statement>")
        legalTokens = legalTokens[1:]
        statement()
    elif legalTokens[0][1] == "endif":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <If’> ::= <Empty>")
        empty()
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected else <statement> or endif")


def ret():
    global legalTokens
    if legalTokens[0][1] == "return":
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] != ";":
            outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Return> ::=  return<Return’>")
            retPrime()
        if legalTokens[0][1] == ";":
            outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Return’> ::= <Empty>")
            legalTokens = legalTokens[1:]
            empty()
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Return>")


def retPrime():
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Return’> ::= <Expression>")
    exp()


def printPut():
    global legalTokens
    if legalTokens[0][1] == "put":
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "(":
            legalTokens = legalTokens[1:]
            exp()
            if legalTokens[0][1] == ")":
                legalTokens = legalTokens[1:]
                if legalTokens[0][1] == ";":
                    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Print> ::=	put ( <Expression>);")
                    legalTokens = legalTokens[1:]
                else:
                    outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
            else:
                outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [put]")


def scanGet():
    global legalTokens
    if legalTokens[0][1] == "get":
        legalTokens = legalTokens[1:]
        if legalTokens[0][1] == "(":
            legalTokens = legalTokens[1:]
            ids()
            if legalTokens[0][1] == ")":
                legalTokens = legalTokens[1:]
                if legalTokens[0][1] == ";":
                    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Print> ::=	get ( <IDs>);")
                    legalTokens = legalTokens[1:]
                else:
                    outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected ;")
            else:
                outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [get]")

def condLoop():
    global legalTokens
    if legalTokens[0][1] == "while":
        legalTokens = legalTokens[1:]
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <While> ::=  while ( <Condition>  )  <Statement> ")
        if legalTokens[0][1] == "(":
            legalTokens = legalTokens[1:]
            cond()
            if legalTokens[0][1] == ")":
                legalTokens = legalTokens[1:]
                statement()
                outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <While> ::=  while ( <Condition>  )  <Statement> ")
            else:
                outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected (")
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected [While]")

def cond():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Condition> ::= 	<Expression>  <Relop>   <Expression>")
    exp()
    relop()
    exp()



def relop():
    global legalTokens
    if (
        legalTokens[0][1] == "=="
        or legalTokens[0][1] == "!="
        or legalTokens[0][1] == ">"
        or legalTokens[0][1] == "<"
        or legalTokens[0][1] == "<="
        or legalTokens[0][1] == "=>"
    ):
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Relop> ::=    	==   |   !=	|   > 	|   <	|  <=   |	=>")
        legalTokens = legalTokens[1:]
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Relop>")


def exp():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Expression>  ::= <Term><Expression’>")
    term()
    expPrime()


def expPrime():
    global legalTokens
    if legalTokens[0][1] == "+":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Expression’> ::= +<Term><Expression’>")
        legalTokens = legalTokens[1:]
        term()
        expPrime()
    elif legalTokens[0][1] == "-":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Expression’> ::= -<Term><Expression’>")
        legalTokens = legalTokens[1:]
        term()
        expPrime()
    else:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Expression’> ::= <Empty>")
        empty()


def term():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Term>  ::= <Factor><Term’>")
    factor()
    termPrime()


def termPrime():
    global legalTokens
    if legalTokens[0][1] == "*":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Term’> ::= *<Factor><Term’>")
        legalTokens = legalTokens[1:]
        factor()
        termPrime()
    elif legalTokens[0][1] == "/":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Term’> ::= /<Factor><Term’>")
        legalTokens = legalTokens[1:]
        factor()
        termPrime()
    else:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Term’> ::= <Empty>")
        empty()


def factor():
    global legalTokens
    if legalTokens[0][1] == "-":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Factor> ::= -  <Primary>")
        legalTokens = legalTokens[1:]
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Factor> ::= <Primary>")
    primary()


def primary():
    global legalTokens
    if legalTokens[0][0] == STATE_IDENTIFIER:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Primary> ::=  <Identifier> <Primary’>")
        legalTokens = legalTokens[1:]
        primaryPrime()
    elif legalTokens[0][0] == STATE_INT:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Primary> ::=  <Integer>")
        legalTokens = legalTokens[1:]
    elif legalTokens[0][0] == STATE_REAL:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Primary> ::=  <Integer>")
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "true":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Primary> ::=  true")
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "false":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Primary> ::=  false")
        legalTokens = legalTokens[1:]
    elif legalTokens[0][1] == "(":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Primary> ::=   ( <Expression> ) ")
        legalTokens = legalTokens[1:]
        exp()
        if legalTokens[0][1] == ")":
            legalTokens = legalTokens[1:]
    else:
        outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected <Primary>")


def primaryPrime():
    global legalTokens
    if legalTokens[0][1] == "(":
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Primary’> ::= (<IDs>)")
        legalTokens = legalTokens[1:]
        ids()
        if legalTokens[0][1] == ")":
            legalTokens = legalTokens[1:]
        else:
            outFile.write(f"\nGot: Lexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t, Expected )")
    else:
        outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Primary’> ::= <Empty>")
        empty()


def empty():
    global legalTokens
    outFile.write(f"\nLexeme - {legalTokens[0][1]}, Line - {legalTokens[0][2]}:\n\t <Empty>   ::= <Empty>")
    return None


if __name__ == "__main__":
    state = True
    while state:
        source = input("Please enter file name or Return 1 to finish.\n")
        if source == "1":
            state = False
            break
        t = getText(source)
        f = removeComments(t)
        global queuedTextpi
        queuedText = spaceOpsandSeps(f)
        global legalTokens
        global lineCounter
        legalTokens = []
        illegalTokens = []
        lineCounter = 1
        while len(queuedText) > 0:
            t = lexer()
            if t is not None:
                if t[0] == STATE_ERROR:
                    illegalTokens.append([t[0], t[1], lineCounter])
                else:
                    legalTokens.append([t[0], t[1], lineCounter])
        if len(illegalTokens) != 0:
            for i in illegalTokens:
                outFile.write(f"Unrecognized Token: {i[1]}, {i[2]}\n")
            break
        print("\n")
        rat22f()
        outFile.close()
