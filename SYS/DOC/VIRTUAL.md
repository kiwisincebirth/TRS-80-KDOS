
# Virtual Memory Design

This is an approach to overcoming the memory limitations of the TRS-80 
(Z80) by using an RP2350 as an "intelligent" memory controller. 
The design manages bank-switching automatically.

## High Level Overview

The system utilizes the standard TRS-80 2KB "memory hole" ($3000–$37FF) to provide
128KB of paged RAM organised into 256 x 512-byte memory pages.

These pages are primarily designed to act as partitioned RAM specifically for 
the purpose of providing functional code, not for storing large data blocks.

* Each 512 byte page is designed to contain a single function
* Each paged function can only have a single entry point. 
* A paged function may contain sub-functions determined by parameter passing
* A paged function can CALL or JP to another paged function.

The (almost) 2KB is broken down into 2 important area's.

The first 1024-bytes (referred to as the Trampoline) acts as entry points 
into paged RAM, similar a jump "vector" table commonly used as entry points
for system functions. Each 4 byte entry in this area represents a unique
paged function, which you invoke by a call (or Jump) into the slot 

The next 512-bytes are the paged memory itself, and are switched implicitly
to align to the chosen virtual page function.

### The Flow

When the Z80 needs to call a paged routine it needs to:
* Entry: Z80 code Calls a paged function via its address in the Trampoline range (e.g., $3010).
* Trigger: The RP2350 sees this read, pushes the current Page number onto an internal Stack 
  (Ring Buffer), and switches the current page based on the trampoline address.
* Redirection: The RP2350 provides the CALL $3400 instruction, via 3 bytes (e.g. $3010-$3012) 
* Execution: The Z80 runs the user code at $3400 in the selected Page
* Return 1: The user routine ends with a RET, returning to the 4th byte of the trampoline slot (e.g. $3013).
* Unwind: The RP2350 sees the read at $3013, restores the current page from the value saved in the stack
* Return 2: The RP2350 provides the RET instruction, via byte (e.g. $3013)
* Result: The Z80 is back in the original calling code with the original page restored.

## High-Level Details

### Memory Map

The memory in the range ($3000–$37FF) is broken down in the following way
* Trampoline Area ($3000–$33FF): Contains 256 "slots" (4 bytes each). Each slot corresponds to a specific 512-byte memory bank.
* Main Paged RAM ($3400–$35FF): A 512-byte view into the currently active memory bank.
* Extra Paged RAM ($3600–$37DF): "Common Ground" RAM that is visible regardless of which page is active.
* Reserved ($37E0=$37EF): Reserved for floppy and printer devices, not mapped by this solution. 
* Control Registers ($37F0–$37FF): "Control Registers" control registers for manual management.

### Trampoline area

The trampoline Area contain 256 - 4 byte slots. Each slot corresponds to a specific 512-byte memory bank. 

The 4 bytes are defined as
* Offset 0 - R/W - Contains opcode for CALL or JP
* Offset 1 - R/O - Contains LSB of address $3400
* Offset 2 - R/O - Contains MSB of address $3400
* Offset 3 - R/O - Contains opcode for RET

The RP2350 performs the following logic when accessing the bytes
* Offset 0 : R/W : Will set the current page register based on the slot being accessed.
* Offset 0 : Read : If the byte returned is a 0xCD (CALL), then the page register (prior to change) will be
  pushed to a stack.
* Offset 0 : Write : Only 2 values are permitted, 0xC3 (JP), or the default 0xCD (CALL).
* Offset 3 : Read : The prior page (stored on stack) will be restored as the current page

### Control Registers

The following registers are provided
* 37F0 is the main Page register which allows manual reads and write.
* 37F1 is the extra RAM Page register, for manual read and write
* 37F8 is a command register, writing to this address will affect the operation of virtual memory

## Handling JP (Jump) vs CALL

To prevent the internal hardware stack from overflowing, the system distinguishes between a CALL (round-trip) and a JP (one-way).
* CALL (0xCD): Increments the stack pointer to allow for nesting (reentrancy).
* JP (0xC3): Switches the page but does not push to the stack, which is ideal for exiting to DOS or terminal jumps.

The following is an analysis of best approach for defining virtual memory pages

| Calling Code | Springboard  | Exit From VM | Unwind of the Virtual Page                   | Call Stack |     | 
|--------------|--------------|--------------|----------------------------------------------|------------|-----|
| JUMP         | JUMP         | JUMP         | GOOD. No expectation of unwind               | GOOD       | A # |
| JUMP         | JUMP         | RET          | ** OK. Expectation of unwind                 | GOOD       | C # |
| JUMP         | CALL (push)  | JUMP         | ** BAD **                                    | ** BAD **  | F-  |
| JUMP         | CALL (push)  | RET          | GOOD. Normal Ret from routine as final line  | GOOD       | A # |
| CALL         | JUMP         | JUMP         | ** OK. Future ret will bypass the unwind     | GOOD       | C   |
| CALL         | JUMP         | RET          | ** OK. Bypass unwind of Virtual Memory       | OK         | C - |
| CALL         | CALL (push)  | JUMP         | GOOD. Normal Call, future ret will unwind VM | GOOD       | A # |
| CALL         | CALL (push)  | RET          | GOOD. Normal Call/Ret pttern                 | GOOD       | A # |

Call to a Routine that Returns Only -> Make it a CALL
Call to a routine that Jumps Only   -> Make it a CALL
Call to a routine that RETs or JPs  -> Make it a CALL

Jump to a Routine that Returns Only -> Make it a CALL
Jump to a routine that jumps   Only -> Make it a Jump
Jump to a routine that RETs or JPs  -> Make it a Jump

A routine that changes the Stack    -> Make it a Jump

### In summary

Normally These should be set up as a CALL
* Any routine that You CALL
* Any code that ONLY exits via RET

Exceptions where a JUMP should be used
* Any code that directly manipulates the Stack
* Any code you Jump to that doesn't exclusivly RET

## Potential Pitfalls to Watch

### Performance

Adding an extra CALL/RET pair 
* adds roughly 27 T-states (~15 microseconds at 1.77MHz), a negligible cost for automatic management.
* adds 2 bytes per virtual call, again negligible cost for automatic management.

The RP2350 uses GPIO bit-banging and Wait States to "freeze" the Z80 while it processes memory cycles, 
making its internal operations invisible to the Z80.

### Interrupts

If an ISR uses the $3000 trampoline while the main program is mid-trampoline, the stack could get out of sync.
* Either disable interrupts during trampoline execution
* (or) ensure ISRs avoid that range.

### Direct Memory Access

Range $3000–$33FF is no longer general-purpose memory; it must be treated strictly as the trampoline area.
