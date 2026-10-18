# Noyaba Bytecode v1 stack effects

`S` is the value stack. `args` are instruction operands, not Python call-stack values.

| Opcode | Stack before | Stack after | Purpose |
|---|---|---|---|
| CONST/LOAD | `S` | `S,v` | push constant or binding |
| STORE | `S,v` | `S` | write binding cell |
| ADD/SUB/MUL/DIV/MOD/POW | `S,a,b` | `S,r` | numeric operator dispatch |
| EQ/NE/LT/LE/GT/GE | `S,a,b` | `S,bool` | comparison |
| AND/OR | `S,a,b` | `S,bool` | logical operation |
| NOT/NEG | `S,a` | `S,r` | unary operation |
| BIT_AND/BIT_OR/BIT_XOR/SHL/SHR | `S,a,b` | `S,r` | integer bit operation |
| JUMP | `S` | `S` | set IP to instruction boundary |
| JUMP_IF_TRUE/FALSE | `S,bool` | `S` | conditional branch |
| CALL(n) | `S,fn,a1..an` | `S,result` | invoke native or Noyaba function |
| RETURN | `S,result` | caller `S,result` | restore frame |
| CREATE_REF | `S` | `S,ref` | reference to binding cell |
| LOAD_REF/STORE_REF | `S,ref` / `S,ref,v` | `S,v` / `S` | reference access (compiler may lower through STORE) |
| CREATE_STRUCT(n) | `S,k1,v1..kn,vn` | `S,object` | dynamic/fixed object |
| GET_ATTR/SET_ATTR | `S,obj` / `S,v,obj` | `S,v` / `S` | central attribute dispatch |
| GET_ITEM/SET_ITEM | `S,obj,i` / `S,v,obj,i` | `S,v` / `S` | indexed access |
| CREATE_LIST/CREATE_ARRAY | `S,v1..vn` | `S,sequence` | sequence construction |
| CREATE_ENV/DESTROY_ENV | `S` | `S` | explicit temporary scope lifetime |
| RAISE | `S,error` | handler/unwind | raise CenterError |
| SETUP_EXCEPTION/POP_EXCEPTION | `S` | `S` | handler registration/removal |
| IMPORT | `S` | `S` | module loading boundary |
| VIEW/INPUT | `S,args` | `S,result` | registered I/O builtins |
| HALT | `S` | `S` | stop execution |

The prototype uses dataclass instructions rather than a packed byte array. `BYTECODE_VERSION = 1`; an incompatible encoding must increment it.
