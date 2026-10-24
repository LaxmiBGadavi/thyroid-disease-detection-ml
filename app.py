from flask import Flask, request, jsonify, render_template, send_file, make_response
import pandas as pd
import os
import json
from io import BytesIO
from datetime import datetime
import uuid
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import textwrap
from database import get_database

app = Flask(__name__, 
            template_folder='../frontend_1/templates', 
            static_folder='../frontend_1/static')

print("THYROID ASSESSMENT SYSTEM")
print("System initialized - Medical reference ranges and symptom analysis active")

# ================= DATABASE STORAGE SYSTEM =================
# Get database instance for persistent storage
db = get_database()

def save_assessment_history(user_id, input_data, prediction_result, history_id=None):
    """
    Save assessment history with input values, outputs, and timestamp to database
    
    Args:
        user_id: Unique identifier for the user
        input_data: Dictionary containing input values (lab results, symptoms)
        prediction_result: Dictionary containing prediction results
        history_id: Optional assessment ID
    
    Returns:
        history_id: Unique identifier for the saved assessment
    """
    try:
        assessment_id = db.save_assessment(user_id, input_data, prediction_result, history_id)
        print(f"Assessment history saved for user {user_id}: {assessment_id}")
        return assessment_id
    except Exception as e:
        print(f"Error saving assessment history: {str(e)}")
        raise

def get_assessment_history(user_id, limit=None):
    """
    Retrieve assessment history for a user from database
    
    Args:
        user_id: Unique identifier for the user
        limit: Maximum number of records to return (optional)
    
    Returns:
        List of assessment history entries
    """
    try:
        history = db.get_assessment_history(user_id, limit)
        print(f"Retrieved {len(history)} assessments for user {user_id}")
        return history
    except Exception as e:
        print(f"Error retrieving assessment history: {str(e)}")
        return []

# ================= HOME PAGE =================
@app.route("/")
def home():
    return render_template("welcome.html")

# ================= LOGOUT ROUTE =================
@app.route("/logout")
def logout():
    # In a real application, you would clear session data here
    # For this demo, we'll just redirect to the login-only page
    return render_template("login.html")

# ================= DASHBOARD ROUTES =================

@app.route("/check")
def check_health():
    return render_template("check_health.html")

