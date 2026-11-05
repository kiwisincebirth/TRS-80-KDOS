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
def symbol(name):
 return int(re.search(r'^'+re.escape(name)+r'\s*=?\s*([0-9A-F]+)',LISTING,re.M)[1],16)
HIST_LEN=symbol('hist_len')
HIST_ENTRY=symbol('dos_history_page')
HIST_CODE=symbol('PAGE_DOSHISTORY')
HIST_DATA=symbol('DPAGE_DOSHISTORY')
HIST_PAGES=symbol('HISTORY_PAGES')
HIST_MAX=symbol('HISTORY_MAX')
HIST_LIMIT=symbol('hist_limit')
CFG_ENTRY=symbol('history_config_page')
CFG_CODE=symbol('PAGE_HISTORYCFG')
CFG_LOADED=symbol('hist_cfg_loaded')

class Rig:
 def __init__(self):
  self.m=Z80Machine(); self.mem=self.m.memory
  self.banks=[bytearray(512) for _ in range(256)]; self.page=0; self.dpage=0
  self.page_returns=[]; self.page_writes=[]
  self.hooks={}; self.keys=deque(); self.output=[]; self.checkpoints=[]
  self.m.mark_addrs(0x37e0,32,self.m.WRITE_MARK)
  self.m.set_write_callback(self.write)
  self.m.set_input_callback(lambda port:0x41 if port&255==0xcf else 0)
  self.hook(0x49,self.key); self.hook(0x32a,self.out)
  self.m.set_breakpoint(0xffff)
  self.hook(HIST_ENTRY,self.page_enter)
  self.hook(HIST_ENTRY+3,self.page_return)
  self.hook(CFG_ENTRY,lambda:self.page_enter(CFG_ENTRY,CFG_CODE))
  self.hook(CFG_ENTRY+3,self.page_return)
 def flush(self):
  self.banks[self.page][:]=self.mem[0x3400:0x3600]
  self.banks[self.dpage][:480]=self.mem[0x3600:0x37e0]
 def write(self,addr,value):
  assert addr in (0x37f0,0x37f1),f'Write into hardware area: {addr:04x}'
  self.page_writes.append((addr,value))
  # Code/data banks share the page pool but have independent selectors.
  if addr==0x37f0:
   self.banks[self.page][:]=self.mem[0x3400:0x3600]
   self.page=value; self.mem[0x3400:0x3600]=self.banks[value]
  else:
   self.banks[self.dpage][:480]=self.mem[0x3600:0x37e0]
   self.dpage=value; self.mem[0x3600:0x37e0]=self.banks[value][:480]
  self.mem[addr]=value
 def page_enter(self,entry=HIST_ENTRY,page=HIST_CODE):
  assert self.mem[entry]==0xcd,'Routine must use VIRTUAL_ROUTINE'
  self.page_returns.append(self.page)
  self.write(0x37f0,page)
  self.m.sp-=2
  self.mem[self.m.sp:self.m.sp+2]=(entry+3).to_bytes(2,'little')
  self.m.pc=0x3400
 def page_return(self):
  self.write(0x37f0,self.page_returns.pop());self.ret()
 def hook(self,addr,fn):
  self.hooks[addr]=fn; self.m.set_breakpoint(addr)
 def ret(self):
  sp=self.m.sp; self.m.pc=self.mem[sp]+256*self.mem[sp+1]; self.m.sp=sp+2
 def key(self):
  assert self.keys,'Unexpected extra keyboard read'
  item=self.keys.popleft()
  while isinstance(item,str):
   assert self.dpage==HIST_DATA
   n=self.mem[HIST_LEN]
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
     if addr==0x37f1:self.write(addr,v)
     else:
      assert not 0x37e0<=addr<0x3800,hex(addr)
      self.mem[addr]=v
     addr+=1
    p+=n
   elif typ==2:break
   else:p+=n or 256
 def line(self,keys):
  self.keys=deque(keys); self.output=[]; self.checkpoints=[]
  previous=self.page; previous_data=self.dpage
  self.flush()
  saved_banks=[bytes(b) for b in self.banks]
  reserved=bytes(self.mem[0x37e0:0x3800])
  first_input=not self.banks[HIST_DATA][CFG_LOADED-0x3600]
  self.page_writes=[]
  self.call(HIST_ENTRY)
  self.flush()
  assert self.page==previous and self.dpage==previous_data and self.m.sp==0xf002
  assert not self.page_returns
  assert bytes(self.mem[0x37e0:0x3800])==reserved
  # Only the allocated history data pages may change. Code, DEF USR pointers,
  # unrelated data pages and hardware bytes must remain untouched.
  for i,b in enumerate(saved_banks):
   if i not in range(HIST_DATA,HIST_DATA+HIST_PAGES):assert bytes(self.banks[i])==b,i
  assert [v for a,v in self.page_writes if a==0x37f0]==([HIST_CODE,CFG_CODE,HIST_CODE,previous] if first_input else [HIST_CODE,previous])
  assert not self.keys
  assert 0x1f not in self.output and 0x1c not in self.output
  if self.m.f&1:return None
  assert self.m.hl==0x4318
  assert self.mem[0x4318+self.m.b]==13
  return bytes(self.mem[0x4318:0x4318+self.m.b]).decode('ascii')

