#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
MCE Ryzen Decoder for AMD 17h (23) family.
$ cat /proc/cpuinfo | grep family

Developed by Dimitri Fourny.

From the documentation:
    1.  Read the values of this bank's MCA_IPID and MCA_STATUS registers.
    2.  Use 3.17.3 [Hardware IDs and McaType] to look up the block associated with the values of MCA_IPID[HwId]
    and MCA_IPID[McaType].
    3.  In 3.17.4 [MCA Banks], find the sub-section associated with the block in error.
    4.  In this sub-section, find the MCA_STATUS table.
    5.  In the table, look up the row associated with the MCA_STATUS[ErrorCodeExt] value.
    6.  The error type in this row is the logged error. The MCA_STATUS, MCA_ADDR and MCA_SYND tables contain
    information associated with this error.
    7.  If there is an error in both MCA_STATUS and MCA_DESTAT, the registers contain the same error if
    MCA_STATUS[Deferred] is set. If MCA_STATUS[Deferred] is not set, MCA_DESTAT contains information for
    a different error than MCA_STATUS. MCA_DESTAT does not contain an ErrorCodeExt field, so in this case it is
    not possible to determine the type of error logged in MCA_DESTAT
'''

import sys


class ErrorCodeExt:
    def __init__(self, code, acronym, description):
        self.code = code
        self.acronym = acronym
        self.description = description

    def __str__(self):
        return "{} ({} 0x{:x})".format(self.description, self.acronym, self.code)

class Block:
    def __init__(self):
        self._pos_error_high = 21
        self._pos_error_low = 16

    def _extract_error_code_ext(self, status):
        mask = (1<<(self._pos_error_high))-1 & ~((1<<self._pos_error_low)-1)
        return (mask & status) >> self._pos_error_low

    def decode_error(self, status):
        code = self._extract_error_code_ext(status)
        acronym = ""
        if code < len(self._errors_acronyms):
            acronym = self._errors_acronyms[code]
        description = ""
        if acronym in self._errors_descriptions:
            description = self._errors_descriptions[acronym]
        return ErrorCodeExt(code, acronym, description)

    def __str__(self):
        return "{} ({})".format(self._description, self._acronym)

class BlockRAZ(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "RAZ"
        self._description = "Read-As-Zero"
        self._errors_acronyms = []
        self._errors_descriptions = {}

class BlockReserved(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "Reserved"
        self._description = "Reserved"
        self._errors_acronyms = []
        self._errors_descriptions = {}

class BlockLS(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "LS"
        self._description = "Load-Store Unit"
        self._errors_acronyms = [
            "LDQ", "STQ", "MAB", "L1DTLB", "DcTagErr5", "DcTagErr6", "DcTagErr1",
            "IntErrTyp1", "IntErrTyp2", "SystemReadDataErrorT0", "SystemReadDataErrorT1",
            "DcTagErr2", "DcDataErr1", "DcDataErr2", "DcDataErr3", "DcTagErr4", "L2DTLB",
            "PDC", "DcTagErr3", "DcTagErr7", "L2DataErr"
        ]
        self._errors_descriptions = {
            "L2DataErr": "L2 Fill Data error",
            "DcTagErr7": "DC Tag error type 7",
            "DcTagErr5": "DC Tag error type 5",
            "DcTagErr3": "DC Tag error type 3",
            "PDC": "MCA_ADDR_LS logs a virtual address",
            "L2DTLB": "MCA_ADDR_LS logs a virtual address",
            "DcTagErr4": "DC Tag error type 4",
            "DcDataErr3": "DC Data error type 3",
            "DcDataErr2": "DC Data error type 2",
            "DcDataErr1": "DC Data error type 1 and poison consumption MCA_STATUS[Poison] is set on poison consumption from L2/L3",
            "DcTagErr2": "DC Tag error type 2",
            "SystemReadDataErrorT1": "System Read Data Error Thread 1An error in a read of a line from the data fabric",
            "SystemReadDataErrorT0": "System Read Data Error Thread 0An error in a read of a line from the data fabric",
            "IntErrTyp2": "Internal error type 2",
            "IntErrTyp1": "Internal error type 1",
            "DcTagErr1": "DC Tag error type 1",
            "DcTagErr6": "DC Tag error type 6",
            "L1DTLB": "Level 1 TLB parity error",
            "MAB": "Miss address buffer payload parity error",
            "STQ": "Store queue parity error",
            "LDQ": "Load queue parity error"
        }

class BlockIF(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "IF"
        self._description = "Instruction Fetch Unit"
        self._errors_acronyms = [
            "OcUtagParity", "TagMultiHit","TagParity", "DataParity","DqParity",
            "L0ItlbParity", "L1ItlbParity", "L2ItlbParity", "BpqSnpParT0", "BpqSnpParT1",
            "L1BtbMultiHit", "L2BtbMultiHit", "L2RespPoison", "SystemReadDataError"
        ]
        self._errors_descriptions = {
            "SystemReadDataError": "System Read Data Error. An error in a demand fetch of a line",
            "L2RespPoison": "L2 Cache Response Poison Error. Error is the result of consuming poison data",
            "L2BtbMultiHit": "L2 BTB Multi-Match Error",
            "L1BtbMultiHit": "L1 BTB Multi-Match Error",
            "BpqSnpParT1": "BPQ Thread 1 Snoop Parity Error",
            "BpqSnpParT0": "BPQ Thread 0 Snoop Parity Error",
            "L2ItlbParity": "L2 ITLB Parity Error",
            "L1ItlbParity": "L1 ITLB Parity Error",
            "L0ItlbParity": "L0 ITLB Parity Error",
            "DqParity": "Decoupling Queue PhysAddr Parity Error",
            "DataParity": "IC Data Array Parity Error",
            "TagParity": "IC Full Tag Parity Error",
            "TagMultiHit": "IC Microtag or Full Tag Multi-hit Error",
            "OcUtagParity": "Op Cache Microtag Probe Port Parity Error"
        }

class BlockL2(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "L2"
        self._description = "L2 Cache Unit"
        self._errors_acronyms = [
            "MultiHit", "Tag", "Data", "Hwa"
        ]
        self._errors_descriptions = {
            "Hwa" : "Hardware Assert Error",
            "Data" : "L2M Data Array ECC Error",
            "Tag" : "L2M Tag or State Array ECC Error",
            "MultiHit" : "L2M Tag Multiple-Way-Hit error"
        }

class BlockDE(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "DE"
        self._description = "Decode Unit"
        self._errors_acronyms = [
            "OcTag", "OcDat", "Ibq", "UopQ",
            "Idq", "Faq", "UcDat", "UcSeq", "OCBQ"
        ]
        self._errors_descriptions = {
            "OCBQ" : "Micro-op buffer parity error",
            "UcSeq" : "Patch RAM sequencer parity error",
            "UcDat" : "Patch RAM data parity error",
            "Faq" : "Fetch address FIFO parity error",
            "Idq" : "Instruction dispatch queue parity error",
            "UopQ" : "Micro-op queue parity error",
            "Ibq" : "Instruction buffer parity error",
            "OcDat" : "Micro-op cache data parity error",
            "OcTag" : "Micro-op cache tag parity error",
        }

class BlockEX(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "EX"
        self._description = "Execution Unit"
        self._errors_acronyms = [
            "WDT", "PRF", "FRF", "IDRF", "PLDAG", "PLDAL",
            "CHKPTQ", "RETDISP", "STATQ", "SQ", "BBQ"
        ]
        self._errors_descriptions = {
            "BBQ" : "Branch buffer queue parity error",
            "SQ" : "Scheduling queue parity error",
            "STATQ" : "Retire status queue parity error.",
            "RETDISP" : "Retire dispatch queue parity error",
            "CHKPTQ" : "CHKPTQ. Checkpoint queue parity error",
            "PLDAL" : "EX payload parity error",
            "PLDAG" : "Address generator payload parity error",
            "IDRF" : "Immediate displacement register file parity error",
            "FRF" : "Flag register file parity error",
            "PRF" : "Physical register file parity error",
            "WDT" : "Watchdog Timeout error"
        }

class BlockFP(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "FP"
        self._description = "Floating Point Unit"
        self._errors_acronyms = [
            "PRF", "FL", "SCH",
            "NSQ", "RQ", "SRF", "HWA"
        ]
        self._errors_descriptions = {
            "HWA" : "Hardware assertion",
            "SRF" : "Status register file (SRF) parity error",
            "RQ" : "Retire queue (RQ) parity error",
            "NSQ" : "NSQ parity error",
            "SCH" : "Schedule queue parity error",
            "FL" : "Freelist (FL) parity error",
            "PRF" : "Physical register file (PRF) parity error"
        }

class BlockL3(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "EX"
        self._description = "L3 Cache Unit"
        self._errors_acronyms = [
            "ShadowTag", "MultiHitShadowTag", "Tag",
            "MultiHitTag", "DataArray", "SdpParity",
            "XiVictimQueue", "Hwa"
        ]
        self._errors_descriptions = {
            "Hwa" : "L3 Hardware Assertion",
            "XiVictimQueue" : "L3 Victim Queue Parity Error",
            "SdpParity" : "SDP Parity Error from XI",
            "DataArray" : "L3M Data ECC Error",
            "MultiHitTag" : "L3M Tag Multi-way-hit Error",
            "Tag" : "L3M Tag ECC Error",
            "MultiHitShadowTag" : "Shadow Tag Macro Multi-way-hit Error",
            "ShadowTag" : "Shadow Tag Macro ECC Error"
        }

class BlockUMC(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "UMC"
        self._description = "Unified Memory Controller"
        self._errors_acronyms = [
            "DramEccErr", "WriteDataPoisonErr", "SdpParityErr",
            "ApbErr", "AddressCommandParityErr", "WriteDataCrcErr"
        ]
        self._errors_descriptions = {
            "WriteDataCrcErr" : "Write data CRC error. A write data CRC error on the DRAM data bus",
            "AddressCommandParityErr" : "Address/command parity error. A parity error on the DRAM address/command bus",
            "ApbErr" : "Advanced peripheral bus error. An error on the advanced peripheral bus",
            "SdpParityErr" : "SDP parity error. A parity error on write data from the data fabric",
            "WriteDataPoisonErr" : "Data poison error",
            "DramEccErr" : "DRAM ECC error. An ECC error on a DRAM read"
        }

class BlockPB(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "PB"
        self._description = "Parameter Block"
        self._errors_acronyms = ["EccError"]
        self._errors_descriptions = {"EccError" : "An ECC error in the Parameter Block RAM array",}

class BlockCS(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "CS"
        self._description = "Coherent Slave"
        self._errors_acronyms = [
            "FTI_ILL_REQ", "FTI_ADDR_VIOL", "FTI_SEC_VIOL",
            "FTI_ILL_RSP", "FTI_RSP_NO_MTCH", "FTI_PAR_ERR",
            "SDP_PAR_ERR", "ATM_PAR_ERR", "SPF_ECC_ERR"
        ]
        self._errors_descriptions = {
            "SPF_ECC_ERR" : "Probe Filter ECC Error: An ECC error occurred on a probe filter access",
            "ATM_PAR_ERR" : "Atomic Request Parity Error: Parity error on read of an atomic transaction",
            "SDP_PAR_ERR" : "Read Response Parity Error: Parity error on incoming read response data",
            "FTI_PAR_ERR" : "Request or Probe Parity Error: Parity error on incoming request or probe response data",
            "FTI_RSP_NO_MTCH" : "Unexpected Response: A response was received from the transport layer which does not match any request",
            "FTI_ILL_RSP" : "Illegal Response: An illegal response was received from the transport layer",
            "FTI_SEC_VIOL" : "Security Violation: A security violation was received from the transport layer",
            "FTI_ADDR_VIOL" : "Address Violation: An address violation was received from the transport layer",
            "FTI_ILL_REQ" : "Illegal Request: An illegal request was received from the transport layer"
        }

class BlockPIE(Block):
    def __init__(self):
        Block.__init__(self)
        self._acronym = "PIE"
        self._description = "Power Management, Interrupts, Etc."
        self._errors_acronyms = [
            "HW_ASSERT", "CSW", "GMI", "FTI_DAT_STAT"
        ]
        self._errors_descriptions = {
            "FTI_DAT_STAT" : "Poison data consumption: Poison data was written to an internal PIE register",
            "GMI" : "Link Error: An error occurred on a GMI or xGMI link",
            "CSW" : "Register security violation: A security violation was detected on an access to an internal PIE register",
            "HW_ASSERT" : "Hardware Assert: A hardware assert was detected"
        }

BANKS = [
    BlockLS,
    BlockIF,
    BlockL2,
    BlockDE,
    BlockRAZ,
    BlockEX,
    BlockFP,
    BlockL3,
    BlockL3,
    BlockL3,
    BlockL3,
    BlockL3,
    BlockL3,
    BlockL3,
    BlockL3,
    BlockUMC,
    BlockUMC,
    BlockReserved,
    BlockReserved,
    BlockPB,
    BlockCS,
    BlockCS,
    BlockPIE,
]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: {} <bank_number> <status_code>".format(sys.argv[0]))
        exit(1)

    bank_number = int(sys.argv[1])
    status_code = int(sys.argv[2], 16)
    bank = BANKS[bank_number]()
    print("Bank: {}".format(bank))
    error = bank.decode_error(status_code)
    print("Error: {}".format(error))
