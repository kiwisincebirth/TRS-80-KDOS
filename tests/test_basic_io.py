"""ROM-integrated sequential BASIC file tests.
Set KDOS_TEST_ROM to a 12 KiB Model I Level II-compatible ROM (not bundled).
Run after building SYSP.sys; uses the z80 dependency from test_console.py.
The real ROM tokenizer, interpreter, expressions, variables and garbage
collector execute alongside compiled kDOS. BasicRig models page switching
and Pico file commands with in-memory files; no host file data is modified.
Tests cover typed input/output, EOF, boundaries, errors, lifecycle closes,
and the existing LOAD/RUN path. The smoke program is exported as a tokenized
IOCHECK.BAS under build/SD-CARD. Firmware timing still needs hardware tests.
"""
import sys, os, json
from pathlib import Path
from collections import deque
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tests'))
sys.path.insert(0,str(root/'.test-deps'))
import test_console as base

class BasicError(Exception):
 """Expose a ROM error number for assertions before normal error recovery."""
 def __init__(self,code):self.code=code;super().__init__(f'BASIC error {code:02x}')

class BasicRig(base.Rig):
 """Execute BASIC with simulated code/data banks, console and Pico file handles.

 ROM entry addresses match the Model I Level II layout. CALL trampolines
 restore the caller code page; JP trampolines deliberately leave it changed.
 The filesystem model checks the one-byte enhanced-file protocol.
 """
 def __init__(self):
  super().__init__()
  rom=Path(os.environ['KDOS_TEST_ROM']).read_bytes()
  if len(rom)!=0x3000:raise ValueError('KDOS_TEST_ROM must be a 12 KiB Level II-compatible ROM')
  self.mem[:0x3000]=rom
  # Seed the communication vectors normally copied from ROM at cold boot.
  self.mem[0x4000:0x4036]=self.mem[0x6d2:0x708]
  self.files={};self.handles={};self.selected=0;self.data=deque();self.status=0x40;self.error=0;self.command=0;self.args=[]
  self.m.set_input_callback(self.inp); self.m.set_output_callback(self.outp)
  self.load_cmd(base.BUILD/'SD-CARD/SYS/SYSP.sys')
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
  if port==0xc6:self.selected=v;return
  if port==0xc3:return
  if port==0xc4:
   self.command=v;self.args=[];self.data.clear();self.status=0x40;self.error=0
   if v==0:self.data.extend([1,2,0x55,0xaa])
   elif v in (0x20,0x21,0x15,0x26):
    assert self.selected in self.handles,('invalid handle',self.selected)
    h=self.handles[self.selected]
    if v==0x26:
     fcb=bytearray(9);fcb[0]=h['pos']&255;fcb[1]=h['pos']>>8;fcb[2]=self.selected;fcb[4]=1;self.data.extend(fcb)
    elif v==0x20:
     if h['pos']==len(self.files[h['name']]): self.status=0x41;self.error=0x40|28
     else:self.data.append(self.files[h['name']][h['pos']]);h['pos']+=1
    elif v==0x15:
     self.data.extend(bytes(32));del self.handles[self.selected]
   elif v!=0x14:raise AssertionError(('command',v))
  elif port==0xc2:
   self.args.append(v)
   if self.command==0x14 and len(self.args)==36:
    options,lrl,lo,hi,*name=self.args;name=bytes(name).split(b'\0')[0].decode()
    assert lrl==1
    if not options&0x1c and name not in self.files:self.status=0x41;self.error=0x40|24;return
    if options&8 or name not in self.files:self.files[name]=bytearray()
    ident=next(i for i in range(16) if i not in self.handles)
    self.handles[ident]={'name':name,'pos':0,'mode':options}
    fcb=bytearray(32);fcb[0]=0x80;fcb[3:5]=bytes([lo,hi]);fcb[7]=ident;fcb[9]=lrl;self.data.extend(fcb)
   elif self.command==0x21:
    h=self.handles[self.selected];assert h['mode']&2
    self.files[h['name']].append(v);h['pos']+=1
 def program(self,lines):
  # Build ROM-tokenized lines at TXTTAB with next-line pointers and numbers.
  # A zero pointer ends the program; VARTAB marks the following variable area.
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
 def statement(self,text):
  b=text.encode()+b'\0';self.mem[0x6000:0x6000+len(b)]=b
  self.m.hl=0x6000;self.call(0x1bc0) # ROM tokenizer, result HL before tokens
  # Keep code out of STRBUFF, which input conversion may use.
  start=0x4316; end=start
  while self.mem[end]:end+=1
  tokens=bytes(self.mem[start:end+1]);self.mem[0x6100:0x6100+len(tokens)]=tokens
  # GONE1 expects HL on a separator immediately before the statement.
  self.mem[0x60ff]=58
  self.mem[0x6100+len(tokens):0x6100+len(tokens)+2]=b'\0\0'
  self.mem[0x40a2:0x40a4]=(10).to_bytes(2,'little') # program-mode INPUT
  self.m.hl=0x60ff
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