def history_tests():
 r=Rig(); r.load_cmd(BUILD/'SD-CARD/SYS/SYSP.sys')
 r.write(0x37f0,227)  # history is called from the separate command-shell bank
 r.write(0x37f1,32)   # BASIC's existing DEF FN / USR pointer bank
 assert bytes(r.mem[0x3600:0x3614])==b'\x4a\x1e'*10
 # Canaries include the inaccessible tail of every physical bank.
 for page in range(HIST_DATA,HIST_DATA+HIST_PAGES):r.banks[page][480:]=b'\xa5'*32
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
 # Invoke the same code with different preselected data banks.
 for page in (0,1,31,32,77,HIST_DATA,HIST_DATA+1,HIST_DATA+2):
  r.write(0x37f1,page)
  assert r.line([91,1]) is None
  assert r.line([13])==''
 r.write(0x37f1,32)
 for codepage in (214,222,227):
  r.write(0x37f0,codepage)
  assert r.line([91,1]) is None
 assert bytes(r.mem[0x3600:0x3614])==b'\x4a\x1e'*10
 for page in range(HIST_DATA,HIST_DATA+HIST_PAGES):assert r.banks[page][480:]==b'\xa5'*32
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
 return {'history':'PASS: 8-entry ring, UP/DOWN boundaries, draft, editing, cancel, empty input, 127-character limit, shell dispatch, independent code/data banks, caller data-page restoration, DEF USR preservation, hardware boundary guards'}

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

def configure(content,fail_read=False,busy=None):
 # Run the actual assembled file API, mocking only the board's I/O ports.
 r=Rig();r.load_cmd(BUILD/'SD-CARD/SYS/SYSP.sys')
 r.write(0x37f0,227);r.write(0x37f1,32);r.flush()
 saved=[bytes(b) for b in r.banks]
 state={'status':0x40,'chunk':deque(),'position':0,'length':0,
        'close':0,'reads':0,'command':None,'open_args':bytearray()}
 def inp(port):
  port&=255
  if port==0xcf:
   if (busy=='open' and state['command']==3) or (busy=='read' and state['command']==4) or (busy=='close' and state['command']==6):return 0x80
   return state['status']
  if port==0xc5:return 4
  if port==0xc3:return state['length']&255
  assert port==0xc2
  assert state['chunk'],'Read past end of SD transfer'
  return state['chunk'].popleft()
 def out(port,value):
  port&=255
  if port==0xc3:return
  if port==0xc2:
   assert state['command']==3
   state['open_args'].append(value);return
  assert port==0xc4
  state['command']=value
  if value==3:state['status']=0x41 if content is None else 0x40
  elif value==4:
   state['reads']+=1
   if fail_read and state['reads']>=int(fail_read):state['status']=0x41;return
   pos=state['position'];chunk=content[pos:pos+256]
   state['position']+=len(chunk);state['length']=len(chunk)
   state['chunk']=deque(chunk);state['status']=0x48 if chunk else 0x40
  elif value==6:
   state['close']+=1;state['chunk'].clear();state['status']=0x40
  else:raise AssertionError(value)
 r.m.set_input_callback(inp);r.m.set_output_callback(out)
 assert r.line([13])=='';r.flush()
 assert r.page==227 and r.dpage==32 and not r.page_returns
 assert state['open_args']==b'\x01/SYS/settings.cfg\x00'
 assert state['close']==(0 if content is None or busy=='open' else 1)
 for i,b in enumerate(saved):
  if i not in range(HIST_DATA,HIST_DATA+HIST_PAGES):assert bytes(r.banks[i])==b,i
 limit=r.banks[HIST_DATA][HIST_LIMIT-0x3600]
 reads=state['reads'];opens=bytes(state['open_args'])
 assert r.line([13])==''  # subsequent prompts do not reopen the config
 assert state['reads']==reads and bytes(state['open_args'])==opens
 return r,limit,state

