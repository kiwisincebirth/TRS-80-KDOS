



This is a sophisticated approach to overcoming the memory limitations of the TRS-80 (Z80) by using an RP2350 as an "intelligent" memory bridge. The design essentially creates a Hardware-Assisted Virtual Memory system that manages bank-switching automatically, which is a massive quality-of-life improvement over traditional manual bank-switching.

## High-Level Architecture: The "Smart Trampoline"

### Memory Map

The system utilizes the standard TRS-80 2KB "memory hole" ($3000–$37FF) to interface with the RP2350.

* Trampoline Area ($3000–$33FF): Contains 256 "slots" (4 bytes each). Each slot corresponds to a specific 512-byte memory bank.
* Paged Window ($3400–$35FF): A 512-byte view into the currently active bank.
* Static Scratch RAM ($3600–$37DF): "Common Ground" RAM that is visible regardless of which page is active, used for interrupts and parameter passing.
* Static Scratch RAM ($37F0–$37F1): "Control Registers" control registers for manual management.

### Trampoline area

* Learning the Opcode: During a write operation to offset 0, the code checks if the value is 0xC3 (JP). If not, it defaults to 0xCD (CALL). This allows standard loaders to "program" the hardware's behavior.

* The Implicit Push: When a read occurs at offset 0 and the slot is marked as a CALL, the code saves the currentPage to stack.

* The Auto-Restore (The Second RET): When the Z80 reads offset 3 (the address it returns to after the routine at $3400 finishes), your code restores the previous currentPage before feeding the Z80 the RET opcode ($C9).

### 

### The Logic Flow: Implicit Paging

The brilliance of this design is that the Z80 doesn't "know" it's switching banks. The RP2350 monitors the address bus and changes the environment in real-time.

The "Double RET" Sequence When the Z80 calls a routine via the trampoline:
* Entry: Z80 calls an address in the $3000 range (e.g., $3000).
* Trigger: The RP2350 sees this read, pushes the currentPage onto an internal Hardware Page Stack (Ring Buffer), and switches to the new page.
* Redirection: The RP2350 feeds the Z80 a CALL $3400 opcode.
* Execution: The Z80 runs the code at $3400 in the new bank.
* Return 1: The routine ends with a RET, jumping the Z80 back to the 4th byte of the trampoline slot (e.g., $3003).
* Return 2: The RP2350 sees the read at $3003, pops the previous page from the stack, and feeds the Z80 another RET ($C9).
* Result: The Z80 is back in the original calling code with the original page restored.



## Critical Implementation Details

### Handling JP (Jump) vs CALL

To prevent the internal hardware stack from overflowing, the system distinguishes between a CALL (round-trip) and a JP (one-way).
* CALL (0xCD): Increments the stack pointer to allow for nesting (reentrancy).
* JP (0xC3): Switches the page but does not push to the stack, which is ideal for exiting to DOS or terminal jumps.

### Performance

* Speed: Adding an extra CALL/RET pair adds roughly 27 T-states (~15 microseconds at 1.77MHz), a negligible cost for automatic management.
* Wait States: The RP2350 uses GPIO bit-banging and Wait States to "freeze" the Z80 while it processes memory cycles, making its internal operations invisible to the Z80.

### Memory

* Stack Space: Adding an extra CALL/RET pair adds 2 bytes per virtual call, again negligible cost for automatic management.

### Registers

The following registers are provided
* 37F0 is the current page register which allows manually reads and writes.
* 37F1 is a command register, writing to this address will affect the operation of virtual memory

## Potential Pitfalls to Watch

* Interrupts: If an ISR uses the $3000 trampoline while the main program is mid-trampoline, the stack could get out of sync.
    * Fix: Disable interrupts during trampoline execution
    * or ensure ISRs avoid that range.

* Direct Memory Access: Range $3000–$33FF is no longer general-purpose memory; it must be treated strictly as the trampoline area.
