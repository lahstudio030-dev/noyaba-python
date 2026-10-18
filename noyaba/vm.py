import operator, os, hashlib
from .bytecode import Op
from .parser import parse,Lit
from .compiler import Compiler
from .runtime import *
class Native:
 def __init__(self,fn,name):self.fn=fn;self.name=name
 def __call__(self,args,vm):
  try:return wrap(self.fn(*args))
  except CenterError:raise
  except TypeError as e:raise TypeError_(str(e)) from e
  except ValueError as e:raise ValueError_(str(e)) from e
  except (IndexError,KeyError) as e:raise IndexError_(str(e)) from e
  except OSError as e:raise OsError(str(e)) from e
class Frame:
 def __init__(self,fn,env,filename=None):self.function=fn;self.env=env;self.ip=0;self.filename=filename
class VM:
 def __init__(self,project_root=None,module_paths=None):
  self.heap=Heap();self.globals=Environment(name='<global>');self.stack=[];self.call_stack=[];self.current_frame=None;self.modules={};self.exception_state=None;self.running=True;self.output=[];self.project_root=os.path.abspath(project_root or os.getcwd());self.module_paths=list(module_paths or []);self._builtins()
 def _builtins(self):
  def put(n,fn):self.globals.define(n,Native(fn,n))
  put('view',lambda *a:self._view(*a));put('print',lambda *a:self._view(*a));put('int',self._cast_int);put('float',self._cast_float);put('str',self._cast_str);put('repr',self._cast_repr);put('bool',self._cast_bool);put('len',self._builtin_len);put('__len__',self._builtin_len)
  put('abs',self._builtin_abs);put('max',self._builtin_max);put('min',self._builtin_min);put('pow',self._builtin_pow);put('typeof',self._builtin_typeof)
  put('count',self._builtin_count);put('enumerate',self._builtin_enumerate);put('zip',self._builtin_zip);put('stepview',self._builtin_stepview)
  put('binary',self._builtin_binary);put('hash',self._builtin_hash);put('bitfix',self._builtin_bitfix)
  put('execute',self._builtin_execute);put('eval',self._builtin_math_expression);put('open',self._builtin_open);put('object',lambda:RootObject())
  put('struct',self._builtin_struct)
  put('__class__',lambda d,b=None:self._make_class(d,b,self.current_frame.env if self.current_frame else self.globals))
  put('__fixed_struct__',lambda d,n:FixedStructType(unwrap(n),d))
  put('__struct__',lambda d:StructObject(d.payload if isinstance(d,Value) else d));put('__cost__',lambda d:CostObject({k:wrap(v) for k,v in (d.payload if isinstance(d,Value) else d).items()},Value(Kind.INT,0)));put('__enum__',lambda d:EnumObject(d.payload if isinstance(d,Value) else d))
  put('freeze',lambda x:x);put('callable',self._builtin_callable);put('isinstance',self._builtin_isinstance);put('round',self._builtin_round);put('ord',self._builtin_ord);put('char',self._builtin_char);put('hex',self._builtin_hex);put('oct',self._builtin_oct);put('ascii',self._builtin_ascii);put('list',self._builtin_list);put('array',self._builtin_array);put('dobject',self._builtin_dobject);put('input',self._builtin_input)
 def register_native(self,adapter):
  if not isinstance(adapter,NativeAdapter): raise TypeError_('native registry requires NativeAdapter')
  self.globals.define(adapter.name,adapter); return adapter
 def _view(self,*a):
  s=' '.join(self._object_text(x) for x in a);self.output.append(s);print(s);return NULL
 def _object_text(self,x):
  obj=x.payload if isinstance(x,Value) else x
  if isinstance(obj,InstanceObject):
   for name in ('__str__','__repr__'):
    try:return str(unwrap(self._call(attr_get(obj,name),[])))
    except NameError_: pass
  if isinstance(x,Value) and x.kind is Kind.OBJECT and isinstance(x.payload,ExceptionObject): return str(x.payload.error)
  return str(x)
 def _cast_str(self,x): return wrap(self._object_text(x))
 def _cast_repr(self,x):
  obj=x.payload if isinstance(x,Value) else x
  if isinstance(obj,InstanceObject):
   for name in ('__repr__','__str__'):
    try:return wrap(str(unwrap(self._call(attr_get(obj,name),[]))))
    except NameError_: pass
  return wrap(str(x))
 def _cast_bool(self,x): return wrap(x.truthy() if isinstance(x,Value) else bool(x))
 def _builtin_typeof(self,x):
  if isinstance(x,Value) and x.kind is Kind.OBJECT and isinstance(x.payload,ExceptionObject): return wrap('EXCEPTION')
  if isinstance(x,Value): return wrap(x.kind.value)
  if isinstance(x,InstanceObject): return wrap('CLASS')
  if isinstance(x,ClassObject): return wrap('CLASS')
  if isinstance(x,Function) or isinstance(x,BoundMethod): return wrap('FUNCTION')
  if isinstance(x,Native): return wrap('NATIVE')
  if isinstance(x,EnumObject): return wrap('ENUM')
  if isinstance(x,RootObject): return wrap('OBJECT')
  if isinstance(x,FileObject): return wrap('FILE')
  if isinstance(x,ExceptionObject): return wrap('EXCEPTION')
  return wrap(type(x).__name__.upper())
 def _builtin_isinstance(self,x,t):
  name=t.name if isinstance(t,Native) else (t.payload if isinstance(t,Value) and t.kind is Kind.STRING else None)
  aliases={'int':'INT','float':'FLOAT','str':'STRING','bool':'BOOL','char':'CHAR','list':'LIST','array':'ARRAY'}
  if name == 'exception': return wrap(isinstance(x,ExceptionObject) or (isinstance(x,Value) and x.kind is Kind.OBJECT and isinstance(x.payload,ExceptionObject)))
  if isinstance(x,Value): return wrap(aliases.get(name,name) in {x.kind.value,x.kind.value.lower()})
  if name == 'object': return wrap(isinstance(x,RootObject))
  if isinstance(x,EnumObject): return wrap(name == 'enum')
  if isinstance(x,InstanceObject) and isinstance(t,ClassObject):
   c=x.cls
   while c:
    if c is t:return wrap(True)
    c=c.base
   return wrap(False)
  return wrap(False)
 def _builtin_callable(self,x): return wrap(isinstance(x,(Native,NativeAdapter,Function,BoundMethod,FileMethod,ClassObject,FixedStructType,CostObject)))
 def _builtin_len(self,x):
  obj=x.payload if isinstance(x,Value) else x
  if isinstance(obj,(list,dict,str,bytes,ByteObject,LazySequence)): return wrap(len(obj.data) if isinstance(obj,ByteObject) else (obj.length if isinstance(obj,LazySequence) else len(obj)))
  if isinstance(obj,StructObject): return wrap(len(obj.fields))
  raise TypeError_('len() requires a collection or string')
 def _seq(self,x):
  obj=x.payload if isinstance(x,Value) else x
  if isinstance(obj,(list,tuple,str,bytes)): return len(obj),lambda i: obj[i]
  if isinstance(obj,ByteObject): return len(obj.data),lambda i: obj.data[i]
  if isinstance(obj,LazySequence): return obj.length,obj.get
  raise TypeError_('value is not an iterable sequence')
 def _builtin_count(self,*args):
  if not 2<=len(args)<=3: raise TypeError_('count() expects start, stop, and optional step')
  vals=[unwrap(x) for x in args]
  if len(vals)==2: start,stop,step=vals[0],vals[1],1
  else: start,stop,step=vals
  if not all(isinstance(x,int) and not isinstance(x,bool) for x in (start,step) if x is not None) or (stop is not None and not isinstance(stop,int)): raise TypeError_('count() requires integer arguments')
  if step==0: raise ValueError_('count() step cannot be zero')
  if stop is None: raise ValueError_('count() requires a finite stop')
  n=max(0,(stop-start + (step-1 if step>0 else step+1))//step)
  return LazySequence(n,lambda i:start+i*step)
 def _builtin_enumerate(self,x,start=0):
  n,get=self._seq(x); start=unwrap(start)
  if not isinstance(start,int): raise TypeError_('enumerate() start must be int')
  return LazySequence(n,lambda i:[start+i,get(i)])
 def _builtin_zip(self,*xs):
  if not xs:return LazySequence(0,lambda i:[])
  seqs=[self._seq(x) for x in xs]; n=min(q[0] for q in seqs)
  return LazySequence(n,lambda i:[get(i) for _,get in seqs])
 def _builtin_stepview(self,x,step=1):
  n,get=self._seq(x); step=unwrap(step)
  if not isinstance(step,int) or step==0: raise ValueError_('stepview() step must be a nonzero integer')
  if step>0: length=(n+step-1)//step; index=lambda i:i*step
  else: length=(n+(-step)-1)//(-step); index=lambda i:n-1+i*step
  return LazySequence(length,lambda i:get(index(i)))
 def _builtin_binary(self,*xs):
  out=b''
  for x in xs:
   raw=unwrap(x)
   if isinstance(x,ByteObject): raw=x.data
   if isinstance(raw,str): out+=raw.encode('utf-8')
   elif isinstance(raw,(bytes,bytearray)): out+=bytes(raw)
   elif isinstance(raw,int) and 0<=raw<=255: out+=bytes([raw])
   elif isinstance(raw,list):
    if not all(isinstance(v,int) and 0<=v<=255 for v in raw): raise ValueError_('binary list values must be bytes')
    out+=bytes(raw)
   else: raise TypeError_('binary() accepts strings, bytes, integers, or byte lists')
  return Value(Kind.BINARY,out)
 def _builtin_hash(self,x):
  raw=unwrap(x)
  if isinstance(x,ByteObject): raw=x.data
  if isinstance(raw,str): data=b'S'+raw.encode()
  elif isinstance(raw,bool): data=b'B'+(b'1' if raw else b'0')
  elif isinstance(raw,int): data=b'I'+str(raw).encode()
  elif isinstance(raw,float): data=b'F'+repr(raw).encode()
  elif isinstance(raw,(bytes,bytearray)): data=b'Y'+bytes(raw)
  else: data=b'R'+self._object_text(x).encode()
  u=int.from_bytes(hashlib.sha256(data).digest()[:8],'big'); return wrap(u-(1<<64) if u&(1<<63) else u)
 def _builtin_bitfix(self,x,minimum,maximum):
  minimum,maximum=unwrap(minimum),unwrap(maximum)
  if not isinstance(minimum,int) or not isinstance(maximum,int): raise TypeError_('bitfix() range must be integers')
  if minimum>maximum: raise ValueError_('bitfix() requires min <= max')
  # Fold the deterministic signed 64-bit hash into the inclusive range.
  folded=self._builtin_hash(x).payload & ((1<<64)-1)
  return wrap(minimum + folded % (maximum-minimum+1))
 def _builtin_execute(self,source):
  source=unwrap(source)
  if not isinstance(source,str): raise TypeError_('execute() requires source text')
  self.run(source,'<execute>'); return NULL
 def _builtin_math_expression(self,source):
  source=unwrap(source)
  if not isinstance(source,str): raise TypeError_('math evaluator requires expression text')
  from .parser import Bin,Unary,Lit,Var,Block,ExprStmt
  tree=parse(source)
  if len(tree.xs)!=1 or not isinstance(tree.xs[0],ExprStmt): raise ValueError_('math evaluator accepts one expression')
  def valid(n):
   if isinstance(n,(Lit,Var)): return True
   if isinstance(n,Unary): return n.op in ('+','-','~','!','not') and valid(n.x)
   if isinstance(n,Bin): return n.op in ('+','-','*','/','%','**','<<','>>','&','|','^') and valid(n.a) and valid(n.b)
   return False
  expr=tree.xs[0].x
  if not valid(expr): raise ValueError_('math evaluator permits math expressions only')
  name='__eval_result'; self.run(f'{name} = {source}','<eval>'); return self.globals.get(name)
 def _builtin_open(self,path,mode='r'):
  path,mode=unwrap(path),unwrap(mode)
  if not isinstance(path,str) or not isinstance(mode,str): raise TypeError_('open() requires path and mode strings')
  if any(c not in 'rwa+btx' for c in mode) or mode.count('b')>1: raise ValueError_('invalid open mode')
  try:
   h=open(path,mode); return FileObject(h,path)
  except OSError as e: raise OsError(str(e)) from e
 def _file_call(self,m,args):
  f=m.file
  if f.closed: raise OsError('I/O operation on closed file')
  try:
   if m.name=='read': return wrap(f.handle.read(*[unwrap(x) for x in args]))
   if m.name=='write':
    v=unwrap(args[0]) if len(args)==1 else None
    if not isinstance(v,str): raise TypeError_('file.write() requires string')
    return wrap(f.handle.write(v))
   if m.name=='close': f.handle.close(); f.closed=True; return NULL
   if m.name=='seek': return wrap(f.handle.seek(*[unwrap(x) for x in args]))
   if m.name=='tell': return wrap(f.handle.tell())
  except CenterError: raise
  except TypeError as e: raise TypeError_(str(e)) from e
  except (OSError,ValueError) as e: raise OsError(str(e)) from e
 def _builtin_list(self,*args):
  if len(args)>1: raise TypeError_('list() accepts at most one argument')
  if not args:return Value(Kind.LIST,[])
  obj=args[0].payload if isinstance(args[0],Value) else args[0]
  if not isinstance(obj,(list,tuple,str)): raise TypeError_('list() requires an iterable')
  return Value(Kind.LIST,[wrap(x) for x in obj])
 def _builtin_array(self,*args):
  vals=args[0].payload if len(args)==1 and isinstance(args[0],Value) and args[0].kind in (Kind.LIST,Kind.ARRAY) else list(args)
  return Value(Kind.ARRAY,[wrap(x) for x in vals])
 def _builtin_struct(self,d=None):
  if d is None:return StructObject({})
  obj=d.payload if isinstance(d,Value) else d
  if not isinstance(obj,dict):raise TypeError_('struct() requires a dictionary')
  return StructObject(dict(obj))
 def _builtin_dobject(self,d=None):
  if d is None: return Value(Kind.DOBJECT,{})
  obj=d.payload if isinstance(d,Value) else d
  if not isinstance(obj,dict): raise TypeError_('dobject() requires a dictionary')
  return Value(Kind.DOBJECT,dict(obj))
 def _builtin_abs(self,x): return wrap(abs(unwrap(x)))
 def _builtin_pow(self,a,b): return wrap(pow(unwrap(a),unwrap(b)))
 def _builtin_max(self,*args):
  if not args:raise TypeError_('max() requires at least one argument')
  return wrap(max(unwrap(x) for x in args))
 def _builtin_min(self,*args):
  if not args:raise TypeError_('min() requires at least one argument')
  return wrap(min(unwrap(x) for x in args))
 def _builtin_round(self,x,*args): return wrap(round(unwrap(x),*(unwrap(y) for y in args)))
 def _builtin_ord(self,x):
  raw=unwrap(x)
  if not isinstance(raw,str) or len(raw)!=1:raise TypeError_('ord() requires a one-character string')
  return wrap(ord(raw))
 def _builtin_char(self,x):
  raw=unwrap(x)
  if not isinstance(raw,int):raise TypeError_('char() requires an integer')
  try:return Value(Kind.CHAR,chr(raw))
  except ValueError as e:raise ValueError_(str(e)) from e
 def _builtin_hex(self,x): return wrap(hex(unwrap(x)))
 def _builtin_oct(self,x): return wrap(oct(unwrap(x)))
 def _builtin_ascii(self,x): return wrap(ascii(unwrap(x)))
 def _builtin_input(self,p=''): return wrap(input(str(unwrap(p))))
 def _collection_call(self,m,args):
  obj=m.owner.payload if isinstance(m.owner,Value) else m.owner
  is_dobj=isinstance(m.owner,Value) and m.owner.kind is Kind.DOBJECT
  vals=obj if isinstance(obj,list) else (obj.fields if isinstance(obj,StructObject) else (obj if is_dobj and isinstance(obj,dict) else None))
  raw=[unwrap(x) for x in args]
  if isinstance(obj,(StructObject,dict)):
   fields=obj.fields if isinstance(obj,StructObject) else obj
   if m.name=='get': return fields.get(str(raw[0]),NULL)
   if m.name=='set':
    v=wrap(args[1]); schema=getattr(obj,'schema',{})
    if str(raw[0]) in schema and not type_matches(v,schema[str(raw[0])]): raise TypeError_('DObject field type mismatch')
    fields[str(raw[0])]=v; return v
   if m.name=='remove': return wrap(fields.pop(str(raw[0]),None))
   if m.name=='has': return wrap(str(raw[0]) in fields)
   if m.name=='keys': return Value(Kind.ARRAY,[wrap(k) for k in fields])
   if m.name=='values': return Value(Kind.ARRAY,list(fields.values()))
   if m.name=='items': return Value(Kind.ARRAY,[Value(Kind.ARRAY,[wrap(k),v]) for k,v in fields.items()])
   if m.name=='clear': fields.clear(); return NULL
   if m.name=='copy':
    if isinstance(obj,StructObject): return StructObject(dict(fields),obj.fixed,dict(obj.schema or {}) if obj.schema else obj.schema,obj.name)
    schema=dict(getattr(obj,'schema',{})); return Value(Kind.DOBJECT,DObjectPayload(dict(fields),schema))
  if not isinstance(vals,list): raise TypeError_('collection method requires a collection')
  if m.name=='add': vals.extend(args); return self._wrap_collection(obj)
  if m.name=='clear': vals.clear(); return NULL
  if m.name=='remove': vals.remove(args[0]); return NULL
  if m.name=='count': return wrap(sum(1 for v in vals if equal(v,args[0])))
  if m.name=='pop':
   try:return vals.pop(raw[0] if raw else -1)
   except IndexError as e:raise IndexError_(str(e)) from e
  if m.name=='reverse': vals.reverse(); return self._wrap_collection(obj)
  if m.name=='insert':
   if len(args)!=2 or not isinstance(raw[1],int): raise TypeError_('insert(object, index) requires an integer index')
   vals.insert(raw[1],args[0]); return self._wrap_collection(obj)
  if m.name=='copy': return Value(Kind.ARRAY if isinstance(self._unwrap_owner(m.owner),list) else Kind.LIST,list(vals))
  raise NameError_(f'unknown collection method {m.name!r}')
 def _unwrap_owner(self,x): return x.payload if isinstance(x,Value) else x
 def _wrap_collection(self,obj): return obj if isinstance(obj,Value) else wrap(obj)
 def _cast_int(self,x):
  if isinstance(x,Reference): x=x.target.value
  raw=unwrap(x)
  if isinstance(raw,bool): value=int(raw)
  elif isinstance(raw,(int,float)): value=int(raw)
  else: raise TypeError_('invalid int conversion')
  if not (-2**63 <= value <= 2**63-1): raise ValueError_('signed 64-bit integer overflow')
  return wrap(value)
 def _cast_float(self,x):
  raw=unwrap(x)
  if isinstance(raw,bool): return wrap(float(int(raw)))
  if isinstance(raw,(int,float)): return wrap(float(raw))
  raise TypeError_('invalid float conversion')
 def run(self,source,filename=None):
  chunk=Compiler().compile(parse(source));chunk.emit(Op.HALT);self._exec(chunk,self.globals,filename or '<main>');return self.output
 def _env_value(self,env,name):
  if name.startswith('__') and not self._runtime_private_name(name) and env.parent is None:
   raise PrivacyError(f'internal name is not accessible from module global scope: {name}')
  try:return env.get(name)
  except NameError_: return self.globals.get(name)
 def _runtime_private_name(self,name):
  return name in {'__class__','__cost__','__enum__','__eval_result','__fixed_struct__','__len__','__struct__'} or name.startswith(('__for_','__trigger_','__chain_'))
 def _global_cell(self,name):
  return self.globals.cells.get(name)
 def _call(self,fn,args):
  if isinstance(fn,Native):return fn(args,self)
  if isinstance(fn,NativeAdapter):return fn.call(args,self)
  if isinstance(fn,FileMethod): return self._file_call(fn,args)
  if isinstance(fn,CollectionMethod): return self._collection_call(fn,args)
  if isinstance(fn,Value):fn=fn.payload
  if isinstance(fn,BoundMethod): return self._call(fn.function,[fn.instance]+args)
  if isinstance(fn,Function):
   e=Environment(fn.closure,name=fn.name)
   specs=getattr(fn.chunk,'param_specs',None) or [type('P',(),{'name':n,'typ':None,'default':None}) for n in fn.chunk.params]
   if len(args)>len(specs): raise TypeError_(f'{fn.name}() takes {len(specs)} arguments, got {len(args)}')
   for i,p in enumerate(specs):
    if i<len(args): value=args[i]
    elif p.default is not None:
     dc=Compiler(); dc.e(p.default); dc.chunk.emit(Op.RETURN); value=self._exec(dc.chunk,e)
    else: raise TypeError_(f'{fn.name}() missing required argument: {p.name}')
    e.define(p.name,value,p.typ)
   if args and isinstance(args[0],InstanceObject) and args[0].cls.base: e.define('super',SuperProxy(args[0],args[0].cls.base))
   return self._exec(fn.chunk,e)
  if isinstance(fn,ClassObject):
   inst=InstanceObject(fn,{k:wrap(v) if v is not None else NULL for k,v in fn.fields.items()})
   for name,typ in (fn.field_types or {}).items():
    if inst.fields[name].kind is not Kind.NULL and not type_matches(inst.fields[name],typ): raise TypeError_('fixed class field type mismatch')
   init=attr_get(inst,'__init__') if '__init__' in fn.methods else None
   if init is not None:self._call(init,args)
   return inst
  if isinstance(fn,FixedStructType):
   data=args[0] if args else {}
   data=data.payload if isinstance(data,Value) and isinstance(data.payload,dict) else data
   data=data or {}; unknown=set(data)-set(fn.fields)
   if unknown: raise KeyError_(f'unknown fixed field {next(iter(unknown))}')
   fields={}
   for name,(typ,default) in fn.fields.items():
    if name in data: val=data[name]
    elif default is not None: val=self._eval_default(default,self.current_frame.env)
    else: raise KeyError_(f'missing fixed field {name}')
    if not type_matches(wrap(val),typ): raise TypeError_('fixed struct field type mismatch')
    fields[name]=wrap(val)
   return StructObject(fields,True,fn.fields,fn.name)
  if isinstance(fn,CostObject):return CostObject(fn.members,fn.storage)
  raise TypeError_(f'{fn!r} is not callable')
 def _eval_default(self,node,env):
  if isinstance(node,Lit): return wrap(node.v)
  dc=Compiler(); dc.e(node); dc.chunk.emit(Op.RETURN); return self._exec(dc.chunk,env)
 def _make_class(self,d,b,closure=None):
  base=b if isinstance(b,ClassObject) else None
  methods={}
  closure=closure or self.globals
  for name,ch in d.get('methods',{}).items(): methods[name]=Function(ch,closure,name)
  raw_fields=d.get('fields',[]); own_fields=raw_fields if isinstance(raw_fields,dict) else {x:None for x in raw_fields}
  fields={}; field_types={}
  if base:
   fields.update(base.fields); field_types.update(base.field_types)
  for name,default in own_fields.items(): fields[name]=self._eval_default(default,closure) if default is not None else None
  field_types.update(d.get('field_types',{}))
  return ClassObject(d['name'],fields,methods,base,field_types)
 def _exec(self,chunk,env,filename=None):
  frame=Frame(chunk,env,filename or (self.current_frame.filename if self.current_frame else None));self.call_stack.append(frame);old=self.current_frame;self.current_frame=frame;code=chunk.code;stack=[];handlers=[]
  try:
   while frame.ip<len(code):
    ins=code[frame.ip];frame.ip+=1;op=ins.op;a=ins.arg
    if op is Op.CONST:stack.append(wrap(chunk.constants[a]))
    elif op is Op.CREATE_SLICE:
     step=unwrap(stack.pop()); stop=unwrap(stack.pop()); start=unwrap(stack.pop()); stack.append(slice(start,stop,step))
    elif op is Op.AUG_ADD:
     b=stack.pop(); aa=stack.pop()
     if isinstance(aa,Value) and aa.kind is Kind.ARRAY:
      if not isinstance(b,Value) or b.kind is not Kind.ARRAY: raise TypeError_('Array += requires an Array RHS')
      stack.append(Value(Kind.ARRAY,aa.payload+ b.payload))
     else: stack.append(self.binary(Op.ADD,aa,b))
    elif op is Op.LOAD:
     try: v=self._env_value(env,a)
     except CenterError as error:
      if not self._dispatch_error(error,handlers,frame,env,stack): raise
      continue
     stack.append(v.target.value if isinstance(v,Reference) else v)
    elif op is Op.STORE:
     v=stack.pop(); name,typ,frozen,isref=a
     if hasattr(v,'code') and hasattr(v,'params'): v=Function(v,env,v.name)
     # A normal assignment creates/updates a binding in the current frame;
     # only an existing current-frame cell is updated. References explicitly
     # target cells and therefore remain the separate aliasing path.
     cell=env.cells.get(name)
     if name.startswith('__') and not self._runtime_private_name(name) and env.parent is not None:
      global_cell=self._global_cell(name)
      if global_cell is not None: cell=global_cell
     created=cell is None
     if created: cell=env.define(name,v,typ,frozen)
     if isref:
      if isinstance(v,Reference):cell.value=v
      else:
       try:cell.value=Reference(env.find_cell(v.payload if isinstance(v,Value) and v.kind is Kind.STRING else name))
       except Exception:cell.value=v
     elif isinstance(cell.value,Reference):cell.value.target.set(v)
     elif not created:cell.set(v)
    elif op is Op.POP:stack.pop()
    elif op is Op.LOAD_GLOBAL:stack.append(self.globals.get(a))
    elif op is Op.STORE_GLOBAL:self.globals.set(a,stack.pop())
    elif op is Op.CREATE_REF:stack.append(Reference(env.find_cell(a)))
    elif op is Op.LOAD_REF:
     ref=stack.pop()
     if not isinstance(ref,Reference): raise RefError('LOAD_REF requires a reference')
     stack.append(ref.target.value)
    elif op is Op.STORE_REF:
     value=stack.pop(); ref=stack.pop()
     if not isinstance(ref,Reference): raise RefError('STORE_REF requires a reference')
     ref.target.set(value)
    elif op in (Op.ADD,Op.SUB,Op.MUL,Op.DIV,Op.MOD,Op.POW,Op.EQ,Op.NE,Op.LT,Op.LE,Op.GT,Op.GE,Op.IN,Op.NOT_IN,Op.BIT_AND,Op.BIT_OR,Op.BIT_XOR,Op.SHL,Op.SHR,Op.AND,Op.OR):
     b=stack.pop();aa=stack.pop()
     try: stack.append(self.binary(op,aa,b))
     except CenterError as error:
      if not self._dispatch_error(error,handlers,frame,env,stack): raise
    elif op in (Op.NOT,Op.NEG,Op.BIT_NOT):
     x=stack.pop()
     try:
      if op is Op.NOT: value=not x.truthy()
      elif op is Op.NEG: value=-x.payload
      else:
       if not isinstance(x,Value) or x.kind is not Kind.INT: raise TypeError_('bitwise NOT requires an integer')
       value=~x.payload
      stack.append(wrap(value))
     except CenterError as error:
      if not self._dispatch_error(error,handlers,frame,env,stack): raise
    elif op is Op.JUMP:
     frame.ip=self.resolve(a,chunk)
    elif op is Op.JUMP_IF_FALSE_KEEP:
     if not stack[-1].truthy(): frame.ip=self.resolve(a,chunk)
    elif op is Op.JUMP_IF_TRUE_KEEP:
     if stack[-1].truthy(): frame.ip=self.resolve(a,chunk)
    elif op is Op.SHORT_OR:
     value=stack[-1]
     if isinstance(value,Value) and value.kind is Kind.ARRAY:
      pass
     else:
      stack[-1]=wrap(value.truthy())
      if stack[-1].truthy(): frame.ip=self.resolve(a,chunk)
    elif op is Op.JUMP_IF_FALSE:
     if not stack.pop().truthy():frame.ip=self.resolve(a,chunk)
    elif op is Op.JUMP_IF_TRUE:
     if stack.pop().truthy():frame.ip=self.resolve(a,chunk)
    elif op is Op.CALL:
     args=(stack[-a:] if a else []) if isinstance(a,int) else []
     if isinstance(a,int) and a:del stack[-a:]
     fn=stack.pop()
     try: stack.append(wrap(self._call(fn,args)))
     except CenterError as error:
      if not self._dispatch_error(error,handlers,frame,env,stack): raise
    elif op is Op.RETURN:return stack.pop() if stack else NULL
    elif op is Op.CREATE_LIST:
     vals=stack[-a:] if a else []
     if a: del stack[-a:]
     stack.append(Value(Kind.LIST,vals))
    elif op is Op.CREATE_ARRAY:
     vals=stack[-a:] if a else []
     if a: del stack[-a:]
     stack.append(Value(Kind.ARRAY,vals))
    elif op is Op.CREATE_STRUCT:
     vals=stack[-2*a:] if a else []
     if a: del stack[-2*a:]
     stack.append(Value(Kind.DOBJECT,{vals[i].payload:vals[i+1] for i in range(0,len(vals),2)}))
    elif op is Op.CREATE_DOBJECT:
     schema_val=stack.pop(); schema=schema_val if isinstance(schema_val,dict) else unwrap(schema_val)
     vals=stack[-2*a:] if a else []
     if a: del stack[-2*a:]
     fields={str(vals[i].payload):vals[i+1] for i in range(0,len(vals),2)}
     for key,typ in schema.items():
      if key in fields and not type_matches(fields[key],typ): raise TypeError_(f'DObject field type mismatch: {key}')
     stack.append(Value(Kind.DOBJECT,DObjectPayload(fields,schema)))
    elif op is Op.GET_ATTR:
     stack.append(attr_get(stack.pop(),a))
    elif op is Op.SET_ATTR:
     obj=stack.pop();v=stack.pop();attr_set(obj,a,v)
    elif op is Op.GET_ITEM:
     i=unwrap(stack.pop());o=stack.pop();o=o.payload if isinstance(o,Value) else o
     try:
      if isinstance(i,slice):
       if isinstance(o,StructObject): raise TypeError_('DObject does not support slicing')
       stack.append(Value(Kind.ARRAY if isinstance(o,list) else Kind.LIST,[wrap(v) for v in o[i]]))
      elif isinstance(o,StructObject):stack.append(o.fields[str(i)])
      elif isinstance(o,ByteObject): stack.append(wrap(o.data[i]))
      elif isinstance(o,LazySequence): stack.append(o.get(i))
      else:stack.append(wrap(o[i]))
     except IndexError as error:
      mapped=IndexError_(str(error))
      if self._dispatch_error(mapped,handlers,frame,env,stack): continue
      raise mapped from error
     except KeyError as error:
      mapped=KeyError_(str(error))
      if self._dispatch_error(mapped,handlers,frame,env,stack): continue
      raise mapped from error
    elif op is Op.SET_ITEM:
     i=unwrap(stack.pop());o=stack.pop();v=stack.pop();o=o.payload if isinstance(o,Value) else o
     if isinstance(o,StructObject):o.fields[str(i)]=v
     else:o[i]=v
    elif op is Op.CREATE_ENV:env=Environment(env,'<with>',True)
    elif op is Op.DESTROY_ENV:
     env.destroy();env=env.parent
    elif op is Op.RAISE:
     raw=stack.pop(); raw=raw.payload if isinstance(raw,Value) else raw
     error=raw.error if isinstance(raw,ExceptionObject) else (raw if isinstance(raw,CenterError) else CenterError(str(raw)))
     if self._dispatch_error(error,handlers,frame,env,stack): continue
     raise error
    elif op is Op.SETUP_EXCEPTION:handlers.append(a)
    elif op is Op.POP_EXCEPTION:
     if handlers:handlers.pop()
    elif op is Op.IMPORT:
     try:
      module,names=a; imported=self._import(module,frame.filename)
      for item in names:
       source,alias=item if isinstance(item,tuple) else (item,item)
       if source.startswith('_'): raise PrivacyError(f'private name cannot be imported: {source}')
       try: env.define(alias,imported.get(source))
       except NameError_: raise ImportError_(f'name {source!r} not exported by {module}')
     except CenterError as error:
      if not self._dispatch_error(error,handlers,frame,env,stack): raise
    elif op is Op.HALT:return NULL
   return NULL
  except ReturnSignal as r:return r.value
  finally:self.call_stack.pop();self.current_frame=old
 def resolve(self,a,c):return c.labels.get(a[1],0) if isinstance(a,tuple) and a[0]=='label' else a
 def _dispatch_error(self,error,handlers,frame,env,stack):
  if not handlers:return False
  matched=None
  for record in reversed(handlers):
   for ip,typ,name in record:
    public_names={c.__name__.rstrip('_') for c in type(error).__mro__}
    if typ is None or typ=='CenterError' or typ in public_names: matched=(ip,name); break
   if matched: break
  if not matched:return False
  handlers.pop(); frame.ip=matched[0]; stack.clear()
  if matched[1]: env.define(matched[1],Value(Kind.OBJECT,ExceptionObject(error)))
  return True
 def _module_candidates(self,module,filename):
  name=module.replace('.',os.sep); candidates=[]
  if filename and filename not in ('<main>',None): candidates.append(os.path.join(os.path.dirname(os.path.abspath(filename)),name))
  candidates.append(os.path.join(self.project_root,name))
  candidates += [os.path.join(p,name) for p in self.module_paths]
  out=[]
  for p in candidates:
   if p.endswith(('.ny','.noy')): out.append(p)
   else: out.extend((p+'.noy',p+'.ny'))
  return out
 def _import(self,module,filename):
  path=next((os.path.realpath(p) for p in self._module_candidates(module,filename) if os.path.isfile(p)),None)
  if path is None: raise ImportError_(f'module not found: {module}')
  rec=self.modules.get(path)
  if rec and rec['state']=='loading': raise ModuleLoadError(f'circular import: {path}')
  if rec and rec['state']=='loaded': return rec['env']
  env=Environment(name=path); self.modules[path]={'state':'loading','env':env}
  try:
   with open(path,encoding='utf8') as f: source=f.read()
   chunk=Compiler().compile(parse(source)); chunk.emit(Op.HALT); self._exec(chunk,env,path)
   self.modules[path]['state']='loaded'; return env
  except CenterError as e:
   self.modules.pop(path,None); raise ModuleLoadError(f'module initialization failed: {path}: {e}') from e
 def binary(self,op,a,b):
  aa=a.payload if isinstance(a,Value) else a; bb=b.payload if isinstance(b,Value) else b
  if op in (Op.IN,Op.NOT_IN):
   if not isinstance(bb,(list,tuple,str,bytes,dict)):
    raise TypeError_('right operand of in must be a collection')
   if isinstance(bb,dict): found=aa in bb
   elif isinstance(bb,(str,bytes)):
    try: found=aa in bb
    except TypeError as e: raise TypeError_(str(e)) from e
   else: found=any(equal(a,item) for item in b.payload)
   return wrap(not found if op is Op.NOT_IN else found)
  if isinstance(aa,list) or isinstance(bb,list):
   left=aa if isinstance(aa,list) else None; right=bb if isinstance(bb,list) else None
   selected=left if left is not None else right
   if op is Op.ADD and left is not None and right is not None and not (all(self._numeric(v) for v in left) and all(self._numeric(v) for v in right)):
    raise TypeError_('Array + Array requires numeric elements; use += for joining Arrays')
   bitops=(Op.BIT_AND,Op.BIT_OR,Op.OR,Op.BIT_XOR,Op.SHL,Op.SHR)
   numeric=(Op.ADD,Op.SUB,Op.MUL,Op.DIV,Op.MOD,Op.EQ,Op.NE,Op.LT,Op.LE,Op.GT,Op.GE)
   if op in bitops and not self._array_ints(selected): raise TypeError_('bitwise Array operation requires integer elements')
   if op in numeric and not self._array_numeric(selected): raise TypeError_('numeric Array operation requires numeric elements')
   if left is not None and right is not None:
    if len(left)!=len(right): raise LengthError('Array operands must have equal length')
    pairs=zip(left,right)
   elif left is not None: pairs=((x,b) for x in left)
   else: pairs=((a,x) for x in right)
   element_op=Op.BIT_OR if op is Op.OR else op
   return Value(Kind.ARRAY,[self.binary(element_op,x,y) for x,y in pairs])
  if op is Op.EQ:return wrap(equal(a,b))
  if op is Op.NE:return wrap(not equal(a,b))
  if op is Op.AND:return wrap(a.truthy() and b.truthy())
  if op is Op.OR:return wrap(a.truthy() or b.truthy())
  if op is Op.DIV and b.payload==0:raise ZeroDivisionError_('division by zero')
  f={Op.ADD:operator.add,Op.SUB:operator.sub,Op.MUL:operator.mul,Op.DIV:operator.truediv,Op.MOD:operator.mod,Op.POW:operator.pow,Op.LT:operator.lt,Op.LE:operator.le,Op.GT:operator.gt,Op.GE:operator.ge,Op.BIT_AND:operator.and_,Op.BIT_OR:operator.or_,Op.BIT_XOR:operator.xor,Op.SHL:operator.lshift,Op.SHR:operator.rshift}[op]
  try:
   result=f(a.payload,b.payload)
   if isinstance(result,int) and not isinstance(result,bool) and not (-2**63 <= result <= 2**63-1):
    raise ValueError_('signed 64-bit integer overflow')
   return wrap(result)
  except OverflowError:raise ValueError_('integer overflow')
  except TypeError as e: raise TypeError_(str(e)) from e
 def _numeric(self,x): return isinstance(x,Value) and x.kind in (Kind.INT,Kind.FLOAT)
 def _array_numeric(self,xs): return all(self._numeric(x) for x in xs)
 def _array_ints(self,xs): return all(isinstance(x,Value) and x.kind is Kind.INT for x in xs)

def run_source(source):return VM().run(source)