def configuration_tests():
 cases=[(None,8),(b'',8),(b'\xef\xbb\xbfHistorySize=20',20),(b'# comment\r\nEnableHighRAM=0\r\n',8),
        (b'HistorySize=1',1),(b'HistorySize=20',20),
        (b'  hIsToRySiZe \t= 13 # comment\r\n',13),
        (b'HistorySize=13#HistorySize=20\n',13),
        (b'HistorySize=21',20),(b'HistorySize=999999999999999',20),
        (b'HistorySize=0',8),(b'HistorySize=-1',8),(b'HistorySize=+1',8),
        (b'HistorySize=abc',8),(b'HistorySize=',8),(b'HistorySize=1 2',8),
        (b'HistorySize=12abc',8),(b'HistorySizeExtra=20',8),
        (b'# HistorySize=20\n;HistorySize=19\nHistorySize=00009',9),
        (b'HistorySize=20\nHistorySize=4',4),
        (b'HistorySize=20\nHistorySize=bad',8),
        (b'HistorySize\rHistorySize=17\r',17),
        (b'#'+b'x'*4096+b'\nHistorySize=19\n',19)]
 for content,expected in cases:
  _,actual,_=configure(content)
  assert actual==expected,(content,actual,expected)
 _,actual,_=configure(b'HistorySize=20',fail_read=True)
 assert actual==8
 _,actual,_=configure(b'HistorySize=20\n#'+b'x'*300,fail_read=2)
 assert actual==8
 # Place the key/value across every position around a 256-byte block edge.
 for padding in range(240,266):
  _,actual,_=configure(b'#'+b'x'*padding+b'\nHistorySize=17')
  assert actual==17,padding
 # Verify every supported size, including non-powers of two and maximum.
 for capacity in range(1,HIST_MAX+1):
  r,actual,_=configure(f'HistorySize={capacity}\n'.encode())
  assert actual==capacity
  for i in range(capacity+5):assert r.line(f'CMD{i}\r'.encode())==f'CMD{i}'
  keys=[]
  for i in range(capacity+2):keys.extend([91,'checkpoint'])
  for i in range(capacity+2):keys.extend([10,'checkpoint'])
  keys.append(13)
  assert r.line(keys)==''
  assert r.checkpoints[:capacity+2]==[f'CMD{i}' for i in range(capacity+4,4,-1)]+['CMD5','CMD5']
  assert r.checkpoints[capacity+2:]==[f'CMD{i}' for i in range(6,capacity+5)]+['','','']
  assert r.line(list(b'UNFINISHED')+[91,10,13])=='UNFINISHED'
  assert r.line([91,8,ord('!'),13])=='UNFINISHE!'
  assert r.line([91,1]) is None
 # Longest lines in every maximum-capacity slot, plus the final draft slot.
 r,_,_=configure(b'HistorySize=20')
 for i in range(25):assert r.line([65+i]*127+[13])==chr(65+i)*127
 keys=[]
 for i in range(20):keys.extend([91,'checkpoint'])
 keys.append(1)
 assert r.line(keys) is None
 assert r.checkpoints==[chr(65+i)*127 for i in range(24,4,-1)]
 assert r.line([90]*127+[91,10,13])=='Z'*127
 # BUSY forever is bounded; a bad optional setting cannot hang DOS input.
 for phase in ('open','read','close'):
  _,limit,_=configure(b'HistorySize=20',busy=phase)
  assert limit==(20 if phase=='close' else 8)
 _,limit,_=configure(b'#'+b'x'*17000)
 assert limit==8
 # Configuration is deliberately absent from normal startup.

 r=Rig();r.load_cmd(BUILD/'SD-CARD/SYS/SYSP.sys')
 assert r.mem[symbol('READYX')]==0x21 # original LD HL,_KDOSMSG
 return {'configuration':'PASS: defaults, all sizes 1-20, clamp, invalid/missing settings, comments/whitespace/case, duplicate settings, read errors, block boundaries, rollover and 127-byte slots at capacity 20, lazy initialization, bounded BUSY/size fallback'}

