from dataclasses import dataclass
from .lexer import Lexer,Token
from .runtime import IndentError
class N: pass
@dataclass
class Lit(N): v:object
@dataclass
class Var(N): name:str
@dataclass
class Bin(N): op:str; a:N; b:N
@dataclass
class Chain(N): terms:list; ops:list
@dataclass
class Unary(N): op:str; x:N
@dataclass
class Call(N): f:N; args:list
@dataclass
class Attr(N): o:N; name:str
@dataclass
class Index(N): o:N; i:N
@dataclass
class SliceN(N): start:N=None; stop:N=None; step:N=None
@dataclass
class ListN(N): xs:list
@dataclass
class DictN(N): xs:list
@dataclass
class DictEntry(N): key:str; value:N; typ:str=None
@dataclass
class Assign(N): target:N; value:N; decl:object=None; frozen:bool=False; ref:bool=False
@dataclass
class AugAssign(N): target:N; op:str; value:N
@dataclass
class ExprStmt(N): x:N
@dataclass
class Block(N): xs:list
@dataclass
class If(N): branches:list; other:Block=None
@dataclass
class While(N): cond:N; body:Block
@dataclass
class For(N): name:str; seq:N; body:Block
@dataclass
class Break(N): pass
@dataclass
class Continue(N): pass
@dataclass
class Func(N): name:str; params:list; body:Block
@dataclass
class Param(N): name:str; typ:object=None; default:N=None
@dataclass
class Return(N): x:N
@dataclass
class With(N): name:object; body:Block
@dataclass
class Goto(N): name:str
@dataclass
class Label(N): name:str
@dataclass
class Raise(N): x:N
@dataclass
class Try(N): body:Block; catches:list
@dataclass
class Except(N): typ:str; name:str; body:Block
@dataclass
class ClassN(N): name:str; base:object; body:Block
@dataclass
class Import(N): names:list; module:str
@dataclass
class Trigger(N): value:N; cases:list; default:Block=None
@dataclass
class Case(N): values:list; body:Block
@dataclass
class Macro(N): name:str; params:list; body:N
@dataclass
class StructDef(N): name:str; fields:list

