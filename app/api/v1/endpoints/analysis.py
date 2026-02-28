from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.api import deps
from app.models.user import User
from app.models.analysis import Analysis, AnalysisRead
from app.services.ai_service import ai_service
from app.db.session import get_session

router = APIRouter()

@router.post("/cbc", response_model=AnalysisRead)
def analyze_cbc(
    data: Dict[str, float],
    db: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user)
):
    try:
        prediction_results = ai_service.predict_cbc(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")
    
    analysis = Analysis(
        user_id=current_user.id,
        analysis_type="CBC",
        input_data=data,
        result_data=prediction_results
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

@router.get("/history", response_model=List[AnalysisRead])
def get_analysis_history(
    db: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user)
):
    statement = select(Analysis).where(Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc())
    results = db.exec(statement).all()
    return results

@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user)
):
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return analysis
