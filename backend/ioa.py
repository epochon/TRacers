"""
TRACES Pro - Intervention Orchestrator Agent (IOA)
Autonomous agent that orchestrates interventions
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import secrets

from app.models.database import Student, Event, Analysis
from app.models.agent import (
    AgentSession, InterventionPlan, AgentAction, InterventionOutcome,
    AgentObservation, GovConnectSignal, AgentStatus, InterventionType,
    InterventionStatus, ActionStatus
)

class InterventionOrchestratorAgent:
    """
    The brain of TRACES - autonomous intervention orchestrator
    
    Capabilities:
    - Continuous observation
    - Hypothesis generation
    - Intervention planning
    - Tool orchestration
    - Human-in-the-loop
    - Outcome verification
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.observation_window_days = 14
        self.risk_threshold = 0.6
        self.intervention_cooldown_days = 7
    
    # ========================================================================
    # STEP 1: CONTINUOUS OBSERVATION
    # ========================================================================
    
    def observe_student(self, student_id: int) -> Dict[str, Any]:
        """Continuously monitor student patterns"""
        
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None
        
        # Get recent events
        cutoff_date = datetime.utcnow() - timedelta(days=self.observation_window_days)
        events = self.db.query(Event).filter(
            Event.student_id == student_id,
            Event.event_date >= cutoff_date
        ).all()
        
        # Get recent analyses
        analyses = self.db.query(Analysis).filter(
            Analysis.student_id == student_id,
            Analysis.created_at >= cutoff_date
        ).order_by(Analysis.created_at.desc()).all()
        
        # Calculate risk trend
        risk_scores = [a.confidence for a in analyses]
        risk_trend = self._calculate_trend(risk_scores)
        risk_velocity = self._calculate_velocity(risk_scores)
        
        # Detect patterns
        observations = {
            'student_id': student_id,
            'risk_scores': risk_scores,
            'current_risk': risk_scores[0] if risk_scores else 0.0,
            'risk_trend': risk_trend,
            'risk_velocity': risk_velocity,
            'event_count': len(events),
            'high_severity_events': len([e for e in events if e.severity > 0.6]),
            'patterns': self._detect_patterns(events, analyses),
            'anomalies': self._detect_anomalies(events),
            'context': self._gather_context(student, events)
        }
        
        # Store observation
        for pattern_type, pattern_data in observations['patterns'].items():
            obs = AgentObservation(
                student_id=student_id,
                observation_type=pattern_type,
                metric_name='risk_trend',
                metric_value=observations['current_risk'],
                metric_text=json.dumps(pattern_data),
                anomaly_detected=len(observations['anomalies']) > 0,
                severity=observations['current_risk'],
                pattern_type=risk_trend,
                observed_at=datetime.utcnow()
            )
            self.db.add(obs)
        
        self.db.commit()
        
        return observations
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate if risk is increasing, stable, or decreasing"""
        if len(scores) < 2:
            return "stable"
        
        recent_avg = sum(scores[:3]) / min(3, len(scores))
        older_avg = sum(scores[3:6]) / max(1, min(3, len(scores) - 3))
        
        if recent_avg > older_avg + 0.1:
            return "increasing"
        elif recent_avg < older_avg - 0.1:
            return "decreasing"
        return "stable"
    
    def _calculate_velocity(self, scores: List[float]) -> float:
        """Calculate rate of change in risk"""
        if len(scores) < 2:
            return 0.0
        
        return scores[0] - scores[-1]
    
    def _detect_patterns(self, events: List[Event], analyses: List[Analysis]) -> Dict:
        """Detect patterns in student behavior"""
        patterns = {}
        
        # Financial stress pattern
        financial_events = [e for e in events if 'financial' in e.event_type.value.lower()]
        if len(financial_events) >= 2:
            patterns['financial_stress'] = {
                'count': len(financial_events),
                'severity': sum(e.severity for e in financial_events) / len(financial_events),
                'timespan_days': (max(e.event_date for e in financial_events) - 
                                 min(e.event_date for e in financial_events)).days
            }
        
        # Academic overload pattern
        academic_events = [e for e in events if 'attendance' in e.event_type.value.lower() 
                          or 'course' in e.event_type.value.lower()]
        if len(academic_events) >= 2:
            patterns['academic_pressure'] = {
                'count': len(academic_events),
                'severity': sum(e.severity for e in academic_events) / len(academic_events)
            }
        
        # Social isolation pattern (from chat data - to be implemented)
        patterns['social_isolation'] = {
            'no_peer_chats': True,  # TODO: Check chat history
            'no_recent_logins': False  # TODO: Check login history
        }
        
        return patterns
    
    def _detect_anomalies(self, events: List[Event]) -> List[Dict]:
        """Detect anomalous events"""
        anomalies = []
        
        # Sudden spike in high-severity events
        recent_high = [e for e in events[:5] if e.severity > 0.7]
        if len(recent_high) >= 2:
            anomalies.append({
                'type': 'severity_spike',
                'description': f'{len(recent_high)} high-severity events in short period',
                'severity': 0.8
            })
        
        return anomalies
    
    def _gather_context(self, student: Student, events: List[Event]) -> Dict:
        """Gather relevant context"""
        return {
            'is_first_generation': student.is_first_generation,
            'year': student.year,
            'department': student.department,
            'cgpa': student.cgpa,
            'scholarship_type': student.scholarship_type,
            'recent_event_types': [e.event_type.value for e in events[:5]]
        }
    
    # ========================================================================
    # STEP 2: HYPOTHESIS GENERATION
    # ========================================================================
    
    def generate_hypotheses(self, observations: Dict) -> List[Dict]:
        """Generate hypotheses about root causes using LLM reasoning"""
        
        hypotheses = []
        
        # Financial stress hypothesis
        if 'financial_stress' in observations['patterns']:
            hypotheses.append({
                'cause': 'Financial Stress',
                'confidence': 0.8,
                'evidence': [
                    f"{observations['patterns']['financial_stress']['count']} financial events",
                    f"Average severity: {observations['patterns']['financial_stress']['severity']:.2f}"
                ],
                'indicators': ['scholarship_delay', 'fee_failure'],
                'intervention_types': [
                    InterventionType.FINANCIAL_AID,
                    InterventionType.SCHOLARSHIP_MATCH,
                    InterventionType.FEE_EXTENSION
                ]
            })
        
        # Academic overload hypothesis
        if 'academic_pressure' in observations['patterns']:
            hypotheses.append({
                'cause': 'Academic Overload',
                'confidence': 0.7,
                'evidence': [
                    f"{observations['patterns']['academic_pressure']['count']} academic events",
                    f"Risk trend: {observations['risk_trend']}"
                ],
                'indicators': ['attendance_warning', 'course_drop'],
                'intervention_types': [
                    InterventionType.ACADEMIC_SUPPORT,
                    InterventionType.PEER_SUPPORT
                ]
            })
        
        # Social isolation hypothesis
        if observations['patterns'].get('social_isolation', {}).get('no_peer_chats'):
            hypotheses.append({
                'cause': 'Social Isolation',
                'confidence': 0.6,
                'evidence': [
                    'No peer interaction detected',
                    'Low engagement patterns'
                ],
                'indicators': ['isolation'],
                'intervention_types': [
                    InterventionType.PEER_SUPPORT,
                    InterventionType.COUNSELOR_CHAT
                ]
            })
        
        return hypotheses
    
    # ========================================================================
    # STEP 3: INTERVENTION PLANNING
    # ========================================================================
    
    def create_intervention_plan(
        self, 
        student_id: int, 
        observations: Dict, 
        hypotheses: List[Dict]
    ) -> InterventionPlan:
        """Create multi-step intervention plan"""
        
        # Create agent session
        session = AgentSession(
            student_id=student_id,
            session_id=f"session_{secrets.token_hex(8)}",
            status=AgentStatus.PLANNING,
            current_risk_score=observations['current_risk'],
            risk_trend=observations['risk_trend'],
            risk_velocity=observations['risk_velocity'],
            goal=f"Reduce dropout probability below {self.risk_threshold*100}% in 7 days",
            target_risk_score=self.risk_threshold * 0.7,
            target_deadline=datetime.utcnow() + timedelta(days=7),
            observations=observations,
            hypotheses=hypotheses,
            started_at=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Generate plan based on top hypotheses
        top_hypothesis = max(hypotheses, key=lambda h: h['confidence'])
        
        # Create intervention plan
        plan = InterventionPlan(
            session_id=session.id,
            student_id=student_id,
            plan_id=f"plan_{secrets.token_hex(8)}",
            title=f"Address {top_hypothesis['cause']}",
            description=f"Multi-step intervention to reduce {top_hypothesis['cause'].lower()}",
            reasoning={
                'primary_cause': top_hypothesis['cause'],
                'confidence': top_hypothesis['confidence'],
                'evidence': top_hypothesis['evidence'],
                'all_hypotheses': hypotheses
            },
            identified_causes=[h['cause'] for h in hypotheses],
            expected_outcome=f"Risk reduction from {observations['current_risk']:.2f} to {self.risk_threshold*0.7:.2f}",
            requires_approval=True,
            priority=self._calculate_priority(observations, hypotheses),
            estimated_duration_days=7,
            success_metrics={
                'risk_reduction_target': 0.3,
                'student_engagement': True,
                'response_within_days': 3
            },
            created_at=datetime.utcnow()
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        # Create action sequence
        self._create_action_sequence(plan, top_hypothesis, observations)
        
        return plan
    
    def _calculate_priority(self, observations: Dict, hypotheses: List[Dict]) -> int:
        """Calculate intervention priority (1-5, 5 is highest)"""
        risk = observations['current_risk']
        trend = observations['risk_trend']
        
        if risk > 0.8:
            return 5
        elif risk > 0.6 and trend == 'increasing':
            return 4
        elif risk > 0.6:
            return 3
        elif risk > 0.4 and trend == 'increasing':
            return 3
        else:
            return 2
    
    def _create_action_sequence(
        self, 
        plan: InterventionPlan, 
        hypothesis: Dict, 
        observations: Dict
    ):
        """Create sequence of actions for the plan"""
        
        actions = []
        sequence = 1
        
        # Action 1: Send supportive check-in (if counselor chat needed)
        if InterventionType.COUNSELOR_CHAT in hypothesis['intervention_types']:
            actions.append(AgentAction(
                plan_id=plan.id,
                action_id=f"action_{secrets.token_hex(6)}",
                action_type=InterventionType.COUNSELOR_CHAT,
                sequence_order=sequence,
                title="Anonymous Supportive Check-in",
                description="Send anonymous message via chat system",
                delegated_to="counselor_chat_agent",
                tool_parameters={
                    'message_template': 'supportive_checkin',
                    'is_anonymous': True
                },
                scheduled_at=datetime.utcnow()
            ))
            sequence += 1
        
        # Action 2: Financial aid if needed
        if InterventionType.FINANCIAL_AID in hypothesis['intervention_types']:
            actions.append(AgentAction(
                plan_id=plan.id,
                action_id=f"action_{secrets.token_hex(6)}",
                action_type=InterventionType.FEE_EXTENSION,
                sequence_order=sequence,
                title="Draft Fee Extension Email",
                description="Generate fee extension request email for student",
                delegated_to="document_agent",
                tool_parameters={
                    'document_type': 'fee_extension_request',
                    'student_context': observations['context']
                },
                scheduled_at=datetime.utcnow() + timedelta(hours=2)
            ))
            sequence += 1
            
            actions.append(AgentAction(
                plan_id=plan.id,
                action_id=f"action_{secrets.token_hex(6)}",
                action_type=InterventionType.SCHOLARSHIP_MATCH,
                sequence_order=sequence,
                title="Find Relevant Scholarships",
                description="Match student with 2-3 applicable scholarships",
                delegated_to="scholarship_agent",
                tool_parameters={
                    'max_results': 3,
                    'student_profile': observations['context']
                },
                scheduled_at=datetime.utcnow() + timedelta(hours=4)
            ))
            sequence += 1
        
        # Action 3: Peer support
        if InterventionType.PEER_SUPPORT in hypothesis['intervention_types']:
            actions.append(AgentAction(
                plan_id=plan.id,
                action_id=f"action_{secrets.token_hex(6)}",
                action_type=InterventionType.PEER_SUPPORT,
                sequence_order=sequence,
                title="Match with Senior Mentor",
                description="Connect student with senior from same branch",
                delegated_to="peer_match_agent",
                tool_parameters={
                    'match_criteria': {
                        'department': observations['context']['department'],
                        'year_difference': 1,
                        'similar_background': observations['context']['is_first_generation']
                    }
                },
                scheduled_at=datetime.utcnow() + timedelta(hours=6)
            ))
            sequence += 1
        
        # Action 4: Academic support
        if InterventionType.ACADEMIC_SUPPORT in hypothesis['intervention_types']:
            actions.append(AgentAction(
                plan_id=plan.id,
                action_id=f"action_{secrets.token_hex(6)}",
                action_type=InterventionType.ACADEMIC_SUPPORT,
                sequence_order=sequence,
                title="Provide Academic Resources",
                description="Share relevant study materials and support",
                delegated_to="academic_support_agent",
                tool_parameters={
                    'courses': observations['context'].get('struggling_courses', []),
                    'support_type': 'tutoring_and_resources'
                },
                scheduled_at=datetime.utcnow() + timedelta(hours=8)
            ))
            sequence += 1
        
        # Final action: Escalate if no response
        actions.append(AgentAction(
            plan_id=plan.id,
            action_id=f"action_{secrets.token_hex(6)}",
            action_type=InterventionType.EMERGENCY_ESCALATION,
            sequence_order=sequence,
            title="Escalate to Counselor (If No Response)",
            description="Flag for human counselor review if student doesn't respond",
            delegated_to="escalation_agent",
            tool_parameters={
                'response_deadline_hours': 48,
                'escalation_threshold': 'no_response'
            },
            depends_on_action_id=actions[0].id if actions else None,
            scheduled_at=datetime.utcnow() + timedelta(days=2)
        ))
        
        # Add all actions
        for action in actions:
            self.db.add(action)
        
        self.db.commit()
    
    # ========================================================================
    # STEP 4: TOOL EXECUTION
    # ========================================================================
    
    def execute_action(self, action: AgentAction) -> Dict[str, Any]:
        """Execute individual action by delegating to appropriate agent"""
        
        action.status = ActionStatus.EXECUTING
        action.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # Delegate to sub-agents
            if action.delegated_to == "document_agent":
                result = self._document_agent_execute(action)
            elif action.delegated_to == "scholarship_agent":
                result = self._scholarship_agent_execute(action)
            elif action.delegated_to == "peer_match_agent":
                result = self._peer_match_agent_execute(action)
            elif action.delegated_to == "counselor_chat_agent":
                result = self._counselor_chat_agent_execute(action)
            elif action.delegated_to == "academic_support_agent":
                result = self._academic_support_agent_execute(action)
            elif action.delegated_to == "escalation_agent":
                result = self._escalation_agent_execute(action)
            else:
                result = {'success': False, 'error': 'Unknown agent'}
            
            # Update action
            action.status = ActionStatus.COMPLETED if result.get('success') else ActionStatus.FAILED
            action.success = result.get('success', False)
            action.result_data = result
            action.completed_at = datetime.utcnow()
            action.execution_log = {'executed_at': datetime.utcnow().isoformat(), 'result': result}
            
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            action.retry_count += 1
            result = {'success': False, 'error': str(e)}
        
        self.db.commit()
        return result
    
    def _document_agent_execute(self, action: AgentAction) -> Dict:
        """Document generation agent"""
        # TODO: Implement actual document generation
        return {
            'success': True,
            'document_type': action.tool_parameters['document_type'],
            'document_url': f'/documents/generated_{action.id}.pdf',
            'message': 'Fee extension email drafted successfully'
        }
    
    def _scholarship_agent_execute(self, action: AgentAction) -> Dict:
        """Scholarship matching agent"""
        # TODO: Implement actual scholarship matching
        return {
            'success': True,
            'scholarships': [
                {'name': 'Merit Scholarship 2024', 'amount': 50000, 'deadline': '2024-03-30'},
                {'name': 'First Generation Support', 'amount': 30000, 'deadline': '2024-04-15'}
            ],
            'message': 'Found 2 relevant scholarships'
        }
    
    def _peer_match_agent_execute(self, action: AgentAction) -> Dict:
        """Peer matching agent"""
        # TODO: Implement actual peer matching
        return {
            'success': True,
            'mentor': {
                'name': 'Anonymous Senior',
                'department': action.tool_parameters['match_criteria']['department'],
                'year': 4
            },
            'message': 'Matched with senior mentor'
        }
    
    def _counselor_chat_agent_execute(self, action: AgentAction) -> Dict:
        """Counselor chat initiation agent"""
        # TODO: Integrate with chat system
        return {
            'success': True,
            'chat_room_id': f'room_{secrets.token_hex(8)}',
            'message': 'Anonymous chat initiated'
        }
    
    def _academic_support_agent_execute(self, action: AgentAction) -> Dict:
        """Academic support agent"""
        # TODO: Implement academic support
        return {
            'success': True,
            'resources': ['Study guide', 'Tutoring schedule', 'Office hours'],
            'message': 'Academic resources shared'
        }
    
    def _escalation_agent_execute(self, action: AgentAction) -> Dict:
        """Escalation agent"""
        # TODO: Implement escalation logic
        return {
            'success': True,
            'escalated_to': 'counselor',
            'message': 'Case escalated for human review'
        }
    
    # ========================================================================
    # STEP 5: HUMAN-IN-THE-LOOP
    # ========================================================================
    
    def request_approval(self, plan: InterventionPlan) -> Dict:
        """Request human approval for plan"""
        
        plan.approval_status = InterventionStatus.PENDING_APPROVAL
        self.db.commit()
        
        return {
            'plan_id': plan.plan_id,
            'requires_approval': True,
            'approval_request': {
                'student_id': plan.student_id,
                'risk_score': plan.session.current_risk_score,
                'primary_cause': plan.reasoning['primary_cause'],
                'proposed_actions': [
                    {'type': a.action_type.value, 'title': a.title}
                    for a in plan.actions
                ],
                'expected_outcome': plan.expected_outcome
            }
        }
    
    def approve_plan(self, plan_id: str, approver_id: int, notes: str = None) -> bool:
        """Approve intervention plan"""
        
        plan = self.db.query(InterventionPlan).filter(
            InterventionPlan.plan_id == plan_id
        ).first()
        
        if not plan:
            return False
        
        plan.approval_status = InterventionStatus.APPROVED
        plan.approved_by = approver_id
        plan.approved_at = datetime.utcnow()
        plan.approval_notes = notes
        plan.started_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    # ========================================================================
    # STEP 6: OUTCOME VERIFICATION
    # ========================================================================
    
    def verify_outcome(self, plan: InterventionPlan) -> InterventionOutcome:
        """Verify intervention effectiveness"""
        
        student_id = plan.student_id
        
        # Get new observations
        new_observations = self.observe_student(student_id)
        
        # Calculate metrics
        risk_before = plan.session.current_risk_score
        risk_after = new_observations['current_risk']
        risk_reduction = risk_before - risk_after
        
        # Check success criteria
        goals_achieved = {
            'risk_reduced': risk_reduction >= plan.success_metrics.get('risk_reduction_target', 0.3),
            'student_responded': self._check_student_response(student_id),
            'engagement_improved': new_observations['risk_trend'] == 'decreasing'
        }
        
        success_rate = sum(goals_achieved.values()) / len(goals_achieved)
        
        # Create outcome
        outcome = InterventionOutcome(
            plan_id=plan.id,
            student_id=student_id,
            risk_score_before=risk_before,
            risk_score_after=risk_after,
            risk_reduction=risk_reduction,
            student_responded=goals_achieved['student_responded'],
            engagement_improved=goals_achieved['engagement_improved'],
            goals_achieved=goals_achieved,
            success_rate=success_rate,
            effectiveness_score=self._calculate_effectiveness(plan, goals_achieved),
            requires_plan_b=success_rate < 0.5,
            escalation_needed=risk_after > 0.7,
            measured_at=datetime.utcnow()
        )
        
        self.db.add(outcome)
        
        # Update session
        plan.session.status = AgentStatus.COMPLETED
        plan.session.completed_at = datetime.utcnow()
        plan.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        # Generate Plan B if needed
        if outcome.requires_plan_b:
            self._generate_plan_b(student_id, new_observations, outcome)
        
        return outcome
    
    def _check_student_response(self, student_id: int) -> bool:
        """Check if student responded to interventions"""
        # TODO: Implement actual response checking
        return True
    
    def _calculate_effectiveness(self, plan: InterventionPlan, goals: Dict) -> float:
        """Calculate intervention effectiveness score"""
        return sum(goals.values()) / len(goals)
    
    def _generate_plan_b(self, student_id: int, observations: Dict, outcome: InterventionOutcome):
        """Generate alternative plan if initial plan failed"""
        # Generate new hypotheses excluding what didn't work
        hypotheses = self.generate_hypotheses(observations)
        
        # Create new plan with different approach
        # Mark as higher priority
        # This would recursively call create_intervention_plan
        pass
