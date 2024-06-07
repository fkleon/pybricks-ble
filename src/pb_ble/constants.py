from typing import Optional, Tuple, Union

PybricksData = Tuple[Union[bool, int, float, str, bytes]]
PybricksMessage = Tuple[int, Optional[PybricksData]]

LEGO_CID = 0x0397
"""LEGO System A/S company identifier."""