def boot_loader_test():
 # Execute the real BOOT.SYS loader rather than the test CMD parser.
 # Stop at STARTUP; BASIC ROM initialization itself is not emulated.
 r=Rig();r.mem[0x5200:0x5300]=(BUILD/'SD-CARD/SYS/BOOT.SYS').read_bytes()
 content=(BUILD/'SD-CARD/SYS/SYSP.sys').read_bytes()
 state={'status':0x40,'data':deque(),'pos':0,'cmd':None,'open':bytearray()}
 r.m.mark_addrs(0x3000,0x400,r.m.WRITE_MARK)
 original_write=r.write
 def write(addr,value):
  if 0x3000<=addr<0x3400:
   original_write(0x37f0,(addr-0x3000)//4);r.mem[addr]=value
  else:original_write(addr,value)
 r.m.set_write_callback(write)
 def where():
  r.m.hl=int.from_bytes(r.mem[r.m.sp:r.m.sp+2],'little');r.ret()
 r.hook(0xb,where)
 r.hook(0x75,lambda:(_ for _ in ()).throw(AssertionError('Boot fell back to BASIC')))
 r.hook(0x5400,lambda:setattr(r.m,'pc',0xffff))
 def inp(port):
  port&=255
  if port==0xcf:return state['status']
  if port==0xc2:
   assert state['data'],'Boot read beyond available data'
   return state['data'].popleft()
  raise AssertionError(port)
 def out(port,value):
  port&=255
  if port==0xc3:return
  if port==0xc2:state['open'].append(value);return
  assert port==0xc4
  state['cmd']=value
  if value==0:state['data']=deque([1,0,0x55,0xaa]);state['status']=0x48
  elif value==3:state['status']=0x40
  elif value==4:
   pos=state['pos'];chunk=content[pos:pos+256]
   state['pos']+=len(chunk);state['data']=deque(chunk);state['status']=0x48 if chunk else 0x41
  elif value==6:state['data'].clear();state['status']=0x40
  else:raise AssertionError(value)
 r.m.set_input_callback(inp);r.m.set_output_callback(out)
 r.call(0x5200);r.flush()
 assert state['open'][1:].split(b'\x00')[0]==b'/SYS/SYSP.SYS'
 expected=Rig();expected.load_cmd(BUILD/'SD-CARD/SYS/SYSP.sys');expected.flush()
 for page in [HIST_CODE,CFG_CODE,*range(HIST_DATA,HIST_DATA+HIST_PAGES),32]:
  assert r.banks[page]==expected.banks[page],page
 assert bytes(r.mem[0x5400:0x5480])==bytes(expected.mem[0x5400:0x5480])
 return {'boot_loader':'PASS: actual BOOT.SYS loads SYSP.sys through SD ports and reaches STARTUP with code/data banks intact'}

if __name__=='__main__':
 report=history_tests()|directory_tests()|configuration_tests()|boot_loader_test()
 report['scope']='Compiled Z80 execution with mocked ROM console and Floppy80 API; no physical hardware or interrupt/timing validation.'
 (BUILD/'test-results.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
