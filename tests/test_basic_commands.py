"""ROM-integrated CMD/KILL tests, independent of sequential file I/O.
Set KDOS_TEST_ROM to a 12 KiB Model I Level II-compatible ROM (not bundled).
Run after building SYSP.sys; uses the z80 dependency from test_console.py.
The real ROM tokenizer, interpreter, expression and error routines execute
alongside compiled kDOS. BasicRig models paging/console and CommandRig models
the Pico directory/delete protocol with in-memory files: no host files are
deleted. Tests cover continuation, errors, cleanup and existing LOAD/RUN.
The final test exports a tokenized CMDKILL.BAS plus disposable CKTEST.TMP
under build/SD-CARD for hardware testing. Board timing is not simulated.
"""
import sys, os, json
from pathlib import Path
from collections import deque
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tests'))
sys.path.insert(0,str(root/'.test-deps'))
import test_console as base

class BasicError(Exception):
 """Capture a ROM error code for assertions before its normal error unwind."""
 def __init__(self,code):self.code=code;super().__init__(f'BASIC error {code:02x}')

class BasicRig(base.Rig):
 """Run actual BASIC against compiled kDOS, with simulated page trampolines.

 ROM addresses match the supported Model I Level II layout. Breakpoints
 provide input/output and stop at READY rather than entering the UI loop.
 """
 def __init__(self):
  super().__init__()
  rom=Path(os.environ['KDOS_TEST_ROM']).read_bytes()
  if len(rom)!=0x3000:raise ValueError('KDOS_TEST_ROM must be a 12 KiB Level II-compatible ROM')
  self.mem[:0x3000]=rom
  # Seed the ROM communication vectors normally copied during cold boot.
  self.mem[0x4000:0x4036]=self.mem[0x6d2:0x708]
  self.files={};self.handles={};self.selected=0;self.data=deque();self.status=0x40;self.error=0;self.command=0;self.args=[]
  self.m.set_input_callback(self.inp); self.m.set_output_callback(self.outp)
  self.load_cmd(base.BUILD/'SD-CARD/SYS/SYSP.sys')
  # CALL trampolines save/restore code pages; JP trampolines do not.
  for p in range(256):
   addr=0x3000+4*p
   if self.mem[addr] in (0xcd,0xc3):
    self.hook(addr,lambda p=p:self.enter(p))
    self.hook(addr+3,self.page_return)
  self.hook(0x49,lambda:self.key_return())
  self.hook(0x19a2,lambda:self.fail())
  self.hook(0x1a19,lambda:setattr(self.m,'pc',0xffff))
  self.call(0x5400)
  self.hook(0x1d1e,self.statement_end)
  self.output=[]
 def statement_end(self):
  # Stop at end-of-statement; otherwise continue NEWSTT past its breakpoint.
  self.m.pc=0xffff if self.mem[self.m.hl]==0 else 0x1d25
 def enter(self,p):
  a=0x3000+4*p
  if self.mem[a]==0xcd:
   self.page_returns.append(self.page)
   self.m.sp-=2;self.mem[self.m.sp:self.m.sp+2]=(a+3).to_bytes(2,'little')
  self.write(0x37f0,p);self.m.pc=0x3400
 def key_return(self):self.m.a=13;self.ret()
 def fail(self):raise BasicError(self.m.e)
 def inp(self,port):
  port &=255
  if port==0xcf:return self.status
  if port==0xc5:return self.error
  if port==0xc2:
   assert self.data, ('empty port',self.command)
   return self.data.popleft()
  return 0
 def outp(self,port,v):
  port &=255
  if port==0xc4 and v==0:
   self.command=0;self.status=0x40;self.data=deque([1,2,0x55,0xaa]);return
  if port==0xff:return # ROM cassette/keyboard latch initialization
  raise AssertionError(('unexpected Pico write',port,v))
 def program(self,lines):
  # Tokenize each line in ROM and construct its next-pointer/line-number
  # header at TXTTAB. A zero pointer terminates the program; VARTAB follows.
  start=int.from_bytes(self.mem[0x40a4:0x40a6],'little');address=start
  for number,text in lines:
   raw=text.encode()+b'\0';self.mem[0x6000:0x6000+len(raw)]=raw
   self.m.hl=0x6000;self.call(0x1bc0)
   end=0x4316
   while self.mem[end]:end+=1
   tokens=bytes(self.mem[0x4316:end+1]);nxt=address+4+len(tokens)
   line=nxt.to_bytes(2,'little')+number.to_bytes(2,'little')+tokens
   self.mem[address:nxt]=line;address=nxt
  self.mem[address:address+2]=b'\0\0'
  self.mem[0x40f9:0x40fb]=(address+2).to_bytes(2,'little')
  self.hooks[0x1d1e]=lambda:setattr(self.m,'pc',0x1d25)
  try:return self.statement('RUN')
  finally:self.hooks[0x1d1e]=self.statement_end
 def statement(self,text,direct=False):
  b=text.encode()+b'\0';self.mem[0x6000:0x6000+len(b)]=b
  self.m.hl=0x6000;self.call(0x1bc0) # ROM tokenizer, result HL before tokens
  # Keep code out of STRBUFF, which input conversion may use.
  start=0x4316; end=start
  while self.mem[end]:end+=1
  tokens=bytes(self.mem[start:end+1]);destination=0x4316 if direct else 0x6100
  self.mem[destination:destination+len(tokens)]=tokens
  # GONE1 expects HL on the separator before the first statement token.
  self.mem[destination-1]=58
  self.mem[destination+len(tokens):destination+len(tokens)+2]=b'\0\0'
  self.mem[0x40a2:0x40a4]=(0xffff if direct else 10).to_bytes(2,'little')
  self.m.hl=destination-1
  self.call(0x1d5a)
  assert not self.page_returns, self.page_returns
  result=bytes(self.output);self.output=[];return result


