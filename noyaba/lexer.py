from dataclasses import dataclass
import re
from .runtime import IndentError
@dataclass
class Token: kind:str; value:str; line:int; col:int
class Lexer:
    specs=[('NUMBER',r'\d+(?:\.\d+)?'),('STRING',r'"[^"]*"|\'[^\']*\''),('ID',r'[A-Za-z_][A-Za-z0-9_]*'),('OP',r'\+=|==|!=|<=|>=|<<|>>|\*\*|:=|->|&&|\|\||[+*/%<>=!&|^~.:,;()\-]|\[|\]|\{|\}')]
    kws=set('if elif else while for in func return ref with class extends try do except as goto break continue true false null struct cost enum freeze import from and or not trigger case default macro'.split())
    def __init__(self,s): self.s=s; self.i=0; self.line=1; self.col=1; self.ind=[0]
    def tokens(self):
        out=[]; at_line=True; delimiters=0
        while self.i<len(self.s):
            if at_line:
                n=0
                while self.i<len(self.s) and self.s[self.i] in ' \t': n += 4 if self.s[self.i]=='\t' else 1; self.i+=1
                if self.i>=len(self.s): break
                if self.s[self.i]=='\n': self.i+=1; self.line+=1; self.col=1; continue
                if self.s[self.i]=='#':
                    while self.i<len(self.s) and self.s[self.i]!='\n': self.i+=1
                    continue
                if delimiters==0:
                    if n>self.ind[-1]: self.ind.append(n); out.append(Token('INDENT','',self.line,1))
                    while n<self.ind[-1]: self.ind.pop(); out.append(Token('DEDENT','',self.line,1))
                    if n!=self.ind[-1]:
                        raise IndentError(f'unmatched indentation level at {self.line}:1')
                at_line=False; self.col=n+1
            if self.i>=len(self.s): break
            ch=self.s[self.i]
            if ch in ' \t\r': self.i+=1; self.col+=1; continue
            if ch=='\n':
                self.i+=1; self.line+=1; self.col=1; at_line=True
                if delimiters==0: out.append(Token('NL','',self.line-1,self.col))
                continue
            if ch=='#':
                while self.i<len(self.s) and self.s[self.i]!='\n': self.i+=1
                continue
            for kind,pat in self.specs:
                m=re.match(pat,self.s[self.i:])
                if m:
                    v=m.group(); out.append(Token('KW' if kind=='ID' and v in self.kws else kind,v,self.line,self.col)); self.i+=len(v); self.col+=len(v)
                    if v in '([{': delimiters+=1
                    elif v in ')]}': delimiters=max(0,delimiters-1)
                    break
            else: raise SyntaxError(f'unknown character {ch!r} at {self.line}:{self.col}')
        while len(self.ind)>1: self.ind.pop(); out.append(Token('DEDENT','',self.line,1))
        out.append(Token('EOF','',self.line,self.col)); return out
