import math
'''. It handles the "Probability of Success" and updates the student's level after every answer.'''

'''Rasch Model Integrity: By using $P = 1 / (1 + e^{-(\theta - b)})$, you are accurately modeling the probability of success based on the logit difference between student ability ($\theta$) and item difficulty ($b$).Dynamic Measurement: The Standard Error (SE) decreases as the student answers more questions. This happens because each response adds Item Information ($P \times (1-P)$) to your database.95% Confidence: The test only stops when the computer is statistically certain (95% confidence) that the student’s true ability is either above or below the Passing Standard ($0.0$ logits).'''


import math

class NCLEXAdaptiveEngine:
    PASSING_STANDARD = 0.0  # The RN Passing line
    INITIAL_SE = 1.0        # Start with high uncertainty

    @staticmethod
    def calculate_probability(theta, difficulty):
        # Rasch Model: P(x=1) = e^(theta-b) / (1 + e^(theta-b))
        try:
            return 1 / (1 + math.exp(-(theta - difficulty)))
        except OverflowError:
            return 0.99 if theta > difficulty else 0.01

    @classmethod
    def update_student_ability(cls, session, is_correct, question_difficulty):
        """
        Updates Theta (Ability) and Standard Error using the Rasch Model.
        """
        p = cls.calculate_probability(session.current_theta, question_difficulty)
        
        # 1. Update Theta (Ability Estimate)
        # weight (Step-size) usually ranges from 0.1 to 0.5. 
        # 0.1 provides smooth transitions suitable for high-stakes exams.
        weight = 0.1 
        session.current_theta += weight * (is_correct - p)
        
        # 2. Update Standard Error (SE)
        # SE is the square root of the inverse of summed information.
        # Information for a dichotomous item = P * (1 - P).
        session.total_information += (p * (1 - p))
        session.standard_error = 1 / math.sqrt(session.total_information)
        
        session.save()
        return session.current_theta

    @classmethod
    def check_stopping_rule(cls, session):
        """
        Implements the 95% Confidence, Maximum Length, and Minimum Length rules.
        """
        questions_answered = session.userresponses_set.count()
        
        # RULE 1: Minimum Length (NCLEX-RN is 85 items)
        if questions_answered < 85:
            return "CONTINUE"

        # RULE 2: 95% Confidence Rule
        # Calculate the 95% Confidence Interval boundaries
        # Z-score for 95% confidence is 1.96.
        lower_95_limit = session.current_theta - (1.96 * session.standard_error)
        upper_95_limit = session.current_theta + (1.96 * session.standard_error)

        if lower_95_limit > cls.PASSING_STANDARD:
            return "PASS" # Entire interval is above passing line
        
        if upper_95_limit < cls.PASSING_STANDARD:
            return "FAIL" # Entire interval is below passing line

        # RULE 3: Maximum Length (NCLEX-RN is 150 items)
        if questions_answered >= 150:
            return "PASS" if session.current_theta >= cls.PASSING_STANDARD else "FAIL"

        return "CONTINUE"