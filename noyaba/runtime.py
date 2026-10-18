from dataclasses import dataclass, field
from enum import Enum

class CenterError(Exception): pass
class FreezeError(CenterError): pass
class RefError(CenterError): pass
class TypeError_(CenterError): pass
class NameError_(CenterError): pass
class ValueError_(CenterError): pass
class IndexError_(CenterError): pass
class LengthError(CenterError): pass
class KeyError_(CenterError): pass
class ZeroDivisionError_(CenterError): pass
class ImportError_(CenterError): pass
class CostError(CenterError): pass
class PrivacyError(CenterError): pass
class ModuleLoadError(ImportError_): pass
class ScopeError(CenterError): pass
class TriggerError(CenterError): pass
class SyntaxError_(CenterError): pass
class SystemError_(CenterError): pass
class IndentError(SyntaxError_, SyntaxError): pass
class OsError(CenterError): pass
class ReturnSignal(Exception):
    def __init__(self,value): self.value=value
@dataclass
class NativeAdapter:
    name: str; fn: object; abi_major: int=1; ownership: str='borrowed'
    def call(self,args,vm,abi_major=1):
        if abi_major != self.abi_major: raise SystemError_('native ABI major version mismatch')
        try: return wrap(self.fn(*args))
        except CenterError: raise
        except Exception as e: raise CenterError(f'native call failed: {e}') from e

class Kind(Enum): INT='INT'; FLOAT='FLOAT'; BOOL='BOOL'; CHAR='CHAR'; STRING='STRING'; BINARY='BINARY'; ARRAY='ARRAY'; LIST='LIST'; DOBJECT='DOBJECT'; STRUCT='STRUCT'; CLASS='CLASS'; FUNCTION='FUNCTION'; REFERENCE='REFERENCE'; ENUM='ENUM'; COST='COST'; NATIVE='NATIVE'; OBJECT='OBJECT'; NULL='NULL'
@dataclass
class Value:
    kind: Kind
    payload: object = None
    def __str__(self):
        if self.kind is Kind.NULL: return 'null'
        if self.kind is Kind.BOOL: return 'true' if self.payload else 'false'
        if self.kind in (Kind.LIST,Kind.ARRAY): return '['+', '.join(str(x) for x in self.payload)+']'
        if self.kind is Kind.DOBJECT: return '{'+', '.join(f'{k}: {v}' for k,v in self.payload.items())+'}'
        return str(self.payload)
    def truthy(self): return False if self.kind is Kind.NULL else bool(self.payload)

def wrap(x):
    if isinstance(x,Value): return x
    if x is None: return Value(Kind.NULL,None)
    if isinstance(x,bool): return Value(Kind.BOOL,x)
    if isinstance(x,int): return Value(Kind.INT,x)
    if isinstance(x,float): return Value(Kind.FLOAT,x)
    if isinstance(x,str): return Value(Kind.STRING,x)
    if isinstance(x,(bytes,bytearray)): return Value(Kind.BINARY,bytes(x))
    if isinstance(x,list): return Value(Kind.LIST,[wrap(y) for y in x])
    return x

def unwrap(x):
    if isinstance(x,Value): return x.payload if x.kind not in (Kind.LIST,Kind.ARRAY) else [unwrap(y) for y in x.payload]
    return x

@dataclass
class BindingCell:
    value: Value
    declared_type: object=None
    dynamic: bool=True
    frozen: bool=False
    alive: bool=True
    def set(self,v):
        if not self.alive: raise RefError('binding cell is no longer alive')
        v=wrap(v)
        if self.frozen: raise FreezeError('binding is frozen')
        if self.declared_type and not type_matches(v,self.declared_type): raise TypeError_('fixed binding type mismatch')
        self.value=v

def type_matches(v,t):
    """Match a declared Noyaba type without leaking host-language types."""
    if not isinstance(t,(str,Kind)): return True
    obj=v.payload if isinstance(v,Value) else v
    names={
        'int':Kind.INT,'float':Kind.FLOAT,'str':Kind.STRING,'string':Kind.STRING,
        'bool':Kind.BOOL,'char':Kind.CHAR,'list':Kind.LIST,'array':Kind.ARRAY,
        'null':Kind.NULL,'reference':Kind.REFERENCE,
    }
    if isinstance(t,Kind): return isinstance(v,Value) and v.kind is t
    if isinstance(v,Value) and t.upper() in Kind.__members__: return v.kind is Kind[t.upper()]
    if t.lower() in names: return isinstance(v,Value) and v.kind is names[t.lower()]
    if isinstance(obj,InstanceObject):
        c=obj.cls
        while c:
            if c.name==t:return True
            c=c.base
        return False
    if isinstance(obj,ClassObject): return False
    if isinstance(obj,FixedStructType): return obj.name==t
    if isinstance(obj,StructObject): return t.lower() in ('struct','dobject') or obj.name==t
    if isinstance(obj,EnumObject): return t.lower()=='enum' or getattr(obj,'name',None)==t
    if isinstance(obj,CostObject): return t.lower()=='cost'
    if isinstance(obj,Reference): return t.lower()=='reference'
    if isinstance(obj,(Function,BoundMethod)): return t.lower() in ('function','func')
    if isinstance(obj,NativeAdapter): return t.lower() in ('native','builtin')
    return False

