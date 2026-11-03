"""Execute assembled Z80 code; mock ROM console and Floppy80 directory ports.
Not a complete Model I/Floppy80 emulator: hardware timing/interrupts need testing.
Requires z80 1.2.0 (MIT, Ivan Kosarev); see requirements.txt.
"""
from pathlib import Path
from collections import deque
import sys, json, re, argparse
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--build-dir',type=Path,default=ROOT/'build')
BUILD=parser.parse_args().build_dir
sys.path.insert(0,str(ROOT/'.test-deps'))
from z80 import Z80Machine
LISTING=(BUILD/'src/zout/SYS0P.lst').read_text(encoding='utf-8')
HIST_LEN=int(re.search(r'^hist_len\s+([0-9A-F]+)',LISTING,re.M)[1],16)

class Rig:
 def __init__(self):
  self.m=Z80Machine(); self.mem=self.m.memory
  self.banks=[bytearray(512) for _ in range(256)]; self.page=0
  self.hooks={}; self.keys=deque(); self.output=[]; self.checkpoints=[]
  self.m.mark_addr(0x37f0,self.m.WRITE_MARK)
  self.m.set_write_callback(self.write)
  self.hook(0x49,self.key); self.hook(0x32a,self.out)
  self.m.set_breakpoint(0xffff)
 def write(self,addr,value):
  assert addr==0x37f0
  self.banks[self.page][:]=self.mem[0x3400:0x3600]
  self.page=value; self.mem[0x3400:0x3600]=self.banks[value]
  self.mem[addr]=value
 def hook(self,addr,fn):
  self.hooks[addr]=fn; self.m.set_breakpoint(addr)
 def ret(self):
  sp=self.m.sp; self.m.pc=self.mem[sp]+256*self.mem[sp+1]; self.m.sp=sp+2
 def key(self):
  assert self.keys,'Unexpected extra keyboard read'
  item=self.keys.popleft()
  while isinstance(item,str):
   n=self.banks[183][HIST_LEN-0x3400] if self.page!=183 else self.mem[HIST_LEN]
   self.checkpoints.append(bytes(self.mem[0x4318:0x4318+n]).decode('ascii'))
   item=self.keys.popleft()
  self.m.a=item; self.ret()
 def out(self):
  self.output.append(self.m.a); self.ret()
 def call(self,addr):
  self.m.sp=0xf000; self.mem[0xf000:0xf002]=b'\xff\xff'; self.m.pc=addr
  for _ in range(10000):
   self.m.ticks_to_stop=100000
   self.m.run()
   if self.m.pc==0xffff: return
   if self.m.pc in self.hooks:self.hooks[self.m.pc]()
  raise AssertionError(f'CPU did not finish at {self.m.pc:04x}')
 def load_cmd(self,path):
  data=path.read_bytes(); p=0
  while p<len(data):
   typ,n=data[p:p+2]; p+=2
   if typ==1:
    n=(n-2)&255
    if n==0:n=256
    addr=int.from_bytes(data[p:p+2],'little'); p+=2
    for v in data[p:p+n]:
     if 0x3000<=addr<0x3400: self.write(0x37f0,(addr-0x3000)//4)
     self.mem[addr]=v; addr+=1
    p+=n
   elif typ==2:break
   else:p+=n or 256
 def line(self,keys):
  self.keys=deque(keys); self.output=[]; self.checkpoints=[]
  previous=self.page
  self.call(0x3680)
  assert self.page==previous and self.m.sp==0xf002
  assert not self.keys
  assert 0x1f not in self.output and 0x1c not in self.output
  if self.m.f&1:return None
  assert self.m.hl==0x4318
  assert self.mem[0x4318+self.m.b]==13
  return bytes(self.mem[0x4318:0x4318+self.m.b]).decode('ascii')

def history_tests():
 r=Rig(); r.load_cmd(BUILD/'SD-CARD/SYS/SYSP.sys')
 r.write(0x37f0,227)  # history is called from the separate command-shell bank
 shell_before=bytes(r.mem[0x3400:0x3600])
 assert r.line([91,10,13])==''
 assert r.line(b'DIR\r')=='DIR'
 assert r.line(b'PWD\r')=='PWD'
 assert r.line([91,91,8,ord('X'),13])=='DIX'
 assert r.line([91,1]) is None
 assert r.line([91,13])=='DIX'
 assert r.line(list(b'CD GAMES')+[91,91,10,10,13])=='CD GAMES'
 assert r.line(list(b'TEMP')+[31]+list(b'DIR')+[13])=='DIR'
 assert r.line([8]+list(b'X')+[8,8,13])==''
 assert r.line(list(b'A'*140)+[13])=='A'*127
 assert r.line([91,8,ord('B'),13])=='A'*126+'B'
 for i in range(12):assert r.line(f'CMD{i}\r'.encode())==f'CMD{i}'
 # Inspect each recall without submitting it, then restore the empty draft.
 keys=[]
 for i in range(10):keys.extend([91,'checkpoint'])
 for i in range(10):keys.extend([10,'checkpoint'])
 keys.append(13)
 assert r.line(keys)==''
 assert r.checkpoints[:10]==[f'CMD{i}' for i in range(11,3,-1)]+['CMD4','CMD4']
 assert r.checkpoints[10:]==[f'CMD{i}' for i in range(5,12)]+['','','']
 # Cancelled input must not displace the eight retained commands.
 assert r.line(b'CANCEL\x01') is None
 assert r.line([91,13])=='CMD11'
 # Full console parser integration: the colon shell invokes our editor and DIR.
 r.keys=deque(b'DIR\r'); r.output=[]
 assert bytes(r.mem[0x3400:0x3600])==shell_before
 r.write(0x37f0,227)
 # Find DOSPRMPT address from the assembled symbol table.
 import re
 lst=(BUILD/'src/zout/SYS0P.lst').read_text(encoding='utf-8')
 prompt=int(re.search(r'^DOSPRMPT\s*=\s*([0-9A-F]+)',lst,re.M)[1],16)
 r.mem[prompt]=1
 # RST 28H is the existing supervisor dispatcher; stop and inspect its ID.
 r.hook(0x28,lambda:None)
 r.m.sp=0xf000;r.m.pc=0x3400
 for _ in range(100):
  r.m.ticks_to_stop=100000;r.m.run()
  if r.m.pc==0x28:break
  assert r.m.pc in r.hooks,hex(r.m.pc)
  r.hooks[r.m.pc]()
 else:raise AssertionError('Shell never dispatched')
 assert r.m.a==0x24  # S_DIRCMD, not merely any supervisor call
 return {'history':'PASS: 8-entry ring, UP/DOWN boundaries, draft, editing, cancel, empty input, 127-character limit, shell dispatch'}

def dir_case(total,keys,enhanced=True,hidden=0):
 r=Rig();r.mem[0x4500:0x4700]=(BUILD/'SD-CARD/SYS/overlayd.sys').read_bytes()
 r.mem[0x5000:0x5002]=b'\r\x00';r.m.hl=0x5000
 records=[]
 for i in range(total):
  b=bytearray(32);b[8]=2 if i<hidden else 0
  name=f'F{i:07d}.CMD'.encode();b[9:9+len(name)]=name;records.append(b)
 state={'index':0,'offset':0,'reads':0,'waits':0,'printed':0,'commands':[]}
 def version():r.m.a=int(enhanced);r.m.f=0 if enhanced else 64;r.ret()
 def wait():
  r.m.a=8 if state['index']<total else 0;r.m.f=64;r.ret()
 def display():
  p=r.m.hl
  while r.mem[p] not in (0,3):
   v=r.mem[p];r.output.append(v);p+=1
   if v==13:break
  state['printed']+=1;r.ret()
 def inp(port):
  port&=255
  if port==0xc3:return 32
  assert port==0xc2
  v=records[state['index']][state['offset']];state['offset']+=1
  if state['offset']==32:state['offset']=0;state['index']+=1
  return v
 def out(port,value):
  if port&255==0xc4:state['commands'].append(value)
 r.m.set_input_callback(inp);r.m.set_output_callback(out)
 r.hook(0x4480,version);r.hook(0x448f,wait);r.hook(0x4467,display)
 r.hook(0x402d,lambda:setattr(r.m,'pc',0xffff))
 r.hook(0x4409,lambda:(_ for _ in ()).throw(AssertionError('DIR error')))
 r.keys=deque(keys);r.call(0x4500)
 assert not r.keys
 assert 31 not in r.output and 28 not in r.output
 return state,r.output

def directory_tests():
 s,o=dir_case(175,[1]);assert s['index']==175 and s['printed']==60 and len(o)==960 and 13 not in o
 s,o=dir_case(175,[32,1]);assert s['index']==175 and s['printed']==120 and len(o)==1920
 s,o=dir_case(175,[32,32]);assert s['index']==175 and s['printed']==176 and o[-1]==13
 s,o=dir_case(60,[1]);assert s['index']==60 and s['printed']==60
 s,o=dir_case(0,[]);assert o==[13]
 s,o=dir_case(5,[]);assert s['printed']==6
 s,o=dir_case(175,[1],hidden=10);assert s['printed']==60 and s['index']==175
 s,o=dir_case(175,[1],enhanced=False);assert s['index']==60 and s['commands'].count(9)==60
 return {'directory':'PASS: first/second-page BREAK, normal paging, exact page, empty/short directory, hidden entries, FreHD exit, Pico stream drained, no screen clear'}

if __name__=='__main__':
 report=history_tests()|directory_tests()
 report['scope']='Compiled Z80 execution with mocked ROM console and Floppy80 API; no physical hardware or interrupt/timing validation.'
 (BUILD/'test-results.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
