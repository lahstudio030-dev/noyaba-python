from .parser import *
from .bytecode import Chunk,Op
from .runtime import TypeError_
import copy
class Compiler:
 def __init__(self): self.chunk=Chunk(); self.labels={}; self.pending=[]; self.macros={}; self.macro_stack=[]; self.loop_stack=[]
 def emit(self,op,arg=None): return self.chunk.emit(op,arg,getattr(self,'current_line',0))
 def compile(self,node):
  if isinstance(node,Block):
   self.macros={x.name:x for x in node.xs if isinstance(x,Macro)}
  if isinstance(node,Block):
   for x in node.xs:self.s(x)
  else:self.s(node)
  return self.chunk
 def s(self,n):
  c=self.chunk
  self.current_line=getattr(n,'line',0)
  if isinstance(n,Block):
   for x in n.xs:self.s(x)
  elif isinstance(n,ExprStmt):self.e(n.x); self.emit(Op.POP)
  elif isinstance(n,Macro): pass
  elif isinstance(n,Assign):
   if n.ref and isinstance(n.value,Var): self.emit(Op.CREATE_REF,n.value.name)
   else: self.e(n.value)
   if isinstance(n.target,Var): self.emit(Op.STORE,(n.target.name,n.decl,n.frozen,n.ref))
   elif isinstance(n.target,Attr): self.e(n.target.o); self.emit(Op.SET_ATTR,n.target.name)
   elif isinstance(n.target,Index): self.e(n.target.o);self.e(n.target.i);self.emit(Op.SET_ITEM)
  elif isinstance(n,AugAssign):
   ops={'+':Op.ADD,'-':Op.SUB,'*':Op.MUL,'/':Op.DIV,'%':Op.MOD,'**':Op.POW,'&':Op.BIT_AND,'|':Op.BIT_OR,'^':Op.BIT_XOR,'<<':Op.SHL,'>>':Op.SHR}
   if n.op not in ops: raise SyntaxError(f'unsupported augmented operator: {n.op}=')
   if isinstance(n.target,Var):
    self.emit(Op.LOAD,n.target.name); self.e(n.value); self.emit(Op.AUG_ADD if n.op=='+' else ops[n.op]); self.emit(Op.STORE,(n.target.name,None,False,False))
   elif isinstance(n.target,Attr):
    self.e(n.target.o); self.emit(Op.GET_ATTR,n.target.name); self.e(n.value); self.emit(Op.AUG_ADD if n.op=='+' else ops[n.op]); self.e(n.target.o); self.emit(Op.SET_ATTR,n.target.name)
   elif isinstance(n.target,Index):
    self.e(n.target.o); self.e(n.target.i); self.emit(Op.GET_ITEM); self.e(n.value); self.emit(Op.AUG_ADD if n.op=='+' else ops[n.op]); self.e(n.target.o); self.e(n.target.i); self.emit(Op.SET_ITEM)
  elif isinstance(n,Return):self.e(n.x);self.emit(Op.RETURN)
  elif isinstance(n,Func):
   sub=Compiler(); sub.compile(n.body); sub.chunk.params=[p.name for p in n.params]; sub.chunk.param_specs=n.params; sub.chunk.name=n.name; sub.chunk.emit(Op.CONST,sub.chunk.const(None));sub.chunk.emit(Op.RETURN); idx=c.const(sub.chunk);self.emit(Op.CONST,idx);self.emit(Op.STORE,(n.name,None,False,False))
  elif isinstance(n,If):
   ends=[]
   for cond,b in n.branches:
    self.e(cond); j=self.emit(Op.JUMP_IF_FALSE,None);self.s(b);ends.append(self.emit(Op.JUMP,None));c.patch(j,len(c.code))
   if n.other:self.s(n.other)
   for z in ends:c.patch(z,len(c.code))
  elif isinstance(n,Trigger):
   self.e(n.value); self.emit(Op.STORE,('__trigger_value',None,False,False)); exits=[]
   seen=set()
   for case in n.cases:
    tests=[]
    for val in case.values:
     if isinstance(val,Lit) and repr(val.v) in seen: raise SyntaxError('duplicate constant trigger case')
     if isinstance(val,Lit): seen.add(repr(val.v))
     if isinstance(val,Bin) and val.op in ('==','!=','<','<=','>','>='):
      self.e(val)
     else:
      self.emit(Op.LOAD,'__trigger_value'); self.e(val); tests.append(self.emit(Op.EQ));
    # each test leaves bool; combine by OR for multiple values
    for _ in range(max(0,len(tests)-1)): self.emit(Op.OR)
    j=self.emit(Op.JUMP_IF_FALSE,None); self.s(case.body); exits.append(self.emit(Op.JUMP,None)); c.patch(j,len(c.code))
   if n.default:self.s(n.default)
   for z in exits:c.patch(z,len(c.code))
  elif isinstance(n,While):
   start=len(c.code);self.e(n.cond);j=self.emit(Op.JUMP_IF_FALSE,None);ctx={'continue':start,'breaks':[]};self.loop_stack.append(ctx);self.s(n.body);self.loop_stack.pop();self.emit(Op.JUMP,start);c.patch(j,len(c.code))
   for z in ctx['breaks']: c.patch(z,len(c.code))
  elif isinstance(n,For):
   # lower for to builtin iterator protocol through hidden names
   self.e(n.seq); self.emit(Op.STORE,('__for_seq',None,False,False)); self.emit(Op.CONST,c.const(0)); self.emit(Op.STORE,('__for_i',None,False,False)); start=len(c.code)
   self.emit(Op.LOAD,'__for_i'); self.emit(Op.LOAD,'len'); self.emit(Op.LOAD,'__for_seq'); self.emit(Op.CALL,1); self.emit(Op.LT); j=self.emit(Op.JUMP_IF_FALSE,None)
   self.emit(Op.LOAD,'__for_seq');self.emit(Op.LOAD,'__for_i');self.emit(Op.GET_ITEM);self.emit(Op.STORE,(n.name,None,False,False));ctx={'continue':None,'continues':[],'breaks':[]};self.loop_stack.append(ctx);self.s(n.body);self.loop_stack.pop();ctx['continue']=len(c.code);self.emit(Op.LOAD,'__for_i');self.emit(Op.CONST,c.const(1));self.emit(Op.ADD);self.emit(Op.STORE,('__for_i',None,False,False));self.emit(Op.JUMP,start);c.patch(j,len(c.code))
   for z in ctx['continues']: c.patch(z,ctx['continue'])
   for z in ctx['breaks']: c.patch(z,len(c.code))
  elif isinstance(n,Break):
   if not self.loop_stack: raise SyntaxError('break outside loop')
   self.loop_stack[-1]['breaks'].append(self.emit(Op.JUMP,None))
  elif isinstance(n,Continue):
   if not self.loop_stack: raise SyntaxError('continue outside loop')
   target=self.loop_stack[-1]['continue']; self.loop_stack[-1].setdefault('continues',[]).append(self.emit(Op.JUMP,target))
  elif isinstance(n,With):
   if n.name is None:self.emit(Op.CREATE_ENV);self.s(n.body);self.emit(Op.DESTROY_ENV)
   else:
    sub=Compiler();sub.compile(n.body);sub.chunk.name=n.name;sub.chunk.emit(Op.CONST,sub.chunk.const(None));sub.chunk.emit(Op.RETURN);idx=c.const(sub.chunk);self.emit(Op.CONST,idx);self.emit(Op.STORE,(n.name,None,False,False))
  elif isinstance(n,Goto): self.emit(Op.JUMP,('label',n.name))
  elif isinstance(n,Label): c.labels[n.name]=len(c.code)
  elif isinstance(n,Raise):self.e(n.x);self.emit(Op.RAISE)
  elif isinstance(n,Try):
   setup=self.emit(Op.SETUP_EXCEPTION,None);self.s(n.body);self.emit(Op.POP_EXCEPTION);j=self.emit(Op.JUMP,None); specs=[]
   for ex in n.catches:
    specs.append([len(c.code),ex.typ,ex.name]); self.s(ex.body)
   c.patch(setup,specs)
   c.patch(j,len(c.code))
  elif isinstance(n,ClassN):
   methods={}; fields={}; field_types={}
   for item in n.body.xs:
    if isinstance(item,Func):
     sub=Compiler(); sub.compile(item.body); sub.chunk.params=[p.name for p in item.params]; sub.chunk.param_specs=item.params; sub.chunk.name=item.name; sub.chunk.emit(Op.CONST,sub.chunk.const(None)); sub.chunk.emit(Op.RETURN); methods[item.name]=sub.chunk
    elif isinstance(item,ExprStmt) and isinstance(item.x,Var): fields[item.x.name]=None
    elif isinstance(item,Assign) and isinstance(item.target,Var):
     fields[item.target.name]=item.value
     if item.decl: field_types[item.target.name]=item.decl
   desc={'name':n.name,'fields':fields,'field_types':field_types,'methods':methods,'base':n.base}
   self.emit(Op.LOAD,'__class__'); self.emit(Op.CONST,c.const(desc));
   if n.base:self.emit(Op.LOAD,n.base)
   else:self.emit(Op.CONST,c.const(None))
   self.emit(Op.CALL,2); self.emit(Op.STORE,(n.name,None,False,False))
  elif isinstance(n,StructDef):
   fields={name:(typ,default) for name,typ,default in n.fields}; self.emit(Op.LOAD,'__fixed_struct__'); self.emit(Op.CONST,c.const(fields)); self.emit(Op.CONST,c.const(n.name)); self.emit(Op.CALL,2); self.emit(Op.STORE,(n.name,None,False,False))
  elif isinstance(n,Import): self.emit(Op.IMPORT,(n.module,n.names))
 def e(self,n):
  c=self.chunk
  if isinstance(n,Lit):self.emit(Op.CONST,c.const(n.v))
  elif isinstance(n,Var):self.emit(Op.LOAD,n.name)
  elif isinstance(n,ListN):
   for x in n.xs:self.e(x)
   self.emit(Op.CREATE_ARRAY,len(n.xs))
  elif isinstance(n,DictN):
   typed=any(isinstance(e,DictEntry) and e.typ for e in n.xs)
   for e in n.xs:
    k,v=(e.key,e.value) if isinstance(e,DictEntry) else e
    self.emit(Op.CONST,c.const(k));self.e(v)
   if typed:
    schema={e.key:e.typ for e in n.xs if isinstance(e,DictEntry) and e.typ}
    self.emit(Op.CONST,c.const(schema));self.emit(Op.CREATE_DOBJECT,len(n.xs))
   else:self.emit(Op.CREATE_STRUCT,len(n.xs))
  elif isinstance(n,Chain):
   temp=f'__chain_value_{len(c.code)}'; next_temp=f'__chain_next_{len(c.code)}'; false_jumps=[]
   self.e(n.terms[0]); self.emit(Op.STORE,(temp,None,False,False))
   for i,op in enumerate(n.ops):
    self.e(n.terms[i+1]); self.emit(Op.STORE,(next_temp,None,False,False)); self.emit(Op.LOAD,temp); self.emit(Op.LOAD,next_temp); self.emit({'==':Op.EQ,'!=':Op.NE,'in':Op.IN,'not in':Op.NOT_IN,'<':Op.LT,'<=':Op.LE,'>':Op.GT,'>=':Op.GE}[op])
    if i<len(n.ops)-1:
     false_jumps.append(self.emit(Op.JUMP_IF_FALSE,None)); self.emit(Op.LOAD,next_temp); self.emit(Op.STORE,(temp,None,False,False))
   end=self.emit(Op.JUMP,None); false_at=len(c.code); self.emit(Op.CONST,c.const(False)); end_at=len(c.code); c.patch(end,end_at)
   for jump in false_jumps:c.patch(jump,false_at)
  elif isinstance(n,Bin):
   if n.op in ('and','&&','or'):
    self.e(n.a); self.emit(Op.NOT); self.emit(Op.NOT)
    jump=self.emit(Op.JUMP_IF_FALSE_KEEP if n.op in ('and','&&') else Op.JUMP_IF_TRUE_KEEP,None)
    self.emit(Op.POP); self.e(n.b); self.emit(Op.NOT); self.emit(Op.NOT)
    end=self.emit(Op.JUMP,None); c.patch(jump,len(c.code)); c.patch(end,len(c.code))
   elif n.op=='||':
    self.e(n.a); jump=self.emit(Op.SHORT_OR,None); self.e(n.b); self.emit(Op.OR); c.patch(jump,len(c.code))
   else:
    self.e(n.a);self.e(n.b);self.emit({'+' :Op.ADD,'-':Op.SUB,'*':Op.MUL,'/':Op.DIV,'%':Op.MOD,'**':Op.POW,'==':Op.EQ,'!=':Op.NE,'<':Op.LT,'<=':Op.LE,'>':Op.GT,'>=':Op.GE,'in':Op.IN,'not in':Op.NOT_IN,'&':Op.BIT_AND,'|':Op.BIT_OR,'^':Op.BIT_XOR,'<<':Op.SHL,'>>':Op.SHR}[n.op])
  elif isinstance(n,Unary):self.e(n.x);self.emit({'-':Op.NEG,'!':Op.NOT,'not':Op.NOT,'+':Op.NOP,'~':Op.BIT_NOT}[n.op])
  elif isinstance(n,Call):
   if isinstance(n.f,Var) and n.f.name in self.macros:
    if n.f.name in self.macro_stack: raise SyntaxError('recursive macro expansion')
    m=self.macros[n.f.name]
    if len(m.params)!=len(n.args): raise TypeError_('macro argument count mismatch')
    x=copy.deepcopy(m.body)
    def sub(z):
     if isinstance(z,Var) and z.name in dict(zip(m.params,n.args)): return copy.deepcopy(dict(zip(m.params,n.args))[z.name])
     for name,val in vars(z).items():
      if isinstance(val,N): setattr(z,name,sub(val))
      elif isinstance(val,list): setattr(z,name,[sub(q) if isinstance(q,N) else q for q in val])
     return z
    self.macro_stack.append(n.f.name)
    try:self.e(sub(x))
    finally:self.macro_stack.pop()
    return
   self.e(n.f)
   for a in n.args:self.e(a)
   self.emit(Op.CALL,len(n.args))
  elif isinstance(n,Attr):self.e(n.o);self.emit(Op.GET_ATTR,n.name)
  elif isinstance(n,Index):self.e(n.o);self.e(n.i);self.emit(Op.GET_ITEM)
  elif isinstance(n,SliceN):
   for part in (n.start,n.stop,n.step):
    self.e(part if part is not None else Lit(None))
   self.emit(Op.CREATE_SLICE,3)
