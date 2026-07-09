from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
#from app.models.student_profile import Student
#from app.schemas.student_profile import StudentCreate, StudentRead

#router = APIRouter(prefix="/students", tags=["students"])


#@router.post("", response_model=StudentRead, status_code=201)
#def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
#    student = Student(**student_data.model_dump())
#
#    db.add(student)
#    db.commit()
#    db.refresh(student)
#
#    return student


#@router.get("/{student_id}", response_model=StudentRead)
#def get_student(student_id: int, db: Session = Depends(get_db)):
#    student = db.get(Student, student_id)
#
#    if student is None:
#        raise HTTPException(status_code=404, detail="Student not found")
#
#    return student


#@router.get("", response_model=list[StudentRead])
#def get_students(db: Session = Depends(get_db)):
#    return db.query(Student).order_by(Student.id).all()