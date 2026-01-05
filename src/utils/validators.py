import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field

class TestStep(BaseModel):
    step_number: int
    action: str
    expected_result: str

class UseCase(BaseModel):
    title: str
    goal: str
    preconditions: List[str] = Field(default_factory=list)
    test_data: Dict[str, str] = Field(default_factory=dict)
    steps: List[TestStep]
    expected_results: List[str]
    negative_cases: List[str] = Field(default_factory=list)
    boundary_cases: List[str] = Field(default_factory=list)

class UseCaseOutput(BaseModel):
    use_cases: List[UseCase]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float
    retrieved_sources: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)

def validate_json_structure(data: Any) -> bool:
    try:
        UseCaseOutput(**data)
        return True
    except Exception:
        return False

def sanitize_output(data: Dict[str, Any]) -> Dict[str, Any]:
    if "use_cases" not in data:
        data["use_cases"] = []
    if "metadata" not in data:
        data["metadata"] = {}
    if "confidence_score" not in data:
        data["confidence_score"] = 0.0
    if "retrieved_sources" not in data:
        data["retrieved_sources"] = []
    if "warnings" not in data:
        data["warnings"] = []
    if "assumptions" not in data:
        data["assumptions"] = []
    return data