def basic_loader_tests():
 # Execute the existing BASIC LOAD overlay and ROM reset/linker routines.
 # Mock its legacy program-file API only; sequential-file closes still run
 # through the actual new handlers and simulated enhanced Pico ports.
 maker=BasicRig()
 assert maker.program([(10,'PRINT "LOADED OK"'),(20,'END')])==b'LOADED OK\r'
 start=int.from_bytes(maker.mem[0x40a4:0x40a6],'little')
 end=int.from_bytes(maker.mem[0x40f9:0x40fb],'little')
 program=b'\xff'+bytes(maker.mem[start:end])
 for open_files in (False,True):
  r=BasicRig();state={'remaining':deque(),'opens':0,'closes':0}
  if open_files:
   r.statement('OPEN "O",1,"BEFORE"');r.statement('PRINT#1,"SAVED"')
   r.files['INPUT']=bytearray(b'hello');r.statement('OPEN "I",2,"INPUT"')
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
  if open_files:assert r.files['BEFORE']==b'SAVED\r\n'
 return {'basic_load':'PASS: LOAD, ROM reset/linker and RUN; repeated loads with zero/two open files; caller code/data bank restoration'}


def tests():
 r=BasicRig()
 for s in ['OPEN "O",1,"TEST.DAT"','PRINT#1,"HELLO"','CLOSE 1','OPEN "I",1,"TEST.DAT"','INPUT#1,A$']:
  r.statement(s)
 assert r.statement('PRINT A$')==b'HELLO\r'
 assert r.statement('PRINT EOF(1);EOF(1)')==b'-1 -1 \r'
 r.statement('CLOSE');assert not r.handles
 assert r.files['TEST.DAT']==b'HELLO\r\n'

 r=BasicRig()
 for s in ['OPEN "O",1,"ONE.DAT"','OPEN "O",2,"TWO.DAT"','PRINT#1,"A";",";12;",";"Z"','PRINT#2,123.5','CLOSE #1,#2','OPEN "I",1,"ONE.DAT"','OPEN "I",2,"TWO.DAT"','INPUT#1,A$,N%,B$','INPUT#2,X']:
  r.statement(s)
 assert r.statement('PRINT A$;N%;B$;X')==b'A 12 Z 123.5 \r'
 assert r.statement('PRINT EOF(1);EOF(2)')==b'-1 -1 \r'
 r.statement('CLOSE')

 r=BasicRig();r.files['LINES']=bytearray(b' first, "quoted"\r\n\r\nlast')
 r.statement('OPEN "I",1,"LINES"')
 for expected in [b' first, "quoted"\r',b'\r',b'last\r']:
  assert r.statement('PRINT EOF(1);EOF(1)')==b' 0  0 \r'
  r.statement('LINE INPUT#1,A$');assert r.statement('PRINT A$')==expected
 assert r.statement('PRINT EOF(1)')==b'-1 \r'
 expect_error(r,'LINE INPUT#1,A$',0x7c)
 r.statement('CLOSE')

 r=BasicRig();r.files['FIELDS']=bytearray(b'"A,B",-123, 4.25 ," Z "\n')
 r.statement('OPEN "I",1,"FIELDS"');r.statement('INPUT#1,A$,B%,C#,D$')
 assert r.statement('PRINT A$;B%;C#;D$')==b'A,B-123  4.25  Z \r'
 r.statement('CLOSE')

 # Three independent files, nested EOF expressions switching the data bank.
 r=BasicRig();r.files['IN']=bytearray(b'first\nsecond\n')
 for s in ['OPEN "I",1,"IN"','OPEN "O",2,"OUT"','OPEN "O",3,"THIRD"','PRINT#2,EOF(1);":";EOF(1)','INPUT#1,A$','PRINT#3,A$','CLOSE 2','LINE INPUT#1,A$','PRINT#3,A$','CLOSE']:
  r.statement(s)
 assert r.files['OUT']==b' 0 : 0 \r\n'
 assert r.files['THIRD']==b'first\r\nsecond\r\n'
 assert not r.handles

 # Exact output bytes, semicolons, comma zones, blank output and overwrite.
 r=BasicRig();r.files['OUT']=bytearray(b'old contents longer than new')
 for s in ['OPEN "O",1,"OUT"','PRINT#1,"X";','PRINT#1,"Y", "Z"','PRINT#1,','CLOSE']:
  r.statement(s)
 assert r.files['OUT']==b'XY'+b' '*14+b'Z\r\n\r\n'

 # Arrays and strings survive garbage collection; 255-byte line boundary.
 r=BasicRig();r.statement('CLEAR 2000');r.statement('DIM A$(2)')
 r.files['LONG']=bytearray((b'x'*255+b'\r\n')*15)
 r.statement('OPEN "I",1,"LONG"')
 for i in range(15):
  r.statement('LINE INPUT#1,A$(1)')
  assert r.statement('PRINT LEN(A$(1))')==b' 255 \r'
 assert r.statement('PRINT EOF(1)')==b'-1 \r'
 r.statement('CLOSE')

 for text,code in [('OPEN "I",0,"X"',0x68),('OPEN "I",17,"X"',0x68),('OPEN "R",1,"X"',0x6c),('OPEN "I",1,"MISSING"',0x6a),('OPEN "O",1,""',0x80),('OPEN "O",1,"'+('X'*32)+'"',0x80),('PRINT#1,"X"',0x6c),('PRINT EOF(0)',0x68)]:
  expect_error(BasicRig(),text,code)
 r=BasicRig();r.statement('OPEN "O",1,"X"');r.statement('PRINT#1,"KEEP"')
 expect_error(r,'OPEN "O",1,"X"',0x6e)
 assert r.files['X']==b'KEEP\r\n'
 r.statement('CLOSE')
 for content,statement,code in [(b'no number','INPUT#1,A',0x2a),(b'12abc','INPUT#1,A',0x2a),(b'"unterminated','INPUT#1,A$',0x2a),(b'x'*256,'LINE INPUT#1,A$',0x1c),(b'','INPUT#1,A$',0x7c)]:
  r=BasicRig();r.files['BAD']=bytearray(content);r.statement('OPEN "I",1,"BAD"')
  expect_error(r,statement,code)

 # ROM lifecycle close hook must restore code AND data banks: LOAD calls
 # ROM SCRTCH/RUNC from a banked overlay before returning into that overlay.
 r=BasicRig();r.statement('OPEN "O",1,"X"');r.statement('OPEN "O",2,"Y"')
 r.write(0x37f0,base.symbol('PAGE_OVERLAYB'))
 r.write(0x37f1,32);r.m.hl=0x1234;r.m.de=0x5678;r.m.bc=0xabcd
 r.call(0x41bb)
 assert not r.handles and r.dpage==32
 assert r.page==base.symbol('PAGE_OVERLAYB'),'Lifecycle hook lost the loader code bank'
 assert not r.page_returns
 assert (r.m.hl,r.m.de,r.m.bc)==(0x1234,0x5678,0xabcd)
 # Run a complete BASIC program, including FOR/NEXT, IF/EOF and END.
 r=BasicRig()
 result=r.program([(10,'OPEN "O",1,"ROUND.DAT"'),(20,'FOR I=1 TO 5'),
  (30,'PRINT#1,I,I*2'),(40,'NEXT I'),(50,'CLOSE 1'),
  (60,'OPEN "I",1,"ROUND.DAT"'),(70,'IF EOF(1) THEN 110'),
  (80,'INPUT#1,A,B'),(90,'PRINT A;B'),(100,'GOTO 70'),(110,'END')])
 assert result==b' 1  2 \r 2  4 \r 3  6 \r 4  8 \r 5  10 \r',result
 assert not r.handles

 # Disk error injection: use the actual API wait's FatFS/TRSDOS mapping.
 for raw,expected in [(4,0x6a),(5,0x6a),(7,0x8a),(10,0x88),(0x40|27,0x7a),(1,0x72)]:
  r=BasicRig();original=r.outp
  def fail_open(port,value):
   original(port,value)
   if r.command==0x14 and len(r.args)==36:
    r.status=0x41;r.error=raw;r.handles.clear();r.data.clear()
  r.m.set_output_callback(fail_open)
  expect_error(r,'OPEN "O",1,"BAD"',expected)
  r.write(0x37f1,1);assert r.mem[0x3620]==0
 r=BasicRig();r.statement('OPEN "O",1,"BAD"');original=r.outp
 def fail_write(port,value):
  if port&255==0xc2 and r.command==0x21:r.status=0x41;r.error=1;return
  original(port,value)
 r.m.set_output_callback(fail_write)
 expect_error(r,'PRINT#1,"FAIL"',0x72)
 assert r.files['BAD']==b''
 # Execute the hardware smoke program and export a tokenized LOADable copy.
 r=BasicRig()
 lines=[(int(number),text) for number,text in (line.split(' ',1) for line in (root/'tests/IOCHECK.txt').read_text().splitlines() if line)]
 assert r.program(lines)==b'BASIC FILE I/O PASS\r'
 assert not r.handles
 start=int.from_bytes(r.mem[0x40a4:0x40a6],'little')
 end=int.from_bytes(r.mem[0x40f9:0x40fb],'little')
 program=b'\xff'+bytes(r.mem[start:end])
 assert program.endswith(b'\0\0\0')
 (base.BUILD/'SD-CARD/IOCHECK.BAS').write_bytes(program)
 return {'basic_file_io':'PASS: real ROM parsing/evaluation, typed variables, arrays/GC, three files, EOF lookahead, CR/LF, boundaries, error cases and close lifecycle',
 'scope':'Pico file API and ROM console are simulated; physical firmware timing still needs hardware testing.'}