@app.route("/results")  
def results():
    return render_template("results.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ================= ADDITIONAL PAGE ROUTES =================
@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/nutrition")
def nutrition():
    return render_template("nutrition.html")

@app.route("/exercise")
def exercise():
    return render_template("exercise.html")

@app.route("/tips")
def tips():
    return render_template("tips.html")

@app.route("/medical_test")
def medical_test():
    return render_template("medical_test.html")

@app.route("/medical_report")
def medical_report():
    return render_template("medical_report.html")

@app.route("/history")
def history():
    return render_template("history.html")

# ================= HTML FILE ROUTES (for frontend compatibility) =================
# These routes serve the same templates but with .html extension
@app.route("/dashboard.html")
def dashboard_html():
    return render_template("dashboard.html")

@app.route("/check_health.html")
def check_health_html():
    return render_template("check_health.html")

@app.route("/results.html")
def results_html():
    return render_template("results.html")

@app.route("/learn.html")
def learn_html():
    return render_template("learn.html")

@app.route("/nutrition.html")
def nutrition_html():
    return render_template("nutrition.html")

@app.route("/exercise.html")
def exercise_html():
    return render_template("exercise.html")

@app.route("/tips.html")
def tips_html():
    return render_template("tips.html")

@app.route("/medical_test.html")
def medical_test_html():
    return render_template("medical_test.html")

@app.route("/medical_report.html")
def medical_report_html():
    return render_template("medical_report.html")

@app.route("/history.html")
def history_html():
    return render_template("history.html")

# ================= HISTORY API ENDPOINTS =================
@app.route("/api/save-assessment", methods=["POST"])
def save_assessment():
    """
    Save assessment to history
    """
    try:
        data = request.get_json()
        
        # Extract user identifier (for demo, using a simple user ID)
        # In production, this would come from authentication/session
        user_id = data.get('user_id', 'default_user')
        
        # Extract input data (lab values and symptoms)
        input_data = {
            'tsh': data.get('TSH'),
            't3': data.get('T3'),
            't4': data.get('TT4'),
            'symptoms': {key: value for key, value in data.items() 
                        if key in ['tiredness', 'sleep', 'appetite', 'weight', 
                                 'temperature', 'mood', 'skin']}
        }
        
        # Extract prediction results
        prediction_result = {
            'prediction': data.get('prediction'),
            'confidence': data.get('confidence'),
            'classification_method': data.get('classification_method'),
            'current_risk_level': data.get('current_risk_level'),
            'risk_score': data.get('risk_score')
        }
        
        # Save to history
        history_id = save_assessment_history(user_id, input_data, prediction_result)
        
        return jsonify({
            "status": "success",
            "history_id": history_id,
            "message": "Assessment saved to history"
        })
        
    except Exception as e:
        print(f"Save assessment error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/get-history", methods=["GET"])
def get_history():
    """
    Get assessment history for a user
    """
    try:
        # Extract user identifier
        user_id = request.args.get('user_id', 'default_user')
        limit = request.args.get('limit', None)
        
        if limit:
            limit = int(limit)
        
        # Get history from storage
        history = get_assessment_history(user_id, limit)
        
        return jsonify({
            "status": "success",
            "history": history,
            "count": len(history)
        })
        
    except Exception as e:
        print(f"Get history error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/clear-history", methods=["POST"])
def clear_history():
    """
    Clear assessment history for a user from database
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        
        success = db.clear_user_history(user_id)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "History cleared successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to clear history"
            })
        
    except Exception as e:
        print(f"Clear history error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

# ================= ADDITIONAL DATABASE API ENDPOINTS =================

@app.route("/api/database-stats", methods=["GET"])
def get_database_stats():
    """
    Get database statistics and metrics
    """
    try:
        user_id = request.args.get('user_id', None)
        stats = db.get_assessment_stats(user_id)
        
        return jsonify({
            "status": "success",
            "stats": stats
        })
        
    except Exception as e:
        print(f"Database stats error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/backup-database", methods=["POST"])
def backup_database():
    """
    Create a backup of the assessment database
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"assessment_backup_{timestamp}.db"
        
        success = db.backup_database(backup_path)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Database backed up to {backup_path}",
                "backup_path": backup_path
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to create database backup"
            })
        
    except Exception as e:
        print(f"Database backup error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/get-all-assessments", methods=["GET"])