class Parser:
    def __init__(self,s): self.ts=Lexer(s).tokens(); self.i=0; self.in_class=False
    def t(self): return self.ts[self.i]
    def is_(self,v): return self.t().value==v
    def eat(self,v=None):
        t=self.t()
        if v is not None and t.value!=v: raise SyntaxError(f'expected {v}, got {t.value} line {t.line}')
        self.i+=1; return t
    def skip(self):
        while self.t().kind=='NL': self.i+=1
    def eat_kind(self,k):
        if self.t().kind!=k: raise SyntaxError(f'expected {k}, got {self.t().kind} line {self.t().line}')
        return self.eat()
    def program(self): return self.block(False)
    def block(self,ind=True):
        if ind:
            self.eat(':')
            # A colon followed immediately by a statement is a compact
            # one-statement block; a newline still selects indentation mode.
            if self.t().kind not in ('NL','INDENT'):
                line=self.t().line; node=self.stmt()
                if self.t().line==line and self.t().kind not in ('NL','EOF','DEDENT'):
                    raise SyntaxError(f'unexpected token {self.t().value!r} at line {self.t().line}')
                return Block([node])
            self.skip()
            if self.t().kind!='INDENT': raise IndentError(f'expected indented block at line {self.t().line}')
            self.eat_kind('INDENT')
        xs=[]
        while self.t().kind not in ('EOF','DEDENT'):
            if self.t().kind=='NL': self.i+=1; continue
            if self.t().kind=='INDENT':
                if ind: raise IndentError(f'unexpected indentation at line {self.t().line}')
                self.i+=1; continue
            line=self.t().line; xs.append(self.stmt()); self.skip()
            if self.t().line==line and self.t().kind not in ('EOF','DEDENT'):
                raise SyntaxError(f'unexpected token {self.t().value!r} at line {self.t().line}')
        if ind and self.t().kind=='DEDENT': self.i+=1
        return Block(xs)
    def stmt(self):
        line=self.t().line; n=self._stmt(); setattr(n,'line',line); return n
    def _stmt(self):
        t=self.t().value
        if t in ('cost','enum'):
            kind=self.eat().value; n=self.eat().value; self.eat('=')
            if kind=='enum' and self.is_('['):
                self.eat('['); entries=[]
                if not self.is_(']'):
                    while True:
                        k=self.eat(); self.eat(':'); entries.append((k.value[1:-1] if k.kind=='STRING' else k.value,self.expr()))
                        if not self.is_(','): break
                        self.eat(',')
                        if self.is_(']'): break
                self.eat(']'); value=DictN(entries)
            else: value=self.expr()
            return Assign(Var(n),Call(Var('__'+kind+'__'),[value]))
        if t=='trigger': return self.trigger()
        if t=='macro':
            self.eat(); n=self.eat().value; self.eat('('); ps=[]
            if not self.is_(')'):
                while True:
                    ps.append(self.eat().value)
                    if not self.is_(','): break
                    self.eat(',')
            self.eat(')'); self.eat(':'); self.skip()
            if self.t().kind=='INDENT': self.eat(); self.skip()
            body=self.expr(); self.skip()
            if self.t().kind=='DEDENT': self.eat()
            return Macro(n,ps,body)
        if t in ('if','elif'):
            branches=[]
            while self.is_('if') or self.is_('elif'):
                self.eat(); c=self.expr(); b=self.block(); branches.append((c,b)); self.skip()
            other=None
            if self.is_('else'): self.eat(); other=self.block()
            return If(branches,other)
        if t=='while': self.eat(); return While(self.expr(),self.block())
        if t=='for': self.eat(); n=self.eat().value; self.eat('in'); return For(n,self.expr(),self.block())
        if t=='break': self.eat(); return Break()
        if t=='continue': self.eat(); return Continue()
        if t=='func': return self.function()
        if t=='return': self.eat(); return Return(Lit(None) if self.t().kind in ('NL','DEDENT','EOF') else self.expr())
        if t=='with':
            self.eat(); name=None
            if not self.is_(':'): name=self.eat().value
            return With(name,self.block())
        if t=='goto': self.eat(); return Goto(self.eat().value)
        if self.t().kind=='ID' and self.i+1<len(self.ts) and self.ts[self.i+1].value==':' and self.ts[self.i+2].kind in ('NL','INDENT'):
            n=self.eat().value; self.eat(':'); return Label(n)
        if t=='raise': self.eat(); return Raise(self.expr())
        if t=='try':
            self.eat(); body=self.block(); catches=[]; self.skip()
            while self.is_('except'):
                self.eat(); typ=None; name=None
                if not self.is_(':') and not self.is_('as'): typ=self.eat().value
                if self.is_('as'): self.eat(); name=self.eat().value
                catches.append(Except(typ,name,self.block())); self.skip()
            return Try(body,catches)
        if t=='class':
            self.eat(); n=self.eat().value; base=None
            if self.is_('('): self.eat(); base=self.eat().value; self.eat(')')
            elif self.is_('extends'): self.eat(); base=self.eat().value
            self.in_class=True
            try: body=self.block()
            finally: self.in_class=False
            return ClassN(n,base,body)
        if t=='struct' and self.i+1<len(self.ts) and self.ts[self.i+1].kind=='ID':
            self.eat(); n=self.eat().value; self.eat(':'); self.skip(); self.eat_kind('INDENT'); fields=[]
            while self.t().kind not in ('DEDENT','EOF'):
                if self.t().kind=='NL': self.eat(); continue
                fn=self.eat().value; self.eat(':'); ft=self.eat().value; default=None
                if self.is_('='): self.eat(); default=self.expr()
                fields.append((fn,ft,default)); self.skip()
            if self.t().kind=='DEDENT': self.eat()
            return StructDef(n,fields)
        if t=='from':
            self.eat(); mod=self.eat().value
            while self.is_('.'):
                self.eat('.'); mod += '.' + self.eat().value
            self.eat('import'); names=[]
            while True:
                source=self.eat().value; alias=source
                if self.is_('as'):
                    self.eat('as'); alias=self.eat().value
                names.append((source,alias) if alias!=source else source)
                if not self.is_(','): break
                self.eat(',')
            return Import(names,mod)
        if t=='ref': self.eat(); n=self.eat().value; self.eat('='); return Assign(Var(n),self.expr(),ref=True)
        if t=='freeze': self.eat(); n=self.eat().value; self.eat('='); return Assign(Var(n),self.expr(),frozen=True)
        if self.t().kind=='ID' and self.i+1<len(self.ts) and self.ts[self.i+1].value==':':
            n=self.eat().value; self.eat(':'); typ=self.eat().value
            if self.in_class and not self.is_('='):
                if self.t().kind not in ('NL','DEDENT','EOF'):
                    raise SyntaxError(f'expected field initializer or boundary at line {self.t().line}')
                return Assign(Var(n),Lit(None),decl=typ)
            self.eat('=')
            if typ=='freeze': return Assign(Var(n),self.expr(),frozen=True)
            return Assign(Var(n),self.expr(),decl=typ)
        x=self.expr()
        if self.t().value == '+=':
            op=self.eat().value[:-1]
            if not isinstance(x,(Var,Attr,Index)): raise SyntaxError('augmented assignment requires an assignable target')
            return AugAssign(x,op,self.expr())
        if self.is_('='): self.eat(); return Assign(x,self.expr())
        return ExprStmt(x)
    def function(self):
        self.eat('func'); n=self.eat().value; self.eat('('); ps=[]
        if not self.is_(')'):
            while True:
                pn=self.eat().value; typ=None; default=None
                if self.is_(':'):
                    self.eat(':'); typ=self.eat().value
                if self.is_('='):
                    self.eat('='); default=self.expr()
                elif any(p.default is not None for p in ps):
                    raise SyntaxError(f'non-default parameter follows default parameter: {pn}')
                ps.append(Param(pn,typ,default))
                if not self.is_(','): break
                self.eat(',')
        self.eat(')'); return Func(n,ps,self.block())
    def trigger(self):
        self.eat('trigger'); value=self.expr(); self.eat(':'); self.skip(); self.eat_kind('INDENT'); cases=[]; default=None
        while self.t().kind not in ('DEDENT','EOF'):
            if self.t().kind=='NL': self.eat(); continue
            if self.is_('case'):
                self.eat(); vals=[self.expr()]
                while self.is_(','): self.eat(','); vals.append(self.expr())
                cases.append(Case(vals,self.block())); self.skip()
            elif self.is_('default'):
                self.eat()
                if default is not None: raise SyntaxError('duplicate default')
                default=self.block(); self.skip()
            else: raise SyntaxError(f'expected case/default at line {self.t().line}')
        if self.t().kind=='DEDENT': self.eat()
        return Trigger(value,cases,default)
    def expr(self,minp=0):
        if self.is_('not'):
            self.eat('not'); x=Unary('not',self.expr(3))
        else: x=self.atom()
        prec={'or':1,'||':1,'and':2,'&&':2,'==':3,'!=':3,'in':4,'<':5,'<=':5,'>':5,'>=':5,'|':6,'^':7,'&':8,'<<':9,'>>':9,'+':10,'-':10,'*':11,'/':11,'%':11,'**':12}
        while ((self.t().value in prec) or (self.t().value=='not' and self.i+1<len(self.ts) and self.ts[self.i+1].value=='in')) and (prec.get(self.t().value,4)>=minp):
            op=self.eat().value
            if op=='not' and self.is_('in'):
                self.eat('in'); op='not in'
            p=prec.get(op,4); y=self.expr(p+(0 if op=='**' else 1))
            if op in ('==','!=','in','not in','<','<=','>','>='):
                terms=[x,y]; ops=[op]
                while True:
                    current=self.t().value
                    is_not_in=current=='not' and self.i+1<len(self.ts) and self.ts[self.i+1].value=='in'
                    if not (current in ('==','!=','in','<','<=','>','>=') or is_not_in): break
                    next_op=self.eat().value
                    if next_op=='not': self.eat('in'); next_op='not in'
                    next_y=self.expr(prec.get(next_op,4)+1)
                    terms.append(next_y); ops.append(next_op)
                x=Chain(terms,ops) if len(ops)>1 else Bin(op,x,y)
            else:
                x=Bin(op,x,y)
        return x
    def atom(self):
        t=self.eat()
        if t.value in ('!','-','+','~'): x=Unary(t.value,self.atom())
        elif t.kind=='NUMBER': x=Lit(float(t.value) if '.' in t.value else int(t.value))
        elif t.kind=='STRING': x=Lit(bytes(t.value[1:-1],'utf8').decode('unicode_escape'))
        elif t.value=='true': x=Lit(True)
        elif t.value=='false': x=Lit(False)
        elif t.value=='null': x=Lit(None)
        elif t.value=='[':
            xs=[]
            if not self.is_(']'):
                while True:
                    xs.append(self.expr())
                    if not self.is_(','): break
                    self.eat(',')
                    if self.is_(']'): break
            self.eat(']'); x=ListN(xs)
        elif t.value=='{':
            xs=[]
            if not self.is_('}'):
                while True:
                    k=self.eat(); key=k.value[1:-1] if k.kind=='STRING' else k.value; typ=None
                    if self.is_('as'):
                        self.eat('as'); typ=self.eat().value
                    self.eat(':'); xs.append(DictEntry(key,self.expr(),typ))
                    if not self.is_(','): break
                    self.eat(',')
                    if self.is_('}'): break
            self.eat('}'); x=DictN(xs)
        elif t.value=='(':
            x=self.expr(); self.eat(')')
        else: x=Var(t.value)
        while True:
            if self.is_('('):
                self.eat(); a=[]
                if not self.is_(')'):
                    while True:
                        a.append(self.expr())
                        if not self.is_(','): break
                        self.eat(',')
                        if self.is_(')'): break
                self.eat(')'); x=Call(x,a)
            elif self.is_('.'):
                self.eat(); x=Attr(x,self.eat().value)
            elif self.is_('['):
                self.eat()
                if self.is_(':'):
                    start=None
                else:
                    start=self.expr()
                if self.is_(':'):
                    self.eat(':'); stop=None if self.is_(':') or self.is_(']') else self.expr()
                    step=None
                    if self.is_(':'):
                        self.eat(':'); step=None if self.is_(']') else self.expr()
                    self.eat(']'); x=Index(x,SliceN(start,stop,step))
                else:
                    self.eat(']'); x=Index(x,start)
            else: break
        return x

def parse(s): return Parser(s).program()
