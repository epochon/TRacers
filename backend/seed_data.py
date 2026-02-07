"""
Seed Data Script for TRACE-AI
Creates labeled training data for accuracy evaluation
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import StudentEvent, User
from sqlalchemy import Column, Integer, String, Boolean, Table, MetaData

# Create labels table
metadata = MetaData()
labels_table = Table(
    'labels',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('student_id', Integer),
    Column('needs_intervention', Boolean)
)

# Create all tables
Base.metadata.create_all(bind=engine)
metadata.create_all(bind=engine)


def seed_student_data(db: Session):
    """
    Seed database with realistic labeled student data.
    
    Creates 25 students with varying risk profiles:
    - 10 high-risk (needs intervention = 1)
    - 10 low-risk (needs intervention = 0)
    - 5 moderate-risk (edge cases)
    """
    
    print("Seeding student data...")
    
    # Clear existing data
    db.query(StudentEvent).delete()
    db.execute(labels_table.delete())
    
    # Helper function to create events
    def create_events(student_id: int, event_configs: list):
        events = []
        base_time = datetime.utcnow() - timedelta(days=90)
        
        for i, config in enumerate(event_configs):
            event = StudentEvent(
                student_id=student_id,
                event_type=config['type'],
                severity=config['severity'],
                description=config['description'],
                timestamp=base_time + timedelta(days=config.get('days_offset', i * 7))
            )
            events.append(event)
        
        return events
    
    # HIGH RISK STUDENTS (needs_intervention = 1)
    
    # Student 1: Severe financial crisis
    events = create_events(1, [
        {'type': 'scholarship_delay', 'severity': 0.9, 'description': 'Scholarship not disbursed for 60 days', 'days_offset': 10},
        {'type': 'account_hold', 'severity': 0.85, 'description': 'Account hold preventing registration', 'days_offset': 20},
        {'type': 'mess_card', 'severity': 0.9, 'description': 'Mess card suspended - no food access', 'days_offset': 25},
        {'type': 'hostel_access', 'severity': 0.9, 'description': 'Hostel access revoked', 'days_offset': 30},
        {'type': 'fee_payment', 'severity': 0.8, 'description': 'Unable to pay semester fees', 'days_offset': 35},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=1, needs_intervention=True))
    
    # Student 2: Academic + Financial compound
    events = create_events(2, [
        {'type': 'scholarship_delay', 'severity': 0.7, 'description': 'Scholarship delayed 3 weeks', 'days_offset': 5},
        {'type': 'attendance_warning', 'severity': 0.6, 'description': 'Attendance warning despite medical docs', 'days_offset': 15},
        {'type': 'deadline_conflict', 'severity': 0.5, 'description': 'Conflicting administrative deadlines', 'days_offset': 20},
        {'type': 'registration_block', 'severity': 0.8, 'description': 'Registration blocked', 'days_offset': 40},
        {'type': 'account_hold', 'severity': 0.7, 'description': 'Account hold due to payment issue', 'days_offset': 45},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=2, needs_intervention=True))
    
    # Student 3: Language + Administrative barriers
    events = create_events(3, [
        {'type': 'language_barrier', 'severity': 0.7, 'description': 'Cannot understand financial aid forms', 'days_offset': 8},
        {'type': 'form_confusion', 'severity': 0.6, 'description': 'Submitted wrong scholarship form', 'days_offset': 12},
        {'type': 'scholarship_delay', 'severity': 0.8, 'description': 'Scholarship verification stuck', 'days_offset': 25},
        {'type': 'communication_issue', 'severity': 0.6, 'description': 'Miscommunication with admin office', 'days_offset': 35},
        {'type': 'fee_payment', 'severity': 0.75, 'description': 'Fee payment deadline missed', 'days_offset': 50},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=3, needs_intervention=True))
    
    # Student 4: Hostel + Basic needs crisis
    events = create_events(4, [
        {'type': 'room_assignment', 'severity': 0.7, 'description': 'Room reassignment delayed', 'days_offset': 5},
        {'type': 'hostel_access', 'severity': 0.85, 'description': 'Hostel access card deactivated', 'days_offset': 15},
        {'type': 'mess_card', 'severity': 0.8, 'description': 'Mess card suspended', 'days_offset': 18},
        {'type': 'amenity_restriction', 'severity': 0.6, 'description': 'Amenity access restricted', 'days_offset': 25},
        {'type': 'scholarship_delay', 'severity': 0.7, 'description': 'Scholarship delay causing payment issues', 'days_offset': 40},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=4, needs_intervention=True))
    
    # Student 5: Rapid event clustering
    events = create_events(5, [
        {'type': 'scholarship_delay', 'severity': 0.75, 'description': 'Scholarship delayed', 'days_offset': 60},
        {'type': 'fee_payment', 'severity': 0.7, 'description': 'Fee payment issue', 'days_offset': 62},
        {'type': 'account_hold', 'severity': 0.8, 'description': 'Account hold applied', 'days_offset': 64},
        {'type': 'attendance_warning', 'severity': 0.6, 'description': 'Attendance warning', 'days_offset': 66},
        {'type': 'registration_block', 'severity': 0.85, 'description': 'Registration blocked', 'days_offset': 68},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=5, needs_intervention=True))
    
    # Students 6-10: More high-risk cases
    for sid in range(6, 11):
        events = create_events(sid, [
            {'type': 'scholarship_delay', 'severity': 0.7 + (sid % 3) * 0.1, 'description': f'Scholarship issue {sid}', 'days_offset': 10 + sid},
            {'type': 'account_hold', 'severity': 0.75, 'description': f'Account hold {sid}', 'days_offset': 20 + sid},
            {'type': 'hostel_access', 'severity': 0.65 + (sid % 2) * 0.15, 'description': f'Hostel issue {sid}', 'days_offset': 30 + sid},
            {'type': 'fee_payment', 'severity': 0.7, 'description': f'Fee payment issue {sid}', 'days_offset': 40 + sid},
        ])
        for e in events:
            db.add(e)
        db.execute(labels_table.insert().values(student_id=sid, needs_intervention=True))
    
    # LOW RISK STUDENTS (needs_intervention = 0)
    
    # Student 11: Single minor issue
    events = create_events(11, [
        {'type': 'fee_payment', 'severity': 0.2, 'description': 'Minor fee payment delay', 'days_offset': 30},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=11, needs_intervention=False))
    
    # Student 12: Low severity events
    events = create_events(12, [
        {'type': 'form_confusion', 'severity': 0.25, 'description': 'Minor form question', 'days_offset': 20},
        {'type': 'communication_issue', 'severity': 0.2, 'description': 'Clarification needed', 'days_offset': 40},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=12, needs_intervention=False))
    
    # Student 13: Old resolved issues
    events = create_events(13, [
        {'type': 'scholarship_delay', 'severity': 0.4, 'description': 'Old scholarship delay (resolved)', 'days_offset': 5},
        {'type': 'fee_payment', 'severity': 0.3, 'description': 'Old fee issue (resolved)', 'days_offset': 10},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=13, needs_intervention=False))
    
    # Students 14-20: More low-risk cases
    for sid in range(14, 21):
        events = create_events(sid, [
            {'type': 'form_confusion', 'severity': 0.15 + (sid % 3) * 0.05, 'description': f'Minor issue {sid}', 'days_offset': 15 + sid * 2},
        ])
        for e in events:
            db.add(e)
        db.execute(labels_table.insert().values(student_id=sid, needs_intervention=False))
    
    # MODERATE RISK (Edge cases for testing)
    
    # Student 21: Moderate financial issue
    events = create_events(21, [
        {'type': 'scholarship_delay', 'severity': 0.55, 'description': 'Moderate scholarship delay', 'days_offset': 20},
        {'type': 'fee_payment', 'severity': 0.5, 'description': 'Fee payment concern', 'days_offset': 35},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=21, needs_intervention=True))
    
    # Student 22: Moderate academic friction
    events = create_events(22, [
        {'type': 'attendance_warning', 'severity': 0.5, 'description': 'Attendance warning', 'days_offset': 25},
        {'type': 'deadline_conflict', 'severity': 0.45, 'description': 'Deadline conflict', 'days_offset': 40},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=22, needs_intervention=False))
    
    # Student 23: Multiple low-severity events
    events = create_events(23, [
        {'type': 'form_confusion', 'severity': 0.3, 'description': 'Form confusion', 'days_offset': 10},
        {'type': 'communication_issue', 'severity': 0.35, 'description': 'Communication issue', 'days_offset': 20},
        {'type': 'language_barrier', 'severity': 0.4, 'description': 'Language barrier', 'days_offset': 30},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=23, needs_intervention=False))
    
    # Student 24: Recent high severity but single event
    events = create_events(24, [
        {'type': 'account_hold', 'severity': 0.7, 'description': 'Recent account hold', 'days_offset': 85},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=24, needs_intervention=True))
    
    # Student 25: Old high severity events
    events = create_events(25, [
        {'type': 'scholarship_delay', 'severity': 0.8, 'description': 'Old scholarship delay (resolved)', 'days_offset': 5},
        {'type': 'account_hold', 'severity': 0.75, 'description': 'Old account hold (resolved)', 'days_offset': 10},
    ])
    for e in events:
        db.add(e)
    db.execute(labels_table.insert().values(student_id=25, needs_intervention=False))
    
    db.commit()
    
    print(f"✓ Seeded 25 students with labeled data")
    print(f"  - 14 high-risk students (needs intervention)")
    print(f"  - 11 low-risk students (no intervention needed)")
    
    # Print summary
    total_events = db.query(StudentEvent).count()
    print(f"✓ Created {total_events} events")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_student_data(db)
        print("\n✓ Database seeded successfully!")
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