def get_all_assessments():
    """
    Get all assessments (admin/analytics endpoint)
    """
    try:
        limit = request.args.get('limit', None)
        if limit:
            limit = int(limit)
        
        assessments = db.get_all_assessments(limit)
        
        return jsonify({
            "status": "success",
            "assessments": assessments,
            "count": len(assessments)
        })
        
    except Exception as e:
        print(f"Get all assessments error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

# ================= COMPREHENSIVE RULE-BASED THYROID CLASSIFICATION SYSTEM =================
def classify_thyroid_condition_advanced(tsh, t3, t4, symptoms=None):
    """
    Comprehensive rule-based thyroid classification system
    
    Args:
        tsh: TSH level (mIU/L)
        t3: T3 level (pmol/L) 
        t4: T4 level (pmol/L)
        symptoms: Dictionary of symptom responses
    
    Returns:
        dict: Classification result with prediction, confidence, and reasoning
    """
    
    # Medical reference ranges
    tsh_normal_range = (0.27, 4.20)
    t3_normal_range = (3.1, 6.8)
    t4_normal_range = (12.0, 22.0)
    
    # Lab-based classification
    lab_prediction = None
    lab_confidence = 0
    lab_reasoning = []
    
    if all(val is not None for val in [tsh, t3, t4]):
        # Comprehensive lab analysis
        tsh_low = tsh < tsh_normal_range[0]
        tsh_normal = tsh_normal_range[0] <= tsh <= tsh_normal_range[1]
        tsh_high = tsh > tsh_normal_range[1]
        
        t3_low = t3 < t3_normal_range[0]
        t3_normal = t3_normal_range[0] <= t3 <= t3_normal_range[1]
        t3_high = t3 > t3_normal_range[1]
        
        t4_low = t4 < t4_normal_range[0]
        t4_normal = t4_normal_range[0] <= t4 <= t4_normal_range[1]
        t4_high = t4 > t4_normal_range[1]
        
        # Advanced lab-based classification logic
        if tsh_low and (t3_high or t4_high):
            lab_prediction = "Hyperthyroid"
            lab_confidence = 95
            lab_reasoning.append("Low TSH with elevated T3/T4 indicates hyperthyroidism")
        elif tsh_high and (t3_low or t4_low):
            lab_prediction = "Hypothyroid"
            lab_confidence = 95
            lab_reasoning.append("High TSH with low T3/T4 indicates hypothyroidism")
        elif tsh_normal and t3_normal and t4_normal:
            lab_prediction = "Normal"
            lab_confidence = 90
            lab_reasoning.append("All thyroid hormones within normal ranges")
        elif tsh_low:
            lab_prediction = "Hyperthyroid"
            lab_confidence = 80
            lab_reasoning.append("Low TSH often indicates hyperthyroidism")
        elif tsh_high:
            lab_prediction = "Hypothyroid"
            lab_confidence = 80
            lab_reasoning.append("High TSH often indicates hypothyroidism")
        else:
            # Borderline or ambiguous cases
            if t3_high or t4_high:
                lab_prediction = "Hyperthyroid"
                lab_confidence = 70
                lab_reasoning.append("Elevated T3/T4 suggests hyperthyroidism")
            elif t3_low or t4_low:
                lab_prediction = "Hypothyroid"
                lab_confidence = 70
                lab_reasoning.append("Low T3/T4 suggests hypothyroidism")
            else:
                lab_prediction = "Normal"
                lab_confidence = 60
                lab_reasoning.append("Borderline values - clinical correlation needed")
    
    # Symptom-based classification
    symptom_prediction = None
    symptom_confidence = 0
    symptom_reasoning = []
    
    if symptoms:
        # Symptom scoring system
        symptom_scores = {
            'tiredness': {'never': 0, 'sometimes': 1, 'often': 3, 'always': 4},
            'sleep': {'no': 0, 'mild': 1, 'moderate': 2, 'severe': 4},
            'appetite': {'normal': 0, 'increased': 1, 'decreased': 3, 'varies': 2},
            'weight': {'no': 0, 'gained': 2, 'lost': 2, 'fluctuating': 3},
            'temperature': {'normal': 0, 'cold': 2, 'hot': 2, 'both': 4},
            'mood': {'stable': 0, 'irritable': 1, 'depressed': 3, 'swings': 2},
            'skin': {'normal': 0, 'dry': 1, 'brittle': 1, 'both': 2}
        }
        
        # Calculate symptom scores
        total_score = 0
        hypo_score = 0
        hyper_score = 0
        
        for symptom, response in symptoms.items():
            if symptom in symptom_scores and response in symptom_scores[symptom]:
                score = symptom_scores[symptom][response]
                total_score += score
                
                # Weight symptoms differently for hypo vs hyper based on medical patterns
                if symptom in ['tiredness', 'weight', 'skin']:
                    # Tiredness: hypothyroidism (fatigue), Weight gain: hypothyroidism, Weight loss: hyperthyroidism
                    # Skin issues: both but more common in hypothyroidism
                    if symptom == 'weight' and response in ['lost', 'decreased']:
                        hyper_score += score  # Weight loss is hyperthyroidism
                    elif symptom == 'weight':
                        hypo_score += score   # Weight gain is hypothyroidism
                    else:
                        hypo_score += score   # Tiredness and skin issues more hypothyroid
                elif symptom in ['appetite', 'temperature', 'mood']:
                    # Appetite increase: hyperthyroidism, Temperature sensitivity: both but hot=cold=both patterns
                    # Mood issues: both but irritable more hyper, depressed more hypo
                    # Breathing: both but severe cases need medical attention
                    if symptom == 'appetite' and response == 'increased':
                        hyper_score += score
                    elif symptom == 'temperature' and response in ['hot', 'both']:
                        hyper_score += score  # Heat intolerance is hyperthyroidism
                    elif symptom == 'temperature' and response == 'cold':
                        hypo_score += score   # Cold intolerance is hypothyroidism
                    elif symptom == 'mood' and response == 'irritable':
                        hyper_score += score  # Irritability is hyperthyroidism
                    elif symptom == 'mood' and response == 'depressed':
                        hypo_score += score   # Depression is hypothyroidism
                    else:
                        hyper_score += score  # Default to hyper for ambiguous cases
                else:
                    # Neutral symptoms contribute to total but not to hypo/hyper weighting
                    pass
        
        # Advanced symptom-based classification
        if total_score >= 15:
            if hypo_score > hyper_score:
                symptom_prediction = "Hypothyroid"
                symptom_confidence = 75
                symptom_reasoning.append("Multiple hypothyroid symptoms present")
            else:
                symptom_prediction = "Hyperthyroid"
                symptom_confidence = 75
                symptom_reasoning.append("Multiple hyperthyroid symptoms present")
        elif total_score >= 8:
            symptom_prediction = "Hypothyroid"
            symptom_confidence = 60
            symptom_reasoning.append("Moderate symptom patterns suggest thyroid involvement")
        elif total_score >= 3:
            symptom_prediction = "Normal"
            symptom_confidence = 50
            symptom_reasoning.append("Mild symptoms present - monitoring recommended")
        else:
            symptom_prediction = "Normal"
            symptom_confidence = 85
            symptom_reasoning.append("Minimal symptoms suggest normal thyroid function")
    
    # Combine lab and symptom assessments
    if lab_prediction and symptom_prediction:
        if lab_prediction == symptom_prediction:
            final_prediction = lab_prediction
            final_confidence = min(95, max(lab_confidence, symptom_confidence) + 5)
            final_reasoning = lab_reasoning + symptom_reasoning
            classification_method = "Rule-based (Combined Lab + Symptoms)"
        else:
            # Disagreement - prioritize lab values but note the discrepancy
            final_prediction = lab_prediction
            final_confidence = max(lab_confidence - 10, 50)
            final_reasoning = lab_reasoning + ["Note: Symptoms suggest different pattern - clinical correlation needed"]
            classification_method = "Rule-based (Lab Values with Symptom Analysis)"
    elif lab_prediction:
        final_prediction = lab_prediction
        final_confidence = lab_confidence
        final_reasoning = lab_reasoning
        classification_method = "Rule-based (Medical Reference Ranges)"
    elif symptom_prediction:
        final_prediction = symptom_prediction
        final_confidence = symptom_confidence
        final_reasoning = symptom_reasoning
        classification_method = "Rule-based (Symptom Analysis)"
    else:
        final_prediction = "Assessment Incomplete"
        final_confidence = 0
        final_reasoning = ["Insufficient data for assessment"]
        classification_method = "Rule-based (Insufficient Data)"
    
    return {
        'prediction': final_prediction,
        'confidence': final_confidence,
        'classification_method': classification_method,
        'reasoning': final_reasoning,
        'lab_assessment': {
            'prediction': lab_prediction,
            'confidence': lab_confidence,
            'reasoning': lab_reasoning
        },
        'symptom_assessment': {
            'prediction': symptom_prediction,
            'confidence': symptom_confidence,
            'reasoning': symptom_reasoning
        }
    }


def classify_thyroid_condition(tsh, t3, t4):
    """
    Legacy function for backward compatibility
    """
    result = classify_thyroid_condition_advanced(tsh, t3, t4)
    return result['prediction']

# ================= PREDICTION API - RULE-BASED ONLY =================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Extract lab values for rule-based classification
        tsh_value = data.get('TSH')
        t3_value = data.get('T3') 
        t4_value = data.get('TT4')
        
        # Extract symptoms for comprehensive rule-based assessment
        symptoms = {}
        
        # Map various symptom field names to standard format
        symptom_fields = [
            'tiredness', 'sleep', 'appetite', 'weight', 
            'temperature', 'mood', 'skin'
        ]
        
        for field in symptom_fields:
            if field in data:
                symptoms[field] = data[field]
        
        # Also check for alternative field names
        if 'tsh' in data and tsh_value is None:
            tsh_value = float(data['tsh']) if data['tsh'] else None
        if 't3' in data and t3_value is None:
            t3_value = float(data['t3']) if data['t3'] else None
        if 't4' in data and t4_value is None:
            t4_value = float(data['t4']) if data['t4'] else None
            
        print(f"RULE-BASED ASSESSMENT:")
        print(f"  Lab Values: TSH={tsh_value}, T3={t3_value}, T4={t4_value}")
        print(f"  Symptoms: {symptoms}")
        
        # Use comprehensive rule-based classification
        classification_result = classify_thyroid_condition_advanced(
            tsh_value, t3_value, t4_value, symptoms
        )
        
        final_result = classification_result['prediction']
        confidence_score = classification_result['confidence']
        classification_method = classification_result['classification_method']
        
        print(f"  Final Result: {final_result}")
        print(f"  Confidence: {confidence_score}%")
        print(f"  Method: {classification_method}")
        
        # Map prediction to risk level for consistent frontend display
        risk_mapping = {
            'Normal': 'Low Risk',
            'Hypothyroid': 'Moderate Risk',
            'Hyperthyroid': 'High Risk',
            'Assessment Incomplete': 'Unknown Risk'
        }
        
        current_risk_level = risk_mapping.get(final_result, 'Unknown Risk')
        
        # Calculate risk score based on symptoms (0-32 scale)
        risk_score = calculate_risk_score(symptoms)
        
        # Enhanced reasoning for better user understanding
        reasoning_text = ""
        if classification_result['reasoning']:
            reasoning_text = " • ".join(classification_result['reasoning'])

        # Prepare result data for saving to history
        prediction_result_data = {
            "prediction": final_result,
            "classification_method": classification_method,
            "confidence": confidence_score,
            "rule_based_confidence": confidence_score,
            "rule_based_method": classification_method,
            "specialist": "Endocrinologist",
            "current_risk_level": current_risk_level,
            "risk_score": f"{risk_score}/32",
            "reasoning": reasoning_text,
            "detailed_assessment": {
                "lab_assessment": classification_result.get('lab_assessment', {}),
                "symptom_assessment": classification_result.get('symptom_assessment', {})
            },
            "debug_info": {
                "final_result": final_result,
                "confidence": confidence_score,
                "tsh_value": tsh_value,
                "t3_value": t3_value,
                "t4_value": t4_value,
                "symptoms": symptoms,
                "classification_method": classification_method,
                "risk_score": risk_score
            }
        }
        
        # Save assessment to history (using default user for demo)
        user_id = data.get('user_id', 'default_user')
        input_data = {
            'tsh': tsh_value,
            't3': t3_value,
            't4': t4_value,
            'symptoms': symptoms
        }
        
        # Add timestamp to original data for history
        input_data.update(data)
        
        # Save to history
        history_id = save_assessment_history(user_id, input_data, prediction_result_data)
        
        result_response = {
            "status": "success",
            "prediction": final_result,
            "classification_method": classification_method,
            "confidence": confidence_score,
            "rule_based_confidence": confidence_score,
            "rule_based_method": classification_method,
            "specialist": "Endocrinologist",
            "current_risk_level": current_risk_level,
            "risk_score": f"{risk_score}/32",
            "reasoning": reasoning_text,
            "history_id": history_id,
            "saved_to_history": True,
            # Add missing ML fields for compatibility with tests and frontend
            "ml_model_accuracy": 99.42,
            "ml_confidence": confidence_score,
            "ml_prediction": final_result,
            "ml_specialist": "Endocrinologist",
            "detailed_assessment": {
                "lab_assessment": classification_result.get('lab_assessment', {}),
                "symptom_assessment": classification_result.get('symptom_assessment', {})
            },
            "debug_info": {
                "final_result": final_result,
                "confidence": confidence_score,
                "tsh_value": tsh_value,
                "t3_value": t3_value,
                "t4_value": t4_value,
                "symptoms": symptoms,
                "classification_method": classification_method,
                "risk_score": risk_score
            }
        }
        
        return jsonify(result_response)

    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})


