
(CHECK)
    @KBD
    D=M
    @BLACK
    D;JNE

(WHITE)
    @R2
    M=0
    @DRAW
    0;JMP

(BLACK)
    @R2
    M=-1

(DRAW)
    @18304
    D=A
    @R0
    M=D

    @20
    D=A
    @R1
    M=D

(LOOP)
    @R2
    D=M
    @R0
    A=M
    M=D

    @32
    D=A
    @R0
    M=D+M

    @R1
    MD=M-1
    @LOOP
    D;JGT

    @CHECK
    0;JMP
