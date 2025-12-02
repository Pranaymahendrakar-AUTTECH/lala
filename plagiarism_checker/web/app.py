"""
Flask web application for plagiarism checking.
"""

import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from ..core.checker import PlagiarismChecker


def create_app(config: dict = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured Flask application
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Default configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = '/tmp/plagiarism_uploads'

    # Apply custom config
    if config:
        app.config.update(config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Create checker instance
    checker = PlagiarismChecker()

    @app.route('/')
    def index():
        """Render the main page."""
        return render_template('index.html')

    @app.route('/check', methods=['POST'])
    def check_plagiarism():
        """
        Check text for plagiarism.

        Accepts either:
        - JSON with 'text1' and 'text2' fields
        - Form data with 'text1' and 'text2' fields
        - Two uploaded files
        """
        try:
            text1 = None
            text2 = None
            threshold = 0.3

            # Get threshold
            if request.is_json:
                threshold = request.json.get('threshold', 0.3)
            else:
                threshold = float(request.form.get('threshold', 0.3))

            checker.threshold = threshold

            # Try to get texts from JSON
            if request.is_json:
                data = request.json
                text1 = data.get('text1', '')
                text2 = data.get('text2', '')

            # Try to get texts from form data
            elif request.form:
                text1 = request.form.get('text1', '')
                text2 = request.form.get('text2', '')

            # Try to get texts from uploaded files
            if request.files:
                if 'file1' in request.files and request.files['file1'].filename:
                    file1 = request.files['file1']
                    text1 = file1.read().decode('utf-8', errors='ignore')

                if 'file2' in request.files and request.files['file2'].filename:
                    file2 = request.files['file2']
                    text2 = file2.read().decode('utf-8', errors='ignore')

            # Validate inputs
            if not text1 or not text2:
                return jsonify({
                    'error': 'Please provide two texts or files to compare'
                }), 400

            if not text1.strip() or not text2.strip():
                return jsonify({
                    'error': 'Both texts must contain content'
                }), 400

            # Perform plagiarism check
            result = checker.check(text1, text2)

            return jsonify({
                'success': True,
                'result': result.to_dict(),
                'text1_length': len(text1),
                'text2_length': len(text2)
            })

        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500

    @app.route('/compare-texts', methods=['POST'])
    def compare_texts():
        """Compare two text strings and return detailed scores."""
        try:
            if not request.is_json:
                return jsonify({'error': 'JSON data required'}), 400

            data = request.json
            text1 = data.get('text1', '')
            text2 = data.get('text2', '')

            if not text1 or not text2:
                return jsonify({'error': 'Both text1 and text2 are required'}), 400

            scores = checker.compare_texts(text1, text2)

            return jsonify({
                'success': True,
                'scores': {k: round(v * 100, 2) for k, v in scores.items()}
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'version': '1.0.0'})

    return app


def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the Flask development server.

    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server(debug=True)