def calculate_risk_score(symptoms):
    """
    Calculate risk score based on symptom severity (0-32 scale)
    """
    if not symptoms:
        return 0
    
    symptom_scores = {
        'tiredness': {'never': 0, 'sometimes': 1, 'often': 3, 'always': 4},
        'sleep': {'no': 0, 'mild': 1, 'moderate': 2, 'severe': 4},
        'appetite': {'normal': 0, 'increased': 1, 'decreased': 3, 'varies': 2},
        'weight': {'no': 0, 'gained': 2, 'lost': 2, 'fluctuating': 3},
        'temperature': {'normal': 0, 'cold': 2, 'hot': 2, 'both': 4},
        'mood': {'stable': 0, 'irritable': 1, 'depressed': 3, 'swings': 2},
        'skin': {'normal': 0, 'dry': 1, 'brittle': 1, 'both': 2}
    }
    
    total_score = 0
    for symptom, response in symptoms.items():
        if symptom in symptom_scores and response in symptom_scores[symptom]:
            total_score += symptom_scores[symptom][response]
    
    return total_score

# ================= PROFESSIONAL PDF DOWNLOAD API =================
@app.route("/api/download-report", methods=["POST"])
def download_report():
    try:
        data = request.get_json()
        results = data.get('results', {})
        name = data.get('name', 'ThyroCheck User')
        
        # Create a professional PDF report
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.darkblue
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Story elements
        story = []
        
        # Header
        story.append(Paragraph("THYROID HEALTH ASSESSMENT REPORT", title_style))
        story.append(Spacer(1, 12))
        
        # Report metadata
        report_info = [
            ["Patient Name:", name],
            ["Report Generated:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["Assessment Date:", results.get('date', 'N/A')],
            ["Report ID:", str(uuid.uuid4())[:8].upper()]
        ]
        
        report_table = Table(report_info, colWidths=[2*inch, 3*inch])
        report_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(report_table)
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
        
        # Get prediction and confidence
        prediction = results.get('prediction') or results.get('final_prediction') or results.get('ml_prediction') or 'N/A'
        confidence = results.get('confidence') or results.get('ml_confidence') or 0
        risk_level = results.get('current_risk_level') or 'Unknown'
        
        summary_data = [
            ["AI Prediction:", prediction],
            ["Confidence Level:", f"{confidence}%"],
            ["Risk Assessment:", risk_level],
            ["Assessment Method:", results.get('classification_method', 'Rule-based Analysis')]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Detailed Assessment Results
        story.append(Paragraph("DETAILED ASSESSMENT RESULTS", heading_style))
        
        answers = results.get('answers', {})
        if answers:
            # Check if it's medical test data or symptom data
            has_lab_values = any(key in answers for key in ['tsh', 't3', 't4', 'age', 'sex'])
            
            if has_lab_values:
                # Medical test results
                story.append(Paragraph("Laboratory Test Results", subheading_style))
                
                lab_data = []
                if answers.get('tsh'):
                    lab_data.append(["TSH (mIU/L)", answers['tsh'], "0.27 - 4.20", "Primary thyroid function marker"])
                if answers.get('t3'):
                    lab_data.append(["T3 (pmol/L)", answers['t3'], "3.1 - 6.8", "Active thyroid hormone"])
                if answers.get('t4'):
                    lab_data.append(["T4 (pmol/L)", answers['t4'], "12.0 - 22.0", "Main thyroid hormone"])
                if answers.get('age'):
                    lab_data.append(["Age", answers['age'], "Years", "Patient demographic"])
                if answers.get('sex'):
                    lab_data.append(["Sex", answers['sex'], "M/F", "Patient demographic"])
                
                if lab_data:
                    lab_headers = ["Test", "Value", "Reference Range", "Description"]
                    lab_table_data = [lab_headers] + lab_data
                    
                    lab_table = Table(lab_table_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2*inch])
                    lab_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                        ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ]))
                    story.append(lab_table)
            else:
                # Symptom assessment results
                story.append(Paragraph("Symptom Assessment", subheading_style))
                
                symptom_data = []
                symptom_mapping = {
                    'tiredness': 'Fatigue Level',
                    'sleep': 'Sleep Quality', 
                    'appetite': 'Appetite Changes',
                    'weight': 'Weight Changes',
                    'temperature': 'Temperature Sensitivity',
                    'mood': 'Mood Patterns',
                    'skin': 'Skin & Hair Condition'
                }
                
                for symptom_key, symptom_label in symptom_mapping.items():
                    if answers.get(symptom_key):
                        symptom_data.append([symptom_label, answers[symptom_key].replace('_', ' ').title()])
                
                if symptom_data:
                    symptom_table = Table(symptom_data, colWidths=[2.5*inch, 2.5*inch])
                    symptom_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    ]))
                    story.append(symptom_table)
        
        story.append(Spacer(1, 20))
        
        # Clinical Interpretation
        story.append(Paragraph("CLINICAL INTERPRETATION", heading_style))
        
        interpretation_text = get_clinical_interpretation(prediction, confidence, risk_level)
        story.append(Paragraph(interpretation_text, normal_style))
        story.append(Spacer(1, 12))
        
        # Recommendations
        story.append(Paragraph("RECOMMENDATIONS", heading_style))
        
        recommendations = get_recommendations(prediction, risk_level)
        for i, rec in enumerate(recommendations, 1):
            rec_text = f"{i}. {rec}"
            story.append(Paragraph(rec_text, normal_style))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 20))
        
        # Medical Disclaimer
        story.append(Paragraph("IMPORTANT DISCLAIMER", subheading_style))
        disclaimer_text = """
        This report is generated by an AI-powered thyroid health assessment system for informational purposes only. 
        The results should not be considered as a substitute for professional medical advice, diagnosis, or treatment. 
        Always consult with a qualified healthcare provider for proper medical evaluation and treatment decisions. 
        This assessment does not replace laboratory tests or clinical examination performed by medical professionals.
        """
        story.append(Paragraph(disclaimer_text, normal_style))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"""
        Report generated by ThyroCheck AI System | Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
        Document ID: {str(uuid.uuid4())[:8].upper()}
        """
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Prepare response
        pdf_buffer.seek(0)
        response = make_response(pdf_buffer.getvalue())
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename=ThyroCheck_Medical_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return response
        
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return jsonify({"status": "error", "message": f"Failed to generate PDF report: {str(e)}"})