def review_regressions():
 # Exercise every slot at once, including firmware handle 0 and BASIC 16.
 r=BasicRig();r.write(0x37f1,0);r.mem[0x3600:0x37e0]=bytes([0x5a])*480
 for i in range(1,17):
  r.statement(f'OPEN "O",{i},"F{i}"')
  r.statement(f'PRINT#{i},"SLOT{i}"')
 assert len(r.handles)==16
 r.statement('CLOSE 16');r.statement('OPEN "I",16,"F16"')
 r.statement('LINE INPUT#16,A$');assert r.statement('PRINT A$')==b'SLOT16\r'
 assert r.statement('PRINT EOF(16)')==b'-1 \r'
 expect_error(r,'OPEN "O",17,"BAD"',0x68)
 expect_error(r,'PRINT EOF(17)',0x68)
 r.statement('CLOSE');assert not r.handles
 r.write(0x37f1,0);assert bytes(r.mem[0x3600:0x37e0])==bytes([0x5a])*480
 for i in range(1,17):assert r.files[f'F{i}']==f'SLOT{i}\r\n'.encode()

 # Call actual ROM _GET/_PUT with a normal-RAM FCB, outside BASIC banks.
 # @INIT must retain existing contents; @OPEN must fail on a missing file.
 r=BasicRig();r.files['RAW']=bytearray(b'old')
 fcb=0x7000;buf=0x7100
 def open_dos(name,entry):
  r.mem[fcb:fcb+32]=name.encode().ljust(32,b'\0')
  r.m.de=fcb;r.m.hl=buf;r.m.b=1;r.call(entry)
 open_dos('MISSING',0x4424);assert not r.m.f&0x40 and r.m.a==24
 open_dos('RAW',0x4420);assert r.m.f&0x40 and r.files['RAW']==b'old'
 r.m.de=fcb;r.call(0x4428);assert r.m.f&0x40
 open_dos('BYTES',0x4420);assert r.m.f&0x40
 r.write(0x37f0,base.symbol('PAGE_BIO_PRINT'));r.write(0x37f1,32)
 for byte in b'A\r\nZ':
  r.m.a=byte;r.m.de=fcb;r.m.hl=0x1234;r.m.bc=0x5678;r.m.ix=0x789a
  r.call(0x1b)
  assert r.m.f&0x40
  assert (r.m.de,r.m.hl,r.m.bc,r.m.ix)==(fcb,0x1234,0x5678,0x789a)
  assert r.page==base.symbol('PAGE_BIO_PRINT') and r.dpage==32 and not r.page_returns
 assert r.files['BYTES']==b'A\r\nZ'
 r.m.de=fcb;r.call(0x4428);assert r.m.f&0x40
 open_dos('BYTES',0x4424);assert r.m.f&0x40
 for byte in b'A\r\nZ':
  r.m.de=fcb;r.m.hl=0x1234;r.m.bc=0x5678;r.m.ix=0x789a;r.call(0x13)
  assert r.m.f&0x40 and r.m.a==byte
  assert (r.m.de,r.m.hl,r.m.bc,r.m.ix)==(fcb,0x1234,0x5678,0x789a)
 r.m.de=fcb;r.call(0x13);assert not r.m.f&0x40 and r.m.a==28
 r.mem[fcb+9]=0;r.m.de=fcb;r.call(0x13)
 assert not r.m.f&0x40 and r.m.a==61 # buffering is explicitly unsupported
 r.mem[fcb+9]=1;r.m.de=fcb;r.call(0x4428)

 # A failed CLOSE must preserve the local open state for a later retry.
 r=BasicRig();r.statement('OPEN "O",1,"CLOSEERR"');original=r.outp
 def fail_close(port,value):
  if port&255==0xc4 and value==0x15:
   r.command=value;r.status=0x41;r.error=1;r.data.clear();return
  original(port,value)
 r.m.set_output_callback(fail_close)
 expect_error(r,'CLOSE 1',0x72)
 r.write(0x37f1,1);assert r.mem[0x3620]==ord('O') and r.handles
 r.m.set_output_callback(original);r.statement('CLOSE 1');assert not r.handles

 # Shared ROM dispatch must still restore banked callers for nested INSTR
 # and EOF expressions in filename/file-number/subscript positions.
 r=BasicRig();r.files['NEST']=bytearray(b'12\n')
 r.statement('OPEN "I",INSTR("A","A"),"NEST"')
 r.statement('DIM A(2)');r.statement('INPUT#1,A(1+EOF(1))')
 assert r.statement('PRINT A(1)')==b' 12 \r'
 r.statement('CLOSE')
 return {'review_regressions':'PASS: 16 slots, slot bounds, page 0 intact, public DOS OPEN/INIT/CLOSE, ROM GET/PUT with RAM FCB, registers/banks, raw CR/LF, EOF, nested ROM evaluation'}

if __name__=='__main__':
 if not os.environ.get('KDOS_TEST_ROM'):raise SystemExit('Set KDOS_TEST_ROM to a Model I Level II-compatible ROM file; see tests/README.txt.')
 report=tests()|basic_loader_tests()|review_regressions()
 (base.BUILD/'basic-io-test-results.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
