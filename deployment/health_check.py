#!/bin/bash

# Health check endpoint for monitoring
# Add this to your Flask app

from flask import Blueprint, jsonify
from app.extensions import db
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check if we can write to disk
        test_file = '/tmp/health_check.txt'
        with open(test_file, 'w') as f:
            f.write('OK')
        os.remove(test_file)
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'filesystem': 'writable'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@health_bp.route('/ready')
def readiness_check():
    """Readiness check for Kubernetes/Docker deployments"""
    return jsonify({'status': 'ready'}), 200

@health_bp.route('/live')
def liveness_check():
    """Liveness check for Kubernetes/Docker deployments"""
    return jsonify({'status': 'alive'}), 200
