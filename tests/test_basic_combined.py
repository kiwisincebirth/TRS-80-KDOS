"""Check CMD/KILL and sequential file I/O together using the real BASIC ROM.
The existing harnesses model board ports; all BASIC/DOS instructions execute.
Requires KDOS_TEST_ROM and the same dependency as the individual suites.
"""
import json
from test_basic_commands import CommandRig, base
from test_basic_io import BasicRig as IORig

class CombinedRig(CommandRig):
 def outp(self,port,value):
  p=port&255
  file_commands=(0x14,0x15,0x20,0x21)
  if p==0xc6 or (p==0xc4 and value in file_commands) or (p==0xc2 and self.command in file_commands):
   return IORig.outp(self,port,value)
  return super().outp(port,value)

def combined_test():
 r=CombinedRig()
 result=r.program([(10,'OPEN "O",1,"MERGE.DAT"'),
  (20,'PRINT#1,"BEFORE"'),(30,'CMD "PWD"'),(40,'PRINT#1,"AFTER"'),
  (50,'CLOSE 1'),(60,'OPEN "I",1,"MERGE.DAT"'),
  (70,'LINE INPUT#1,A$'),(80,'CMD "DIR"'),(90,'LINE INPUT#1,B$'),
  (100,'IF A$<>"BEFORE" OR B$<>"AFTER" THEN STOP'),
  (110,'CLOSE 1'),(120,'KILL "MERGE.DAT"'),
  (130,'PRINT "COMBINED PASS"'),(140,'END')])
 assert result.endswith(b'COMBINED PASS\r'),result
 assert 'MERGE.DAT' not in r.files and not r.handles and not r.page_returns
 return {'combined':'PASS: open file survives CMD PWD/DIR, continued write/read, CLOSE and KILL'}

if __name__=='__main__':
 report=combined_test()
 (base.BUILD/'basic-combined-test-results.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
