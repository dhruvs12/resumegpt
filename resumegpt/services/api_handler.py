from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from .resume_improver import ResumeImprover
from ..models.resume import JobPortalData, ResumeRequest
import json

# Create a Blueprint instead of a Flask app
api = Blueprint('api', __name__)

@api.route('/tailor-resume', methods=['POST', 'OPTIONS'])
@cross_origin()
def tailor_resume():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        print("Received request with content type:", request.content_type)
        print("Request headers:", dict(request.headers))
        
        data = request.get_json()
        print("Received data:", json.dumps(data, indent=2) if data else "No data")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400
            
        if 'jobHtml' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing jobHtml in request'
            }), 400
            
        if 'resumeData' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing resumeData in request'
            }), 400
            
        job_html = data.get('jobHtml')
        resume_data = data.get('resumeData')
        
        # Validate resume_data format
        if not isinstance(resume_data, dict):
            try:
                resume_data = json.loads(resume_data)
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'resumeData must be a valid JSON object'
                }), 400
        
        print("Processing resume with job HTML length:", len(job_html))
        print("Resume data structure:", json.dumps(resume_data, indent=2))
        
        improver = ResumeImprover()
        result = improver.process_resume(
            resume_data=resume_data,
            job_html=job_html
        )
        
        if result and isinstance(result, dict):
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to tailor resume.'
            }), 500
            
    except Exception as e:
        print(f"API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 