def expect_error(r,text,code):
 try:r.statement(text)
 except BasicError as e:
  assert e.code==code,(text,hex(e.code),hex(code))
  # Model the ROM's abandoned statement stack after an error; test commands
  # separately so a failed statement cannot leave a synthetic call frame.
  r.page_returns.clear()
 else:raise AssertionError(('expected error',text,code))


class CommandRig(BasicRig):
 """Provide directory records and an in-memory delete target for DOS services.

 The existing Z80 command parser and overlays still execute; only board
 ports are replaced. sent records the service ID and argument bytes.
 """
 def __init__(self,count=2):
  self.dir_records=[];self.dir_offset=0;self.dir_index=0;self.sent=[];self.io_length=0
  for i in range(count):
   record=bytearray(32);name=f'FILE{i:04d}.DAT'.encode();record[9:9+len(name)]=name
   self.dir_records.append(record)
  super().__init__()
  def version():self.m.a=1;self.m.f=0;self.ret()
  self.hook(0x4480,version)
  self.hook(0x1b,self.out)
 def inp(self,port):
  port &=255
  if self.command==0x11:
   if port==0xcf:return 0x48 if self.dir_index<len(self.dir_records) else 0x40
   if port==0xc3:return 32
   if port==0xc2:
    value=self.dir_records[self.dir_index][self.dir_offset];self.dir_offset+=1
    if self.dir_offset==32:self.dir_offset=0;self.dir_index+=1
    return value
  if self.command==0x1e and port==0xc3:return len(self.data)
  return super().inp(port)
 def outp(self,port,v):
  port &=255
  if port==0xc3:self.io_length=v;return
  if port==0xc4 and v in (0x11,*range(0x18,0x1f)):
   self.command=v;self.args=[];self.status=0x40;self.data.clear();self.sent.append((v,self.args))
   if v==0x11:self.dir_index=0;self.dir_offset=0
   if v==0x1e:self.data.extend(b'/TEST\r');self.status=0x48
   return
  if port==0xc2 and self.command in (0x11,*range(0x18,0x1f)):
   self.args.append(v)
   if self.command==0x1b and len(self.args)==self.io_length:
    name=bytes(self.args).rstrip(b'\0').decode()
    if name in self.files:del self.files[name]
    else:self.status=0x41;self.error=4
   return
  super().outp(port,v)

