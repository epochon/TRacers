"""
Accuracy Testing Script for TRACE-AI
Evaluates multi-agent system performance against labeled data
"""

import sys
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sqlalchemy import text
from database import SessionLocal
from models import StudentEvent
from agents.financial_agent_ml import FinancialAgentML
from agents.features import extract_features


def load_labels(db):
    """Load ground truth labels from database."""
    result = db.execute(text("SELECT student_id, needs_intervention FROM labels"))
    labels = {row[0]: bool(row[1]) for row in result}
    return labels


def load_student_events(db, student_id):
    """Load all events for a student."""
    events = db.query(StudentEvent).filter(
        StudentEvent.student_id == student_id
    ).all()
    return events


def train_agents(db, labels):
    """
    Train all ML agents on labeled data.
    
    Args:
        db: Database session
        labels: Dictionary of student_id -> needs_intervention
    """
    print("\n" + "="*60)
    print("TRAINING AGENTS")
    print("="*60)
    
    # Initialize agents
    financial_agent = FinancialAgentML()
    
    # Collect training data
    X_train = []
    y_train = []
    
    for student_id, label in labels.items():
        events = load_student_events(db, student_id)
        if events:
            features = extract_features(events)
            X_train.append(features)
            y_train.append(1 if label else 0)
    
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    
    print(f"\nTraining data: {len(X_train)} students")
    print(f"  - Positive (needs intervention): {sum(y_train)}")
    print(f"  - Negative (no intervention): {len(y_train) - sum(y_train)}")
    
    # Train financial agent
    financial_agent.train(X_train, y_train)
    financial_agent.save_model()
    
    return financial_agent


def evaluate_system(db, labels, agents):
    """
    Evaluate the multi-agent system.
    
    Args:
        db: Database session
        labels: Ground truth labels
        agents: Dictionary of trained agents
        
    Returns:
        Dictionary of metrics
    """
    print("\n" + "="*60)
    print("EVALUATING SYSTEM")
    print("="*60)
    
    predictions = []
    ground_truth = []
    
    financial_agent = agents['financial']
    
    for student_id, true_label in labels.items():
        # Load student events
        events = load_student_events(db, student_id)
        
        if not events:
            continue
        
        # Get agent prediction
        result = financial_agent.evaluate(events)
        risk_score = result['risk']
        
        # Simple threshold-based decision
        predicted_label = risk_score >= 0.5
        
        predictions.append(predicted_label)
        ground_truth.append(true_label)
        
        # Print individual prediction
        status = "✓" if predicted_label == true_label else "✗"
        print(f"{status} Student {student_id}: Risk={risk_score:.3f}, "
              f"Predicted={predicted_label}, Actual={true_label}")
    
    # Calculate metrics
    accuracy = accuracy_score(ground_truth, predictions)
    precision = precision_score(ground_truth, predictions, zero_division=0)
    recall = recall_score(ground_truth, predictions, zero_division=0)
    f1 = f1_score(ground_truth, predictions, zero_division=0)
    cm = confusion_matrix(ground_truth, predictions)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm,
        'predictions': predictions,
        'ground_truth': ground_truth
    }


def print_results(metrics):
    """Print evaluation results."""
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    print(f"\nAccuracy:  {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall:    {metrics['recall']:.2%}")
    print(f"F1 Score:  {metrics['f1']:.2%}")
    
    print("\nConfusion Matrix:")
    cm = metrics['confusion_matrix']
    print(f"                Predicted")
    print(f"              No    Yes")
    print(f"Actual  No  [{cm[0][0]:4d}  {cm[0][1]:4d}]")
    print(f"        Yes [{cm[1][0]:4d}  {cm[1][1]:4d}]")
    
    # Check if target accuracy achieved
    target_accuracy = 0.88
    if metrics['accuracy'] >= target_accuracy:
        print(f"\n✓ TARGET ACHIEVED: Accuracy {metrics['accuracy']:.2%} >= {target_accuracy:.0%}")
    else:
        print(f"\n✗ Below target: Accuracy {metrics['accuracy']:.2%} < {target_accuracy:.0%}")
        print(f"  Gap: {(target_accuracy - metrics['accuracy']):.2%}")


def main():
    """Main evaluation function."""
    print("\n" + "="*60)
    print("TRACE-AI ACCURACY EVALUATION")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Load labels
        print("\nLoading labeled data...")
        labels = load_labels(db)
        print(f"✓ Loaded {len(labels)} labeled students")
        
        # Train agents
        financial_agent = train_agents(db, labels)
        
        agents = {
            'financial': financial_agent
        }
        
        # Evaluate
        metrics = evaluate_system(db, labels, agents)
        
        # Print results
        print_results(metrics)
        
        print("\n" + "="*60)
        print("EVALUATION COMPLETE")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
