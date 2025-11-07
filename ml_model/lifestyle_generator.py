import random
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
print("LOADED LIFESTYLE GENERATOR:", __file__)



class LifestyleGenerator:
    def generate_plan(self, risk_level, patient_data, management_type):
        """Generate personalized daily lifestyle plan"""
        
        plan = {
            'meal_plan': self._generate_meal_plan(risk_level, patient_data),
            'exercise_plan': self._generate_exercise_plan(risk_level, patient_data),
            'daily_reminders': self._generate_reminders(risk_level),
            'educational_content': self._get_educational_content(risk_level),
            'checkup_schedule': self._schedule_checkups(risk_level, management_type)
        }
        
        return plan
    
    def _generate_meal_plan(self, risk_level, data):
        """Heart-healthy Mediterranean diet focus"""
        
        base_meals = {
            'breakfast': [
                {
                    'name': 'Oatmeal with berries and walnuts',
                    'benefits': 'Soluble fiber lowers LDL cholesterol',
                    'nutrients': 'Omega-3, antioxidants, fiber'
                },
                {
                    'name': 'Greek yogurt with flaxseed',
                    'benefits': 'Probiotics and healthy fats',
                    'nutrients': 'Protein, omega-3, calcium'
                },
                {
                    'name': 'Vegetable omelet with olive oil',
                    'benefits': 'Monounsaturated fats support HDL',
                    'nutrients': 'Protein, vitamins, healthy fats'
                }
            ],
            'lunch': [
                {
                    'name': 'Grilled salmon with quinoa and vegetables',
                    'benefits': 'Omega-3 fatty acids reduce inflammation',
                    'nutrients': 'EPA/DHA, complete protein, fiber'
                },
                {
                    'name': 'Lentil soup with whole grain bread',
                    'benefits': 'Plant protein and cholesterol-lowering fiber',
                    'nutrients': 'Protein, iron, B-vitamins'
                },
                {
                    'name': 'Chicken breast with brown rice and broccoli',
                    'benefits': 'Lean protein with anti-inflammatory vegetables',
                    'nutrients': 'Protein, fiber, vitamins C & K'
                }
            ],
            'dinner': [
                {
                    'name': 'Mediterranean grilled fish with roasted vegetables',
                    'benefits': 'Heart-protective omega-3s',
                    'nutrients': 'Lean protein, antioxidants'
                },
                {
                    'name': 'Turkey chili with beans',
                    'benefits': 'High fiber reduces cholesterol absorption',
                    'nutrients': 'Protein, fiber, minerals'
                },
                {
                    'name': 'Vegetable stir-fry with tofu',
                    'benefits': 'Plant sterols lower LDL',
                    'nutrients': 'Plant protein, phytonutrients'
                }
            ],
            'snacks': [
                'Handful of almonds (reduces LDL by 5%)',
                'Apple with natural peanut butter',
                'Carrot sticks with hummus',
                'Low-fat cheese with whole grain crackers'
            ]
        }
        
        restrictions = []
        if risk_level in ['urgent', 'high']:
            restrictions = [
                '❌ AVOID: Saturated fats (butter, red meat, full-fat dairy)',
                '❌ ELIMINATE: Trans fats (processed foods, fried foods)',
                '❌ LIMIT: Dietary cholesterol (<200mg/day)',
                '❌ REDUCE: Sodium (<1500mg/day)',
                '❌ MINIMIZE: Added sugars'
            ]
        
        return {
            'daily_meals': base_meals,
            'restrictions': restrictions,
            'hydration': '8-10 glasses of water daily',
            'supplements': self._recommend_supplements(risk_level),
            'atherosclerosis_focus': 'Anti-inflammatory, cholesterol-lowering foods'
        }
    
    def _generate_exercise_plan(self, risk_level, data):
        """Exercise prescription based on risk"""
        
        if risk_level == 'urgent':
            plan = {
                'type': 'Light activity only - MEDICAL CLEARANCE REQUIRED',
                'duration': '10-15 minutes',
                'frequency': 'Daily gentle walking',
                'warning': '⚠️ Get physician approval before starting exercise',
                'activities': [
                    'Slow walking (level surface)',
                    'Gentle stretching',
                    'Light household activities'
                ]
            }
        elif risk_level == 'high':
            plan = {
                'type': 'Moderate aerobic exercise',
                'duration': '30 minutes',
                'frequency': '5 days/week',
                'intensity': 'Moderate (can talk but not sing)',
                'activities': [
                    'Brisk walking',
                    'Swimming',
                    'Cycling',
                    'Strength training (2x/week)'
                ],
                'benefits': 'Raises HDL, lowers triglycerides, improves insulin sensitivity'
            }
        else:
            plan = {
                'type': 'Regular aerobic + strength training',
                'duration': '40-60 minutes',
                'frequency': '5-7 days/week',
                'intensity': 'Moderate to vigorous',
                'activities': [
                    'Running/Jogging',
                    'HIIT workouts',
                    'Weight training',
                    'Sports activities'
                ],
                'benefits': 'Comprehensive cardiovascular protection'
            }
        
        plan['heart_health_note'] = 'Exercise reverses plaque buildup and improves arterial function'
        return plan
    
    def _generate_reminders(self, risk_level):
        """Daily reminder schedule"""
        
        base_reminders = [
            {'time': '07:00', 'message': '💊 Take morning medications (if prescribed)', 'priority': 'high'},
            {'time': '08:00', 'message': '🥗 Heart-healthy breakfast time', 'priority': 'medium'},
            {'time': '10:00', 'message': '💧 Hydration check - drink water', 'priority': 'low'},
            {'time': '12:30', 'message': '🍽️ Healthy lunch reminder', 'priority': 'medium'},
            {'time': '16:00', 'message': '🚶 Movement break - 10 minute walk', 'priority': 'medium'},
            {'time': '18:30', 'message': '🥙 Dinner time - Mediterranean style', 'priority': 'medium'},
            {'time': '21:00', 'message': '😴 Wind down - prepare for quality sleep', 'priority': 'low'},
        ]
        
        if risk_level in ['urgent', 'high']:
            base_reminders.extend([
                {'time': '09:00', 'message': '📊 Log your symptoms and how you feel', 'priority': 'high'},
                {'time': '20:00', 'message': '💊 Evening medication reminder', 'priority': 'high'},
                {'time': '22:00', 'message': '📝 Review today\'s adherence', 'priority': 'medium'}
            ])
        
        return sorted(base_reminders, key=lambda x: x['time'])
    
    def _get_educational_content(self, risk_level):
        """Daily educational messages about atherosclerosis"""
        
        content = {
            'daily_facts': [
                'Day 1: Atherosclerosis begins when LDL cholesterol penetrates artery walls, triggering inflammation.',
                'Day 2: HDL cholesterol acts like a vacuum cleaner, removing cholesterol from arteries.',
                'Day 3: Plaque buildup can reduce blood flow by 75% before symptoms appear.',
                'Day 4: Every 10% reduction in LDL lowers heart attack risk by 20%.',
                'Day 5: Exercise increases HDL and improves endothelial function within weeks.',
                'Day 6: Omega-3 fatty acids reduce inflammation that drives plaque formation.',
                'Day 7: Soluble fiber binds cholesterol in digestive tract, preventing absorption.'
            ],
            'warning_signs': [
                '⚠️ Chest discomfort or pressure',
                '⚠️ Shortness of breath with exertion',
                '⚠️ Jaw, neck, or arm pain',
                '⚠️ Severe fatigue',
                '⚠️ Dizziness or lightheadedness'
            ],
            'emergency_note': 'Call emergency services immediately if experiencing chest pain or breathing difficulty.'
        }
        
        return content
    
    def _schedule_checkups(self, risk_level, management_type):
        """Schedule follow-up appointments"""
        
        today = datetime.now()
        
        if risk_level == 'urgent':
            schedule = {
                'immediate': 'Physician visit within 24-48 hours',
                'follow_ups': [
                    {'date': (today + relativedelta(weeks=2)).strftime('%Y-%m-%d'), 'type': 'Medication review'},
                    {'date': (today + relativedelta(weeks=6)).strftime('%Y-%m-%d'), 'type': 'Lipid re-test'},
                    {'date': (today + relativedelta(weeks=12)).strftime('%Y-%m-%d'), 'type': 'Comprehensive assessment'}
                ]
            }
        elif risk_level == 'high':
            schedule = {
                'initial': 'Schedule appointment within 1-2 weeks',
                'follow_ups': [
                    {'date': (today + relativedelta(weeks=8)).strftime('%Y-%m-%d'), 'type': 'Lifestyle progress check'},
                    {'date': (today + relativedelta(weeks=12)).strftime('%Y-%m-%d'), 'type': 'Repeat lipid panel'},
                    {'date': (today + relativedelta(months=6)).strftime('%Y-%m-%d'), 'type': 'Full cardiovascular assessment'}
                ]
            }
        elif risk_level == 'medium':
            schedule = {
                'initial': 'Physician review within 1 month',
                'follow_ups': [
                    {'date': (today + relativedelta(months=3)).strftime('%Y-%m-%d'), 'type': 'Lipid re-check'},
                    {'date': (today + relativedelta(months=6)).strftime('%Y-%m-%d'), 'type': 'Progress evaluation'}
                ]
            }
        else:
            schedule = {
                'routine': 'Annual checkup',
                'follow_ups': [
                    {'date': (today + relativedelta(months=12)).strftime('%Y-%m-%d'), 'type': 'Routine lipid screening'}
                ]
            }
        
        return schedule
    
    def _recommend_supplements(self, risk_level):
        """Evidence-based supplement recommendations"""
        
        if risk_level in ['urgent', 'high']:
            return [
                '🐟 Omega-3 (EPA/DHA): 1-2g daily - reduces triglycerides',
                '🌿 Plant sterols: 2g daily - blocks cholesterol absorption',
                '☀️ Vitamin D: If deficient - supports cardiovascular health',
                '⚠️ Consult physician before starting supplements'
            ]
        else:
            return [
                '🐟 Omega-3: Consider if not eating fatty fish 2x/week',
                '☀️ Vitamin D: If deficiency confirmed',
                '💊 Multivitamin: Optional for nutritional insurance'
            ]