def command_tests():
 r=CommandRig();r.write(0x37f1,32)
 result=r.statement('CMD "DIR":PRINT "AFTER"')
 assert b'FILE0000.DAT' in result and result.endswith(b'AFTER\r'),result
 assert r.dir_index==2 and r.dpage==32
 assert r.mem[0x447f]==0
 assert r.statement('CMD "PWD":PRINT "BACK"')==b'/TEST\rBACK\r'
 assert r.statement('C$="cd GAMES":CMD C$:PRINT "OK"')==b'OK\r'
 assert r.sent[-1]==(0x19,list(b'GAMES\0')),r.sent
 # Loop and GOSUB return stacks survive DOS command exits.
 result=r.program([(10,'FOR I=1 TO 3'),(20,'GOSUB 100'),(30,'NEXT I'),
  (40,'PRINT "DONE"'),(50,'END'),(100,'CMD "PWD"'),(110,'RETURN')])
 assert result==b'/TEST\r'*3+b'DONE\r',result
 # First-page BREAK drains directory records, then resumes BASIC.
 r=CommandRig(175)
 def key():r.m.a=1;r.ret()
 r.hook(0x49,key)
 result=r.statement('CMD "DIR":PRINT "RESUMED"')
 assert r.dir_index==175 and result.endswith(b'RESUMED\r') and b'FILE0060.DAT' not in result
 for text,code in [('CMD ""',8),('CMD 12',0x18),('CMD "DIR"+CHR$(13)',8),
  ('CMD "'+('X'*128)+'"',8),('CMD "MISSING"',8),('CMD "LOAD X.CMD"',8)]:
  r=CommandRig();expect_error(r,text,code)
  r.flush();assert r.banks[41][0x83]==0
  assert r.statement('PRINT "RECOVERED"')==b'RECOVERED\r'
 # Existing DOS exits still follow their original ROM reset path.
 r=CommandRig();r.hook(0x6cc,lambda:setattr(r.m,'pc',0xffff))
 for address in (0x402d,0x4030,0x4400):
  r.write(0x37f1,32);r.call(address);assert r.dpage==32
 # Direct-mode command text remains intact in the actual BASIC input buffer.
 r=CommandRig();assert r.statement('CMD "PWD":PRINT "DIRECT"',direct=True)==b'/TEST\rDIRECT\r'
 assert r.statement('CMD LEFT$("PWD",INSTR("PWD","D"))')==b'/TEST\r'
 # Exercise the real ROM error display/unwind, then another successful CMD.
 r=CommandRig();r.m.clear_breakpoint(0x19a2);del r.hooks[0x19a2]
 error=r.statement('KILL "MISSING"',direct=True)
 assert b'File not found' in error,error
 assert r.statement('CMD "PWD"',direct=True)==b'/TEST\r'
 return {'basic_cmd':'PASS: real DOS dispatch, DIR/paging BREAK, PWD/CD, BASIC continuation, loops/GOSUB, errors and ordinary DOS exits'}


def kill_tests():
 r=CommandRig();r.files['DELETE.ME']=bytearray(b'example')
 assert r.statement('KILL "DELETE.ME":PRINT "DELETED"')==b'DELETED\r'
 assert 'DELETE.ME' not in r.files
 assert r.sent[-1]==(0x1b,list(b'DELETE.ME\0'))
 r.files['FOLDER/TEST.DAT']=bytearray(b'test')
 assert r.statement('F$="FOLDER/TEST.DAT":KILL F$:PRINT "NEXT"')==b'NEXT\r'
 assert 'FOLDER/TEST.DAT' not in r.files
 for text,code in [('KILL ""',0x80),('KILL "*.BAS"',0x80),('KILL "A?"',0x80),
  ('KILL "A B"',0x80),('KILL "'+('A'*32)+'"',0x80),('KILL 1',0x18),
  ('KILL "MISSING"',0x6a)]:
  r=CommandRig();expect_error(r,text,code);r.flush();assert r.banks[41][0x83]==0
 # Evaluate and validate the complete statement before deleting anything.
 r=CommandRig();r.files['KEEP']=bytearray(b'keep')
 expect_error(r,'KILL "KEEP",1',2);assert r.files['KEEP']==b'keep' and not r.sent
 # DOS errors propagate as descriptive BASIC errors and clear bridge state.
 for raw,expected in [(4,0x6a),(7,0x8a),(10,0x88),(1,0x72)]:
  r=CommandRig();original=r.outp
  def fail_delete(port,value):
   original(port,value)
   if r.command==0x1b and len(r.args)==r.io_length:r.status=0x41;r.error=raw
  r.m.set_output_callback(fail_delete)
  expect_error(r,'KILL "TEST"',expected)
  r.flush();assert r.banks[41][0x83]==0
  assert r.statement('CMD "PWD"')==b'/TEST\r'
 # Cleanup on an abandoned command preserves both caller banks/registers.
 r=CommandRig();r.write(0x37f1,41);r.mem[0x3683]=1
 r.write(0x37f1,32);r.write(0x37f0,226);r.m.af=0x1234
 r.call(base.symbol('basic_cmd_cancel'));r.flush()
 assert r.page==226 and r.dpage==32 and r.m.af==0x1234
 assert r.banks[41][0x83]==0 and not r.page_returns
 # NEWREADY invokes cleanup even after a nonlocal DOS/ROM exit.
 r.write(0x37f1,41);r.mem[0x3683]=1;r.mem[0x40e1]=1
 r.write(0x37f1,32);r.call(base.symbol('NEWREADY'));r.flush()
 assert r.banks[41][0x83]==0 and r.dpage==32
 return {'basic_kill':'PASS: deletion, expressions/paths, continuation, invalid names/syntax, missing/access/protection/I/O errors and abandoned-command cleanup'}

