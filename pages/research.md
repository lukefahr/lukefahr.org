
## FPGA Bitstream Security

Field-Programmable Gate Arrays (FPGAs) are reprogrammable hardware whose
functionality is specified by a binary configuration file, or bitstream.
However, FPGAs are vulnerable to **malicious bitstream
modification**, where the intended bitstream is modified to insert a
trojan or other unwanted functionality.  
Modern bitstreams are signed and encrypted, but have still proven vulnerable to
modifications.  

Our research is focused on ensuring the integrity of the bitstream through
verification and defensive measures.  We've designed FPGA bitstreams that
include thermal watermarks, or that dynamically overwrite any malicious
modifications.  

{ [HOST'19](papers/duncan_host19.pdf) | [VTS'20](papers/duncan_vts20.pdf)}

## FPGA Piracy Detection

FPGA bitstreams often contain valuable Intellectual Property (IP), creating
incentive for IP theft. This research project is focused
on automatically detecting pirated IP in FPGA using only extracted bitstreams. 

{ [PAINE'20](papers/skipper_paine20.pdf) }

## Emerging Non-volatile FPGA Architectures

90% of the FPGAs sold today are based on SRAM, a volatile memory that looses all state if
powered down. A new wave of emerging non-volatile technologies are competing to
replace SRAM for FPGAs, i.e. ReRAM, MRAM, etc.  Our group is studying how these
new non-volatile memory technologies can be used to improve the performance and
security of FPGA architectures.  



