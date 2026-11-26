# Capstone - Make the Computer Draw a Box
Nand to Tetris - I (ETCNTC301), K.R. Mangalam University
Roll No: 2501730373 | **K = 73**

| Item | Value |
|---|---|
| K mod 3 = 1 | extra feature: clear error messages with line numbers (no crash) |
| K mod 4 = 1 | width = 16 x 2 = 32 pixels (2 words per row) |
| Start row | 73 (rows 73-92), height 20 |
| First screen address | 16384 + 32*73 = 18720 |

Files: `CPU.hdl`, `Memory.hdl`, `Computer.hdl`, `assembler.py`, `Box.asm`, `Box.hack`,
`tests/` (Add, Max, Rect, Pong .asm/.hack, plus `Bad.asm` / `Bad_output.txt` as evidence of the error feature).

Run: `python assembler.py Box.asm` -> `Box.hack`. Load `Box.hack` in the CPU Emulator, run at fast speed, hold any key.
