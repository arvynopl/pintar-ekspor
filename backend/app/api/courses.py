# backend/app/api/courses.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.base import get_db
from ..models.course import Course
from ..models.progress import UserProgress
from ..models.user import User, UserRole
from ..schemas.course import CourseCreate, CourseUpdate, Course as CourseSchema
from ..schemas.progress import UserProgressCreate
from .deps import (
    get_current_user, 
    get_current_admin, 
    get_current_public_user,
    get_user_with_role
)

router = APIRouter()

@router.post("/", response_model=CourseSchema)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)  # Only admin can create
):
    """
    Create a new course (Admin-only endpoint)
    
    Args:
        course (CourseCreate): Course creation details
        db (Session): Database session
        admin (User): Authenticated admin user
    
    Returns:
        CourseSchema: Created course details
    """
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/", response_model=List[CourseSchema])
async def list_courses(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_public_user)  # All authenticated users can view
):
    """
    List courses with pagination
    
    Args:
        skip (int): Number of courses to skip
        limit (int): Maximum number of courses to return
        db (Session): Database session
        current_user (User): Authenticated user
    
    Returns:
        List[CourseSchema]: List of courses
    """
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.get("/{course_id}", response_model=CourseSchema)
async def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_public_user)  # Only requires authenticated user
):
    """
    Retrieve a specific course by ID
    
    Args:
        course_id (int): ID of the course to retrieve
        db (Session): Database session
        current_user (User): Authenticated user
    
    Returns:
        CourseSchema: Course details
    
    Raises:
        HTTPException: If course is not found
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course

@router.put("/{course_id}", response_model=CourseSchema)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)  # Only admin can update
):
    """
    Update an existing course (Admin-only endpoint)
    
    Args:
        course_id (int): ID of the course to update
        course_update (CourseUpdate): Update details
        db (Session): Database session
        admin (User): Authenticated admin user
    
    Returns:
        CourseSchema: Updated course details
    
    Raises:
        HTTPException: If course is not found
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Update only provided fields
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)  # Only admin can delete
):
    """
    Delete a course (Admin-only endpoint)
    
    Args:
        course_id (int): ID of the course to delete
        db (Session): Database session
        admin (User): Authenticated admin user
    
    Returns:
        dict: Deletion confirmation message
    
    Raises:
        HTTPException: If course is not found
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    db.delete(db_course)
    db.commit()
    return {"message": "Course deleted successfully"}

@router.post("/{course_id}/progress")
async def update_progress(
    course_id: int,
    progress: UserProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_public_user)
):
    """
    Update user progress for a specific course
    
    Args:
        course_id (int): ID of the course
        progress (UserProgressCreate): Progress update details
        db (Session): Database session
        current_user (User): Authenticated user
    
    Returns:
        dict: Progress update confirmation
    
    Raises:
        HTTPException: If course is not found
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if progress record exists
    db_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.course_id == course_id
    ).first()
    
    if db_progress:
        # Update existing progress
        db_progress.completed = progress.completed
    else:
        # Create new progress record
        db_progress = UserProgress(
            user_id=current_user.id,
            course_id=course_id,
            completed=progress.completed
        )
        db.add(db_progress)
    
    db.commit()
    return {"message": "Progress updated successfully"}

@router.get("/{course_id}/progress")
async def get_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_public_user)
):
    """
    Retrieve user progress for a specific course
    
    Args:
        course_id (int): ID of the course
        db (Session): Database session
        current_user (User): Authenticated user
    
    Returns:
        dict: User's progress status for the course
    """
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.course_id == course_id
    ).first()
    
    if not progress:
        return {"completed": False}
    
    return {"completed": progress.completed}