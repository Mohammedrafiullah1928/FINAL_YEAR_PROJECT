"""
Web Server for Pedestrian Navigation System
Provides real-time obstacle mapping with GPS integration
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
import json
import os
import sys

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pedestrian-nav-secret-key-2025'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for obstacles (use database for production)
obstacles = []
MAX_OBSTACLES = 1000  # Limit stored obstacles

# User location tracking
active_users = {}

class ObstacleDatabase:
    """Manages obstacle data with location information"""
    
    def __init__(self):
        self.obstacles = []
        self.next_id = 1
    
    def add_obstacle(self, obstacle_data):
        """Add new obstacle with timestamp and ID"""
        obstacle = {
            'id': self.next_id,
            'type': obstacle_data.get('type', 'unknown'),
            'confidence': obstacle_data.get('confidence', 0),
            'latitude': obstacle_data.get('latitude', 0),
            'longitude': obstacle_data.get('longitude', 0),
            'timestamp': datetime.now().isoformat(),
            'severity': obstacle_data.get('severity', 'medium'),
            'description': obstacle_data.get('description', ''),
            'user_id': obstacle_data.get('user_id', 'anonymous')
        }
        
        self.obstacles.append(obstacle)
        self.next_id += 1
        
        # Limit storage
        if len(self.obstacles) > MAX_OBSTACLES:
            self.obstacles.pop(0)
        
        return obstacle
    
    def get_nearby_obstacles(self, lat, lon, radius_km=1.0):
        """Get obstacles within radius of location"""
        nearby = []
        
        for obs in self.obstacles:
            distance = self._calculate_distance(
                lat, lon, 
                obs['latitude'], obs['longitude']
            )
            
            if distance <= radius_km:
                obs_copy = obs.copy()
                obs_copy['distance_km'] = round(distance, 2)
                nearby.append(obs_copy)
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        return nearby
    
    def get_all_obstacles(self):
        """Get all obstacles"""
        return self.obstacles
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two GPS coordinates (Haversine formula)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

# Initialize database
db = ObstacleDatabase()


@app.route('/')
def index():
    """Main map interface with live camera"""
    return render_template('map_live.html')

@app.route('/map')
def map_view():
    """Original map interface"""
    return render_template('map.html')

@app.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    return render_template('dashboard.html')

@app.route('/api/obstacles', methods=['GET'])
def get_obstacles():
    """API endpoint to get all obstacles"""
    return jsonify({
        'success': True,
        'count': len(db.obstacles),
        'obstacles': db.get_all_obstacles()
    })

@app.route('/api/obstacles/nearby', methods=['POST'])
def get_nearby_obstacles():
    """API endpoint to get obstacles near a location"""
    data = request.json
    lat = data.get('latitude', 0)
    lon = data.get('longitude', 0)
    radius = data.get('radius_km', 1.0)
    
    nearby = db.get_nearby_obstacles(lat, lon, radius)
    
    return jsonify({
        'success': True,
        'count': len(nearby),
        'obstacles': nearby
    })

@app.route('/api/obstacles/report', methods=['POST'])
def report_obstacle():
    """API endpoint to report new obstacle"""
    data = request.json
    
    # Validate required fields
    if not data.get('latitude') or not data.get('longitude'):
        return jsonify({
            'success': False,
            'error': 'Latitude and longitude required'
        }), 400
    
    # Add obstacle
    obstacle = db.add_obstacle(data)
    
    # Broadcast to all connected clients
    socketio.emit('new_obstacle', obstacle, broadcast=True)
    
    return jsonify({
        'success': True,
        'obstacle': obstacle
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about detected obstacles"""
    obstacles_list = db.get_all_obstacles()
    
    # Calculate statistics
    total = len(obstacles_list)
    
    # Count by type
    type_counts = {}
    severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    
    for obs in obstacles_list:
        obs_type = obs.get('type', 'unknown')
        type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
        
        severity = obs.get('severity', 'medium')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return jsonify({
        'success': True,
        'total_obstacles': total,
        'by_type': type_counts,
        'by_severity': severity_counts,
        'active_users': len(active_users)
    })


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print(f'Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print(f'Client disconnected: {request.sid}')
    if request.sid in active_users:
        del active_users[request.sid]

@socketio.on('update_location')
def handle_location_update(data):
    """Update user's current location"""
    active_users[request.sid] = {
        'latitude': data.get('latitude'),
        'longitude': data.get('longitude'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Get nearby obstacles
    nearby = db.get_nearby_obstacles(
        data.get('latitude', 0),
        data.get('longitude', 0),
        radius_km=0.5  # 500m radius
    )
    
    emit('nearby_obstacles', {
        'obstacles': nearby,
        'count': len(nearby)
    })

@socketio.on('report_detection')
def handle_detection(data):
    """Handle real-time obstacle detection from client"""
    obstacle = db.add_obstacle(data)
    
    # Broadcast to all clients
    emit('new_obstacle', obstacle, broadcast=True)
    
    # Send confirmation to reporter
    emit('report_confirmed', {'obstacle_id': obstacle['id']})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🗺️  PEDESTRIAN NAVIGATION WEB SERVER")
    print("="*60)
    print("\n📍 Access the map at: http://localhost:5000")
    print("📊 Access dashboard at: http://localhost:5000/dashboard")
    print("\n🔌 WebSocket enabled for real-time updates")
    print("🌐 CORS enabled for mobile app integration")
    print("\n💡 API Endpoints:")
    print("   GET  /api/obstacles - Get all obstacles")
    print("   POST /api/obstacles/nearby - Get nearby obstacles")
    print("   POST /api/obstacles/report - Report new obstacle")
    print("   GET  /api/stats - Get statistics")
    print("\n" + "="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