def basic_loader_tests():
 # Execute the existing BASIC LOAD overlay and ROM reset/linker routines.
 # Mock its legacy program-file API only; sequential-file closes still run
 # through the actual new handlers and simulated enhanced Pico ports.
 maker=BasicRig()
 assert maker.program([(10,'PRINT "LOADED OK"'),(20,'END')])==b'LOADED OK\r'
 start=int.from_bytes(maker.mem[0x40a4:0x40a6],'little')
 end=int.from_bytes(maker.mem[0x40f9:0x40fb],'little')
 program=b'\xff'+bytes(maker.mem[start:end])
 for open_files in (False,):
  r=BasicRig();state={'remaining':deque(),'opens':0,'closes':0}
  def open_program():
   assert bytes(r.mem[r.m.de:r.m.de+r.m.b])==b'GAME.BAS'
   state['opens']+=1;state['remaining']=deque(program)
   r.m.a=0;r.m.f=64;r.ret()
  def read_program():
   assert state['remaining'],'LOAD read past the program end'
   r.m.a=state['remaining'].popleft();r.m.f=64;r.ret()
  def close_program():
   state['closes']+=1;r.m.a=0;r.m.f=64;r.ret()
  def dos_error():raise AssertionError('Unexpected DOS error during LOAD')
  r.hook(base.symbol('api_OPEN'),open_program)
  r.hook(base.symbol('api_READBYTE'),read_program)
  r.hook(base.symbol('api_CLOSE'),close_program)
  r.hook(0x402d,lambda:setattr(r.m,'pc',0xffff))
  r.hook(0x4409,dos_error)
  # Repeated LOAD also catches a stuck callback or stale bank state.
  for attempt in range(2):
   assert r.statement('LOAD "GAME.BAS"')==b''
   assert not r.handles and not state['remaining']
   assert state['opens']==state['closes']==attempt+1
   loaded_start=int.from_bytes(r.mem[0x40a4:0x40a6],'little')
   loaded_end=int.from_bytes(r.mem[0x40f9:0x40fb],'little')
   loaded=bytes(r.mem[loaded_start:loaded_end])
   assert loaded.startswith(program[1:]) and loaded[len(program)-1:] in (b'',b'\0')
   # Let NEWSTT run normally through the loaded program, then END.
   r.hooks[0x1d1e]=lambda:setattr(r.m,'pc',0x1d25)
   assert r.statement('RUN')==b'LOADED OK\r'
   r.hooks[0x1d1e]=r.statement_end
 return {'basic_load':'PASS: LOAD, ROM reset/linker and RUN; repeated loads with no sequential-I/O feature; caller code/data bank restoration'}


def smoke_test():
 r=CommandRig();r.files['CKTEST.TMP']=bytearray(b'disposable test file')
 lines=[(int(number),text) for number,text in (line.split(' ',1) for line in (root/'tests/CMDKILL.txt').read_text().splitlines())]
 result=r.program(lines)
 assert result.endswith(b'CMD/KILL TEST FINISHED\r') and 'CKTEST.TMP' not in r.files
 start=int.from_bytes(r.mem[0x40a4:0x40a6],'little')
 end=int.from_bytes(r.mem[0x40f9:0x40fb],'little')
 (base.BUILD/'SD-CARD/CMDKILL.BAS').write_bytes(b'\xff'+bytes(r.mem[start:end]))
 (base.BUILD/'SD-CARD/CKTEST.TMP').write_text('Disposable file for the CMD/KILL hardware test.\n',encoding='ascii')
 return {'smoke':'PASS: CMDKILL.BAS generated; CKTEST.TMP is the disposable deletion target'}

if __name__=='__main__':
 if not os.environ.get('KDOS_TEST_ROM'):raise SystemExit('Set KDOS_TEST_ROM to a 12 KiB Level II-compatible ROM; see tests/README.txt.')
 report=command_tests()|kill_tests()|basic_loader_tests()|smoke_test()
 report['scope']='Actual BASIC ROM and compiled DOS handlers; Pico filesystem/ports simulated. Physical board testing required.'
 (base.BUILD/'basic-commands-test-results.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
