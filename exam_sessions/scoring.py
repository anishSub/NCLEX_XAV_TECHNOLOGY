class NCLEXScoringService:
    @staticmethod
    def calculate_raw_score(question_type, user_data, correct_data):
        """
        Industry-standard scoring: Merges +/- and All-or-Nothing rules.
        """
        # GROUP 1: +/- Scoring (SATA, Matrix Multiple, Highlight Text)
        if question_type in ['SATA', 'MATRIX_MULTIPLE', 'HIGHLIGHT_TEXT']:
            score = 0
            # user_data is a list of selected IDs or row|col pairs
            for item in user_data:
                if item in correct_data:
                    score += 1 # Correct
                else:
                    score -= 1 # Incorrect (Penalize guessing)
            return max(0, score)

        # GROUP 2: All-or-Nothing Rationale (Dropdowns, Drag-Drop Dyads/Triads)
        elif question_type in ['DROPDOWN_RATIONALE', 'DRAG_DROP_RATIONALE']:
            # correct_data example: {"well1": "A", "well2": "B"}
            for key, val in correct_data.items():
                if user_data.get(key) != val:
                    return 0 # Failed clinical reasoning
            return 1 # Entire rationale is correct

        # GROUP 3: Coordinate Check (Hot Spot)
        elif question_type == 'HOT_SPOT':
            # correct_data: {"x_min": 40, "x_max": 50, "y_min": 30, "y_max": 40}
            ux, uy = user_data.get('x'), user_data.get('y')
            if (correct_data['x_min'] <= ux <= correct_data['x_max'] and 
                correct_data['y_min'] <= uy <= correct_data['y_max']):
                return 1
            return 0

        # GROUP 4: Simple MCQ
        elif question_type == 'MCQ':
            return 1 if user_data == correct_data else 0

        return 0