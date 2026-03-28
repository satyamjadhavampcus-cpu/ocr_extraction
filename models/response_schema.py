from pydantic import BaseModel
from typing import List, Optional

class CertificateData(BaseModel):
    organization: Optional[str] = None
    certificate_number: Optional[str] = None
    issued_date: Optional[str] = None
    expiry_date: Optional[str] = None
    naics: List[str] = []
    unspsc: List[str] = []