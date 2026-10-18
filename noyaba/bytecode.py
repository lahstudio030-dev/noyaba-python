from dataclasses import dataclass
from enum import Enum, auto

class Op(Enum):
    CONST=auto(); LOAD=auto(); STORE=auto(); LOAD_GLOBAL=auto(); STORE_GLOBAL=auto()
    POP=auto(); ADD=auto(); SUB=auto(); MUL=auto(); DIV=auto(); MOD=auto(); POW=auto()
    EQ=auto(); NE=auto(); LT=auto(); LE=auto(); GT=auto(); GE=auto(); IN=auto(); NOT_IN=auto(); AND=auto(); OR=auto(); NOT=auto()
    BIT_AND=auto(); BIT_OR=auto(); BIT_XOR=auto(); SHL=auto(); SHR=auto(); BIT_NOT=auto(); NEG=auto()
    JUMP=auto(); JUMP_IF_TRUE=auto(); JUMP_IF_FALSE=auto(); JUMP_IF_TRUE_KEEP=auto(); JUMP_IF_FALSE_KEEP=auto(); SHORT_OR=auto(); CALL=auto(); RETURN=auto(); HALT=auto()
    CREATE_REF=auto(); LOAD_REF=auto(); STORE_REF=auto(); CREATE_STRUCT=auto(); GET_ATTR=auto(); SET_ATTR=auto()
    GET_ITEM=auto(); SET_ITEM=auto(); CREATE_SLICE=auto(); AUG_ADD=auto(); CREATE_LIST=auto(); CREATE_ARRAY=auto(); CREATE_ENV=auto(); DESTROY_ENV=auto()
    RAISE=auto(); SETUP_EXCEPTION=auto(); POP_EXCEPTION=auto(); IMPORT=auto(); VIEW=auto(); INPUT=auto(); NOP=auto(); CREATE_DOBJECT=auto()

@dataclass(frozen=True)
class Instruction:
    op: Op
    arg: object = None
    line: int = 0

@dataclass
class Chunk:
    name: str = "<module>"
    code: list = None
    constants: list = None
    params: list = None
    locals: list = None
    labels: dict = None
    def __post_init__(self):
        self.code = [] if self.code is None else self.code
        self.constants = [] if self.constants is None else self.constants
        self.params = [] if self.params is None else self.params
        self.locals = [] if self.locals is None else self.locals
        self.labels = {} if self.labels is None else self.labels
    def const(self, x):
        self.constants.append(x); return len(self.constants)-1
    def emit(self, op, arg=None, line=0):
        self.code.append(Instruction(op,arg,line)); return len(self.code)-1
    def patch(self, at, arg): self.code[at] = Instruction(self.code[at].op,arg,self.code[at].line)
