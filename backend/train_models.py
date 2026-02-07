"""
Train All ML Agents
Trains all domain agents on labeled data and saves models
"""

import sys
from sqlalchemy import text
from database import SessionLocal
from models import StudentEvent
from agents.coordinator_ml import CoordinatorAgentML


def load_training_data(db):
    """Load all labeled students and their events."""
    # Get labels
    result = db.execute(text("SELECT student_id, needs_intervention FROM labels"))
    labels = {row[0]: bool(row[1]) for row in result}
    
    # Load events for each student
    training_data = []
    for student_id, label in labels.items():
        events = db.query(StudentEvent).filter(
            StudentEvent.student_id == student_id
        ).all()
        
        if events:
            training_data.append({
                'student_id': student_id,
                'events': events,
                'label': label
            })
    
    return training_data


def main():
    """Train all ML agents."""
    print("\n" + "="*60)
    print("TRAINING ALL ML AGENTS")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Load training data
        print("\nLoading training data...")
        training_data = load_training_data(db)
        print(f"✓ Loaded {len(training_data)} labeled students")
        
        # Count labels
        positive = sum(1 for d in training_data if d['label'])
        negative = len(training_data) - positive
        print(f"  - Positive (needs intervention): {positive}")
        print(f"  - Negative (no intervention): {negative}")
        
        # Initialize coordinator
        print("\nInitializing ML coordinator...")
        coordinator = CoordinatorAgentML()
        
        # Train all agents
        print("\nTraining agents...")
        coordinator.train_all_agents(training_data)
        
        print("\n" + "="*60)
        print("✓ TRAINING COMPLETE")
        print("="*60)
        print("\nAll ML models have been trained and saved to:")
        print("  - models/financial_agent.pkl")
        print("  - models/academic_agent.pkl")
        print("  - models/residential_agent.pkl")
        print("  - models/language_agent.pkl")
        print("\nThe models are now ready to use in the live application!")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
