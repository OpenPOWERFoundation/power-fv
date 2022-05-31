from ._storage import StorageSPRCheck


class LR   (StorageSPRCheck, name="cons_lr",   spr_name="lr"  ): pass
class CTR  (StorageSPRCheck, name="cons_ctr",  spr_name="ctr" ): pass
class XER  (StorageSPRCheck, name="cons_xer",  spr_name="xer" ): pass
class TAR  (StorageSPRCheck, name="cons_tar",  spr_name="tar" ): pass
class SRR0 (StorageSPRCheck, name="cons_srr0", spr_name="srr0"): pass
class SRR1 (StorageSPRCheck, name="cons_srr1", spr_name="srr1"): pass