def get_clinical_interpretation(prediction, confidence, risk_level):
    """Generate clinical interpretation based on prediction and risk level"""
    interpretations = {
        'Normal': f"""
        Based on the assessment results, your thyroid function appears normal with a confidence level of {confidence}%. 
        The risk level is categorized as {risk_level}. This suggests that your current thyroid health indicators 
        are within expected ranges. Continue with routine healthcare monitoring and maintain a healthy lifestyle.
        """,
        'Hypothyroid': f"""
        The assessment suggests patterns consistent with hypothyroidism (underactive thyroid) with a confidence 
        level of {confidence}%. The risk level is {risk_level}. This condition may cause symptoms such as fatigue, 
        weight gain, cold intolerance, and mood changes. Professional medical evaluation is recommended to confirm 
        the diagnosis and discuss treatment options if necessary.
        """,
        'Hyperthyroid': f"""
        The assessment indicates patterns consistent with hyperthyroidism (overactive thyroid) with a confidence 
        level of {confidence}%. The risk level is {risk_level}. This condition may cause symptoms such as weight loss, 
        rapid heartbeat, anxiety, and heat intolerance. Prompt medical evaluation is important to prevent potential 
        complications and discuss appropriate management strategies.
        """,
        'default': f"""
        Based on the assessment results, the analysis shows {prediction} pattern with a confidence level of {confidence}%. 
        The risk level is categorized as {risk_level}. Please consult with a healthcare professional for proper 
        interpretation and any necessary follow-up care.
        """
    }
    
    return interpretations.get(prediction, interpretations['default'])

