// Box.asm      Roll No 2501730373      K = 73
// Start row    = K = 73  (rows 73 .. 92)
// Height       = 20 rows
// Width        = 16 * ((73 mod 4) + 1) = 16 * 2 = 32 pixels = 2 words per row
// First word   = SCREEN + 32*73 = 16384 + 2336 = 18720
// Box is black while any key is pressed, white (erased) when released.

(MAIN)
    @color
    M=0             // assume no key: erase
    @KBD
    D=M
    @DRAW
    D;JEQ           // KBD = 0 -> keep colour 0
    @color
    M=-1            // key pressed -> black

(DRAW)
    @18720
    D=A
    @ptr
    M=D             // ptr -> first word of row 73
    @20
    D=A
    @n
    M=D             // 20 rows to go

(NEXTROW)
    @color
    D=M
    @ptr
    A=M
    M=D             // word 0: pixels 0-15
    A=A+1
    M=D             // word 1: pixels 16-31
    @32
    D=A
    @ptr
    M=D+M           // ptr += 32 (same word, next row)
    @n
    MD=M-1
    @NEXTROW
    D;JGT           // rows left?
    @MAIN
    0;JMP