class Environment:
    def __init__(self,parent=None,name='<env>',temporary=False): self.parent=parent; self.name=name; self.temporary=temporary; self.cells={}; self.alive=True
    def define(self,name,value=Value(Kind.NULL),declared_type=None,frozen=False):
        value=wrap(value)
        if declared_type and not type_matches(value,declared_type): raise TypeError_('fixed binding type mismatch')
        c=BindingCell(value,declared_type,declared_type is None,frozen); self.cells[name]=c; return c
    def find_cell(self,name):
        e=self
        while e:
            if name in e.cells: return e.cells[name]
            e=e.parent
        raise NameError_(name)
    def get(self,name): return self.find_cell(name).value
    def set(self,name,value):
        self.find_cell(name).set(value)
    def destroy(self):
        self.alive=False
        for c in self.cells.values(): c.alive=False
        self.cells.clear()

class Heap:
    def __init__(self): self.objects={}; self.next_id=1
    def allocate(self,obj): i=self.next_id; self.next_id+=1; self.objects[i]=obj; return i
    def release(self,i): self.objects.pop(i,None)

@dataclass
class StructObject:
    fields: dict=field(default_factory=dict); fixed: bool=False; schema: dict=None; name: str=None
@dataclass
class FixedStructType:
    name: str; fields: dict
@dataclass
class ClassObject:
    name: str; fields: dict; methods: dict; base: object=None; field_types: dict=field(default_factory=dict)
@dataclass
class InstanceObject:
    cls: ClassObject; fields: dict=field(default_factory=dict)
@dataclass
class Reference:
    target: BindingCell
@dataclass
class Function:
    chunk: object; closure: Environment; name: str='<function>'
@dataclass
class BoundMethod:
    function: object; instance: object
@dataclass
class LazySequence:
    length: int; getter: object
    def get(self,index):
        if not isinstance(index,int): raise TypeError_('sequence index must be int')
        if index<0 or index>=self.length: raise IndexError_('sequence index out of range')
        return wrap(self.getter(index))
@dataclass
class ByteObject:
    data: bytes
class DObjectPayload(dict):
    def __init__(self, values=None, schema=None):
        super().__init__(values or {}); self.schema=dict(schema or {})
@dataclass
class RootObject:
    pass
@dataclass
class FileObject:
    handle: object; path: str; closed: bool=False
@dataclass
class FileMethod:
    file: FileObject; name: str
@dataclass
class CollectionMethod:
    owner: object; name: str
@dataclass
class SuperProxy:
    instance: object; parent: object
@dataclass
class EnumObject:
    members: dict; name: str=None
@dataclass
class CostObject:
    members: dict; storage: Value; active: object=None
@dataclass
class ExceptionObject:
    error: CenterError

NULL=Value(Kind.NULL)

def attr_get(obj,name):
    original=obj
    if isinstance(obj,Value):
        if obj.kind in (Kind.ARRAY,Kind.LIST) and name in ('add','clear','remove','count','pop','reverse','insert','copy'):
            return CollectionMethod(original,name)
        if obj.kind is Kind.DOBJECT and name in ('get','set','remove','has','keys','values','items','copy','clear'):
            return CollectionMethod(original,name)
        obj=obj.payload
    if isinstance(obj,StructObject) and name in ('get','set','remove','has','keys','values','items','copy','clear'):
        return CollectionMethod(obj,name)
    if isinstance(obj,FileObject) and name in ('read','write','close','seek','tell'):
        return FileMethod(obj,name)
    if isinstance(obj,ExceptionObject):
        if name == 'message': return wrap(str(obj.error))
        if name == 'type': return wrap(type(obj.error).__name__.rstrip('_'))
        if name == 'args': return Value(Kind.ARRAY,[wrap(str(obj.error))])
    if isinstance(obj,dict):
        if name in obj:return obj[name]
    elif isinstance(obj,StructObject):
        if name in obj.fields:return obj.fields[name]
    elif isinstance(obj,InstanceObject):
        if name in obj.fields:return obj.fields[name]
        c=obj.cls
        while c:
            if name in c.methods:return BoundMethod(c.methods[name],obj)
            c=c.base
    elif isinstance(obj,ClassObject) and name in obj.methods:return obj.methods[name]
    elif isinstance(obj,SuperProxy):
        c=obj.parent
        while c:
            if name in c.methods:return BoundMethod(c.methods[name],obj.instance)
            c=c.base
    elif isinstance(obj,EnumObject) and name in obj.members:return wrap(obj.members[name])
    elif isinstance(obj,CostObject) and name in obj.members:
        if obj.active is not None and obj.active != name: raise CostError(f'inactive cost member: {name}')
        return obj.storage
    raise NameError_(f'attribute {name!r} not found')

def attr_set(obj,name,value):
    if isinstance(obj,Value):
        if obj.kind is Kind.DOBJECT:
            v=wrap(value); schema=getattr(obj.payload,'schema',{})
            if name in schema and not type_matches(v,schema[name]): raise TypeError_('DObject field type mismatch')
            obj.payload[name]=v; return
        obj=obj.payload
    if isinstance(obj,dict): obj[name]=wrap(value)
    elif isinstance(obj,StructObject):
        if obj.fixed:
            if name not in obj.schema: raise NameError_(f'unknown fixed field {name}')
            if not type_matches(wrap(value),obj.schema[name][0]): raise TypeError_('fixed struct field type mismatch')
        obj.fields[name]=wrap(value)
    elif isinstance(obj,InstanceObject):
        c=obj.cls; known=set(); types={}
        while c:
            known.update(c.fields)
            types.update(getattr(c,'field_types',{}) or {})
            c=c.base
        if known and name not in known: raise NameError_(f'unknown class field {name}')
        if name in types and not type_matches(wrap(value),types[name]): raise TypeError_('fixed class field type mismatch')
        obj.fields[name]=wrap(value)
    elif isinstance(obj,CostObject):
        if name not in obj.members: raise NameError_(name)
        obj.storage=wrap(value); obj.active=name
    else: raise TypeError_('object has no writable attributes')

def equal(a,b): return a.kind==b.kind and a.payload==b.payload