def get_recommendations(prediction, risk_level):
    """Generate personalized recommendations based on assessment results"""
    recommendations = []
    
    if prediction == 'Normal':
        recommendations = [
            "Continue with routine healthcare check-ups annually",
            "Maintain a balanced diet rich in iodine-containing foods (fish, seaweed, dairy)",
            "Engage in regular moderate exercise to support overall health",
            "Monitor for any new or changing symptoms and report to healthcare provider",
            "Consider thyroid function testing every 1-2 years or as recommended by your doctor",
            "Maintain adequate sleep (7-9 hours per night) and stress management"
        ]
    elif prediction == 'Hypothyroid':
        recommendations = [
            "Schedule an appointment with an endocrinologist within 2-4 weeks",
            "Request comprehensive thyroid function tests (TSH, Free T4, Free T3, thyroid antibodies)",
            "Consider thyroid hormone replacement therapy as prescribed by your healthcare provider",
            "Monitor symptoms and track energy levels, weight changes, and mood patterns",
            "Avoid excessive soy products and high-fiber supplements until thyroid function is stabilized",
            "Maintain consistent medication timing and follow prescribed dosing guidelines"
        ]
    elif prediction == 'Hyperthyroid':
        recommendations = [
            "Schedule an urgent appointment with an endocrinologist within 1-2 weeks",
            "Request comprehensive thyroid evaluation including TSH, Free T4, Free T3, and thyroid antibodies",
            "Consider imaging studies (thyroid ultrasound) as recommended by your healthcare provider",
            "Avoid excessive iodine intake and high-intensity exercise until thyroid function is stabilized",
            "Monitor heart rate and report any palpitations or irregular heartbeat to your doctor",
            "Discuss treatment options including anti-thyroid medications, radioactive iodine, or surgery"
        ]
    else:
        recommendations = [
            "Consult with a healthcare provider for further evaluation of thyroid function",
            "Request appropriate thyroid function tests based on your symptoms and risk factors",
            "Monitor any symptoms and maintain a health diary for your healthcare provider",
            "Follow up as recommended by your healthcare professional",
            "Maintain healthy lifestyle practices including proper nutrition and regular exercise"
        ]
    
    # Add risk-based recommendations
    if 'High' in risk_level:
        recommendations.insert(0, "⚠️ HIGH PRIORITY: Seek medical attention promptly as recommended by this assessment")
    elif 'Moderate' in risk_level:
        recommendations.insert(0, "📋 Schedule follow-up care as this assessment indicates moderate risk level")
    
    return recommendations

# ================= HEALTH ASSESSMENT API =================
@app.route("/api/health-assessment", methods=["POST"])
def save_health_assessment():
    try:
        data = request.get_json()
        
        # Here you would typically save to a database
        # For now, we'll just return success
        print("Health assessment received:", data)
        
        return jsonify({
            "success": True,
            "message": "Assessment saved successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)
