from pydantic import BaseModel

class AnalysisStats(BaseModel):
    malicious: int
    suspicious: int
    undetected: int
    failure: int
    type_unsupported: int

class CrowdsourcedStats(BaseModel):
    high: int
    medium: int
    low: int
    info: int

class FileData(BaseModel):
    last_analysis_stats: AnalysisStats
    crowdsourced_ids_stats: CrowdsourcedStats

class RiskResponse(BaseModel):
    malware_risk_percentage: float
    security_percentage: float

class UpdateVersionRequest(BaseModel):
    app_version: str = None  # Optional: Only update if provided
    cyber_version: str = None  # Optional: Only update if provided