#Warning If the Id pass leaked then
from flask import Flask, render_template, request, jsonify, session
import requests
import sqlite3
import threading
import time
from datetime import datetime, timedelta
import hashlib
import os
import re
import traceback
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
app.secret_key = "naruto_tools_secret_key_2024"

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('naruto_tools.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        uid TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bot_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        user_uid TEXT NOT NULL,
        bot_id TEXT NOT NULL,
        bot_uid TEXT NOT NULL,
        bot_password TEXT NOT NULL,
        started_at TIMESTAMP NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        instance_id TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bot_usage_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id TEXT NOT NULL,
        total_uses INTEGER DEFAULT 0,
        last_used TIMESTAMP
    )''')
    
    conn.commit()
    
    bots = get_bots_list()
    for bot in bots:
        c.execute("INSERT OR IGNORE INTO bot_usage_stats (bot_id, total_uses) VALUES (?, 0)", (bot['id'],))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

# ==================== ALL 88 BOTS ====================
def get_bots_list():
    bots = []
    bot_data = [
        ("bot_1", "4620004865", "RAGHAVLIKEBOT_RAGHAV_GMYXS"),
        ("bot_2", "4620004864", "RAGHAVLIKEBOT_RAGHAV_YZBE2"),
        ("bot_3", "4620004788", "RAGHAVLIKEBOT_RAGHAV_P3YKM"),
        ("bot_4", "4620004786", "RAGHAVLIKEBOT_RAGHAV_9XNO9"),
        ("bot_5", "4620004847", "RAGHAVLIKEBOT_RAGHAV_2MNLL"),
        ("bot_6", "4620004793", "RAGHAVLIKEBOT_RAGHAV_BVXA7"),
        ("bot_7", "4620004856", "RAGHAVLIKEBOT_RAGHAV_QHJGS"),
        ("bot_8", "4620004823", "RAGHAVLIKEBOT_RAGHAV_34E4X"),
        ("bot_9", "4620004801", "RAGHAVLIKEBOT_RAGHAV_O40F7"),
        ("bot_10", "4620006086", "RAGHAVLIKEBOT_RAGHAV_YEKG7"),
        ("bot_11", "4620006085", "RAGHAVLIKEBOT_RAGHAV_VQ3QK"),
        ("bot_12", "4620004868", "RAGHAVLIKEBOT_RAGHAV_1C3JO"),
        ("bot_13", "4620006136", "RAGHAVLIKEBOT_RAGHAV_1H5A0"),
        ("bot_14", "4620006092", "RAGHAVLIKEBOT_RAGHAV_EJMWX"),
        ("bot_15", "4620004854", "RAGHAVLIKEBOT_RAGHAV_2RT1U"),
        ("bot_16", "4620006141", "RAGHAVLIKEBOT_RAGHAV_QRSOJ"),
        ("bot_17", "4620006129", "RAGHAVLIKEBOT_RAGHAV_RXPPX"),
        ("bot_18", "4620004804", "RAGHAVLIKEBOT_RAGHAV_ODTZZ"),
        ("bot_19", "4620006132", "RAGHAVLIKEBOT_RAGHAV_W0MAV"),
        ("bot_20", "4620004836", "RAGHAVLIKEBOT_RAGHAV_L0062"),
        ("bot_21", "4620008077", "RAGHAVLIKEBOT_RAGHAV_S0A96"),
        ("bot_22", "4620008082", "RAGHAVLIKEBOT_RAGHAV_IXLO1"),
        ("bot_23", "4620008641", "RAGHAVLIKEBOT_RAGHAV_SHEAD"),
        ("bot_24", "4620009177", "RAGHAVLIKEBOT_RAGHAV_R0Y5P"),
        ("bot_25", "4620009209", "RAGHAVLIKEBOT_RAGHAV_IXEW2"),
        ("bot_26", "4620006091", "RAGHAVLIKEBOT_RAGHAV_AGZUL"),
        ("bot_27", "4620008085", "RAGHAVLIKEBOT_RAGHAV_97HHH"),
        ("bot_28", "4620009625", "RAGHAVLIKEBOT_RAGHAV_M6I3R"),
        ("bot_29", "4620010005", "RAGHAVLIKEBOT_RAGHAV_BZEX2"),
        ("bot_30", "4620004821", "RAGHAVLIKEBOT_RAGHAV_66M7Q"),
        ("bot_31", "4620009199", "RAGHAVLIKEBOT_RAGHAV_8ROU4"),
        ("bot_32", "4620010151", "RAGHAVLIKEBOT_RAGHAV_CL3HY"),
        ("bot_33", "4620009908", "RAGHAVLIKEBOT_RAGHAV_W2WNV"),
        ("bot_34", "4620009186", "RAGHAVLIKEBOT_RAGHAV_RMJZV"),
        ("bot_35", "4620009637", "RAGHAVLIKEBOT_RAGHAV_RHOQA"),
        ("bot_36", "4620010378", "RAGHAVLIKEBOT_RAGHAV_NUXVL"),
        ("bot_37", "4620010771", "RAGHAVLIKEBOT_RAGHAV_5U3MV"),
        ("bot_38", "4620011189", "RAGHAVLIKEBOT_RAGHAV_348O7"),
        ("bot_39", "4620010764", "RAGHAVLIKEBOT_RAGHAV_7H5T3"),
        ("bot_40", "4620011498", "RAGHAVLIKEBOT_RAGHAV_YXURX"),
        ("bot_41", "4620011521", "RAGHAVLIKEBOT_RAGHAV_26ZY1"),
        ("bot_42", "4620010770", "RAGHAVLIKEBOT_RAGHAV_W8H4O"),
        ("bot_43", "4620011704", "RAGHAVLIKEBOT_RAGHAV_CSJKY"),
        ("bot_44", "4620012787", "RAGHAVLIKEBOT_RAGHAV_0IHMW"),
        ("bot_45", "4620012721", "RAGHAVLIKEBOT_RAGHAV_A7UO9"),
        ("bot_46", "4620012807", "RAGHAVLIKEBOT_RAGHAV_ID17O"),
        ("bot_47", "4620013158", "RAGHAVLIKEBOT_RAGHAV_TNU9D"),
        ("bot_48", "4620012176", "RAGHAVLIKEBOT_RAGHAV_105LS"),
        ("bot_49", "4620013327", "RAGHAVLIKEBOT_RAGHAV_7DPO1"),
        ("bot_50", "4620011164", "RAGHAVLIKEBOT_RAGHAV_8IMVL"),
        ("bot_51", "4620013335", "RAGHAVLIKEBOT_RAGHAV_MD3O2"),
        ("bot_52", "4620014419", "RAGHAVLIKEBOT_RAGHAV_YXVN4"),
        ("bot_53", "4620014436", "RAGHAVLIKEBOT_RAGHAV_B2RYR"),
        ("bot_54", "4620014074", "RAGHAVLIKEBOT_RAGHAV_HM5GF"),
        ("bot_55", "4620012722", "RAGHAVLIKEBOT_RAGHAV_MN29F"),
        ("bot_56", "4620012715", "RAGHAVLIKEBOT_RAGHAV_2RXCJ"),
    ]
    bot_data2 = [
        ("bot_57", "4569404694", "RAGHAVLIKESBOT_RAGHAV_EQOY5"),
        ("bot_58", "4569404695", "RAGHAVLIKESBOT_RAGHAV_2THCG"),
        ("bot_59", "4569404696", "RAGHAVLIKESBOT_RAGHAV_52PSF"),
        ("bot_60", "4569404698", "RAGHAVLIKESBOT_RAGHAV_HA0FE"),
        ("bot_61", "4569404701", "RAGHAVLIKESBOT_RAGHAV_NWE7D"),
        ("bot_62", "4569404702", "RAGHAVLIKESBOT_RAGHAV_HU5G4"),
        ("bot_63", "4569404704", "RAGHAVLIKESBOT_RAGHAV_IAH32"),
        ("bot_64", "4569404705", "RAGHAVLIKESBOT_RAGHAV_BHIV0"),
        ("bot_65", "4569404707", "RAGHAVLIKESBOT_RAGHAV_FJOCY"),
        ("bot_66", "4569404711", "RAGHAVLIKESBOT_RAGHAV_8SQRK"),
        ("bot_67", "4569404717", "RAGHAVLIKESBOT_RAGHAV_1X48C"),
        ("bot_68", "4569404725", "RAGHAVLIKESBOT_RAGHAV_M3WOT"),
        ("bot_69", "4569404727", "RAGHAVLIKESBOT_RAGHAV_N79F5"),
        ("bot_70", "4569404734", "RAGHAVLIKESBOT_RAGHAV_IISYK"),
        ("bot_71", "4569404735", "RAGHAVLIKESBOT_RAGHAV_97Z4R"),
        ("bot_72", "4569404742", "RAGHAVLIKESBOT_RAGHAV_UG67E"),
        ("bot_73", "4569404747", "RAGHAVLIKESBOT_RAGHAV_11IUZ"),
        ("bot_74", "4569404785", "RAGHAVLIKESBOT_RAGHAV_6H5B8"),
        ("bot_75", "4569404788", "RAGHAVLIKESBOT_RAGHAV_B1NHZ"),
        ("bot_76", "4569404789", "RAGHAVLIKESBOT_RAGHAV_T76O6"),
        ("bot_77", "4569404791", "RAGHAVLIKESBOT_RAGHAV_CAJ8V"),
        ("bot_78", "4569404805", "RAGHAVLIKESBOT_RAGHAV_WQT1N"),
        ("bot_79", "4569404812", "RAGHAVLIKESBOT_RAGHAV_C3O6B"),
        ("bot_80", "4569404828", "RAGHAVLIKESBOT_RAGHAV_V2LXY"),
        ("bot_81", "4569404870", "RAGHAVLIKESBOT_RAGHAV_DZUWO"),
        ("bot_82", "4569405038", "RAGHAVLIKESBOT_RAGHAV_07TMR"),
        ("bot_83", "4569405048", "RAGHAVLIKESBOT_RAGHAV_CKGZL"),
        ("bot_84", "4569405049", "RAGHAVLIKESBOT_RAGHAV_MGNB6"),
        ("bot_85", "4569405052", "RAGHAVLIKESBOT_RAGHAV_2WIO6"),
        ("bot_86", "4569405053", "RAGHAVLIKESBOT_RAGHAV_UFO9S"),
        ("bot_87", "4569407545", "RAGHAVLIKESBOT_RAGHAV_C8LTI"),
        ("bot_88", "4569407563", "RAGHAVLIKESBOT_RAGHAV_DEOT7"),
    ]
    
    bots = [{"id": b[0], "uid": b[1], "password": b[2]} for b in bot_data] + [{"id": b[0], "uid": b[1], "password": b[2]} for b in bot_data2]
    return bots

# ==================== API ENDPOINTS ====================
API_URLS = {
    'bio': 'https://bioapi.up.railway.app/bio',
    'info': 'https://info-api-production.up.railway.app/player-info',
    'jwt_gen': 'https://jwt-gen-vaibhav.up.railway.app/token',
    'access_jwt': 'https://naruto-access-jwt.vercel.app/token',
    'friend_add': 'https://naruto-friend.vercel.app/add',
    'friend_remove': 'https://naruto-friend.vercel.app/remove',
    'guild_join': 'https://narruto-guild.vercel.app/join',
    'guild_leave': 'https://narruto-guild.vercel.app/leave',
    'item_add': 'https://naruto-item-add.vercel.app/add-profile',
    'level_up': 'https://fflevel.up.railway.app/start',
    'level_stop': 'https://fflevel.up.railway.app/stop',
    'eat_access': 'https://naruto-eat-access-a3sp.vercel.app/Eat'
}

# ==================== TIMESTAMP CONVERTER ====================
def timestamp_to_relative(timestamp):
    try:
        ts = int(timestamp)
        dt = datetime.fromtimestamp(ts)
        now = datetime.now()
        diff = now - dt
        
        years = diff.days // 365
        months = (diff.days % 365) // 30
        days = diff.days % 30
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60
        
        if years > 0:
            return f"{years}y {months}m {days}d ago"
        elif months > 0:
            return f"{months}m {days}d {hours}h ago"
        elif days > 0:
            return f"{days}d {hours}h {minutes}m ago"
        elif hours > 0:
            return f"{hours}h {minutes}m ago"
        elif minutes > 0:
            return f"{minutes}m {seconds}s ago"
        else:
            return f"{seconds}s ago"
    except:
        return "Unknown"

# ==================== EAT ACCESS FUNCTION ====================
def extract_eat_token(input_text):
    input_text = input_text.strip()
    if 'eat=' in input_text:
        parsed = urlparse(input_text)
        params = parse_qs(parsed.query)
        if 'eat' in params:
            return params['eat'][0]
    return input_text

@app.route('/api/eat-access', methods=['POST'])
def eat_access():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        user_input = data.get('eat_link', '').strip()
        if not user_input:
            return jsonify({'success': False, 'error': 'Please provide eat link or token'}), 400
        
        eat_token = extract_eat_token(user_input)
        api_url = f"{API_URLS['eat_access']}?eat_token={eat_token}"
        response = requests.get(api_url, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': '✅ Eat Access Successful!',
                'data': {
                    'account_id': result.get('account_id'),
                    'nickname': result.get('account_nickname'),
                    'access_token': result.get('access_token'),
                    'region': result.get('region'),
                    'credit': result.get('credit')
                }
            })
        else:
            return jsonify({'success': False, 'error': result.get('message', 'Failed')}), 400
    except Exception as e:
        print(f"Eat access error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== AUTO REMOVE THREAD ====================
def start_bot_removal_thread():
    def check_and_remove():
        while True:
            time.sleep(60)
            conn = sqlite3.connect('naruto_tools.db')
            c = conn.cursor()
            now = datetime.now().isoformat()
            
            expired = c.execute("SELECT id, username, user_uid, bot_uid, bot_password, instance_id FROM bot_sessions WHERE expires_at <= ? AND is_active = 1", (now,)).fetchall()
            
            for session_id, username, user_uid, bot_uid, bot_password, instance_id in expired:
                try:
                    if instance_id and instance_id != 'unknown':
                        try:
                            stop_url = f"{API_URLS['level_stop']}/{instance_id}"
                            requests.get(stop_url, timeout=10)
                        except Exception as e:
                            print(f"Stop instance error (ignored): {e}")
                    
                    try:
                        remove_url = f"{API_URLS['friend_remove']}?uid={bot_uid}&password={bot_password}&friend_uid={user_uid}"
                        requests.get(remove_url, timeout=10)
                    except Exception as e:
                        print(f"Remove friend error (ignored): {e}")
                    
                    c.execute("UPDATE bot_sessions SET is_active = 0 WHERE id = ?", (session_id,))
                    conn.commit()
                    
                    bot_id = c.execute("SELECT bot_id FROM bot_sessions WHERE id = ?", (session_id,)).fetchone()
                    if bot_id:
                        c.execute("UPDATE bot_usage_stats SET total_uses = total_uses - 1 WHERE bot_id = ?", (bot_id[0],))
                        conn.commit()
                    
                    print(f"✅ Auto-removed bot session {session_id}")
                except Exception as e:
                    print(f"Auto-remove error: {e}")
            conn.close()
    
    thread = threading.Thread(target=check_and_remove, daemon=True)
    thread.start()
    print("🔄 Auto-removal thread started!")

# ==================== AUTH ROUTES ====================
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        uid = data.get('uid', '').strip() if data.get('uid') else ''
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'error': 'Username must be 3-20 characters'}), 400
        
        if len(password) < 4:
            return jsonify({'success': False, 'error': 'Password must be at least 4 characters'}), 400
        
        conn = sqlite3.connect('naruto_tools.db')
        c = conn.cursor()
        
        existing = c.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, uid) VALUES (?, ?, ?)", 
                  (username, hashed_password, uid if uid else None))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except Exception as e:
        print(f"Register error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        conn = sqlite3.connect('naruto_tools.db')
        c = conn.cursor()
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = c.execute("SELECT id, username, uid FROM users WHERE username = ? AND password = ?", 
                        (username, hashed_password)).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['user_uid'] = user[2] if user[2] else ''
        
        conn.close()
        return jsonify({'success': True, 'message': 'Login successful!', 'username': user[1]})
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out!'})

@app.route('/api/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({
        'username': session.get('username'),
        'user_uid': session.get('user_uid')
    })

# ==================== INFO API ====================
@app.route('/api/user-full-info', methods=['GET'])
def get_user_full_info():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({'error': 'Missing UID'}), 400
    try:
        resp = requests.get(f"{API_URLS['info']}?uid={uid}", timeout=30)
        data = resp.json()
        
        basic = data.get('basicInfo', {})
        if basic.get('createAt'):
            basic['createdAtRelative'] = timestamp_to_relative(basic['createAt'])
        if basic.get('lastLoginAt'):
            basic['lastLoginRelative'] = timestamp_to_relative(basic['lastLoginAt'])
        
        return jsonify(data)
    except Exception as e:
        print(f"Info error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== JWT GENERATORS ====================
@app.route('/api/jwt', methods=['GET'])
def proxy_jwt():
    uid = request.args.get('uid')
    password = request.args.get('password')
    if not uid or not password:
        return jsonify({'error': 'Missing UID or Password'}), 400
    try:
        resp = requests.get(f"{API_URLS['jwt_gen']}?uid={uid}&password={password}", timeout=30)
        data = resp.json()
        if data.get('token'):
            return jsonify({'token': data['token'], 'success': True})
        return jsonify({'error': 'Could not generate JWT'}), 400
    except Exception as e:
        print(f"JWT error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/access-jwt', methods=['GET'])
def proxy_access_jwt():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({'error': 'Missing access_token'}), 400
    try:
        resp = requests.get(f"{API_URLS['access_jwt']}?access_token={access_token}", timeout=30)
        data = resp.json()
        if data.get('jwt'):
            return jsonify({'token': data['jwt'], 'success': True})
        return jsonify({'error': 'Could not generate JWT'}), 400
    except Exception as e:
        print(f"Access JWT error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== PROXY APIS ====================
@app.route('/api/bio', methods=['GET'])
def proxy_bio():
    access = request.args.get('access')
    bio = request.args.get('bio')
    if not access or not bio:
        return jsonify({'error': 'Missing parameters'}), 400
    try:
        resp = requests.get(f"{API_URLS['bio']}?bio={bio}&access={access}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        print(f"Bio error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/friend-add', methods=['GET'])
def proxy_friend_add():
    access_token = request.args.get('access_token')
    friend_uid = request.args.get('friend_uid')
    if not access_token or not friend_uid:
        return jsonify({'error': 'Missing parameters'}), 400
    try:
        resp = requests.get(f"{API_URLS['friend_add']}?access_token={access_token}&friend_uid={friend_uid}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        print(f"Friend add error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/friend-remove', methods=['GET'])
def proxy_friend_remove():
    access_token = request.args.get('access_token')
    friend_uid = request.args.get('friend_uid')
    if not access_token or not friend_uid:
        return jsonify({'error': 'Missing parameters'}), 400
    try:
        resp = requests.get(f"{API_URLS['friend_remove']}?access_token={access_token}&friend_uid={friend_uid}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        print(f"Friend remove error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/guild/join', methods=['POST'])
def guild_join():
    data = request.json
    access_token = data.get('access_token')
    clan_id = data.get('clan_id')
    if not access_token or not clan_id:
        return jsonify({'error': 'Missing parameters'}), 400
    try:
        resp = requests.get(f"{API_URLS['guild_join']}?clan_id={clan_id}&access_token={access_token}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        print(f"Guild join error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/guild/leave', methods=['POST'])
def guild_leave():
    data = request.json
    access_token = data.get('access_token')
    clan_id = data.get('clan_id')
    if not access_token or not clan_id:
        return jsonify({'error': 'Missing parameters'}), 400
    try:
        resp = requests.get(f"{API_URLS['guild_leave']}?clan_id={clan_id}&access_token={access_token}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        print(f"Guild leave error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/item/add', methods=['POST'])
def add_item():
    data = request.json
    jwt_token = data.get('jwt_token')
    item_id = data.get('item_id')
    if not jwt_token or not item_id:
        return jsonify({'error': 'Missing parameters'}), 400
    try:
        resp = requests.get(f"{API_URLS['item_add']}?token={jwt_token}&itemid={item_id}", timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        print(f"Item add error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== LEVEL UP BOT API ====================
@app.route('/api/bots/status')
def get_bots_status():
    conn = sqlite3.connect('naruto_tools.db')
    c = conn.cursor()
    bots = get_bots_list()
    bot_status = []
    for bot in bots:
        active_sessions = c.execute("SELECT COUNT(*) FROM bot_sessions WHERE bot_id = ? AND is_active = 1", (bot['id'],)).fetchone()[0]
        stats = c.execute("SELECT total_uses FROM bot_usage_stats WHERE bot_id = ?", (bot['id'],)).fetchone()
        bot_status.append({
            'id': bot['id'],
            'uid': bot['uid'],
            'is_running': active_sessions > 0,
            'total_uses': stats[0] if stats else 0
        })
    conn.close()
    return jsonify(bot_status)

@app.route('/api/bots/stats')
def get_bots_stats():
    conn = sqlite3.connect('naruto_tools.db')
    c = conn.cursor()
    
    total_bots = len(get_bots_list())
    active_bots = c.execute("SELECT COUNT(DISTINCT bot_id) FROM bot_sessions WHERE is_active = 1").fetchone()[0]
    free_bots = total_bots - active_bots
    
    conn.close()
    return jsonify({
        'total': total_bots,
        'active': active_bots,
        'free': free_bots
    })

@app.route('/api/my-bots', methods=['GET'])
def get_my_bots():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = sqlite3.connect('naruto_tools.db')
    c = conn.cursor()
    
    my_bots = c.execute("""SELECT id, bot_id, bot_uid, started_at, expires_at, instance_id, is_active, user_uid
                           FROM bot_sessions 
                           WHERE username = ? AND is_active = 1 
                           ORDER BY started_at DESC""", (session['username'],)).fetchall()
    
    result = []
    for bot in my_bots:
        result.append({
            'session_id': bot[0],
            'bot_id': bot[1],
            'bot_uid': bot[2],
            'started_at': bot[3],
            'expires_at': bot[4],
            'instance_id': bot[5],
            'is_active': bot[6],
            'user_uid': bot[7]
        })
    
    conn.close()
    return jsonify(result)

@app.route('/api/levelup/start', methods=['POST'])
def start_level_up():
    if 'username' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    data = request.json
    user_uid = data.get('user_uid')
    bot_id = data.get('bot_id')
    username = session.get('username')
    
    if not user_uid or not bot_id:
        return jsonify({'error': 'Missing user_uid or bot_id'}), 400
    
    conn = sqlite3.connect('naruto_tools.db')
    c = conn.cursor()
    
    existing = c.execute("SELECT id FROM bot_sessions WHERE username = ? AND is_active = 1", (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': 'You already have an active bot! Please stop it first.'}), 400
    
    bots = get_bots_list()
    bot = next((b for b in bots if b['id'] == bot_id), None)
    if not bot:
        conn.close()
        return jsonify({'error': 'Invalid bot ID'}), 400
    
    bot_uid = bot['uid']
    bot_password = bot['password']
    
    bot_active = c.execute("SELECT COUNT(*) FROM bot_sessions WHERE bot_id = ? AND is_active = 1", (bot_id,)).fetchone()[0]
    if bot_active > 0:
        conn.close()
        return jsonify({'error': f'{bot_id} is currently in use by another player'}), 400
    
    try:
        # Friend request (ignore error)
        try:
            add_url = f"{API_URLS['friend_add']}?uid={bot_uid}&password={bot_password}&friend_uid={user_uid}"
            requests.get(add_url, timeout=30)
        except Exception as e:
            print(f"Friend add error (ignored): {e}")
        
        # Start level up
        level_url = f"{API_URLS['level_up']}?uid={bot_uid}&password={bot_password}"
        level_response = requests.get(level_url, timeout=30)
        level_data = level_response.json()
        
        if level_data.get('status') != 'started':
            conn.close()
            return jsonify({'error': 'Failed to start level up'}), 400
        
        now = datetime.now().isoformat()
        expires = (datetime.now() + timedelta(hours=4)).isoformat()
        instance_id = level_data.get('instance_id', 'unknown')
        
        c.execute("""INSERT INTO bot_sessions 
                     (username, user_uid, bot_id, bot_uid, bot_password, started_at, expires_at, is_active, instance_id) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)""", 
                  (username, user_uid, bot_id, bot_uid, bot_password, now, expires, instance_id))
        
        c.execute("UPDATE bot_usage_stats SET total_uses = total_uses + 1, last_used = ? WHERE bot_id = ?", (now, bot_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'✅ Level up started! Bot will auto-stop after 4 hours.',
            'instance_id': instance_id,
            'expires_at': expires
        })
        
    except Exception as e:
        conn.close()
        print(f"Start level up error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/levelup/stop', methods=['POST'])
def stop_level_up():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    session_id = data.get('session_id')
    username = session.get('username')
    
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
    
    conn = sqlite3.connect('naruto_tools.db')
    c = conn.cursor()
    
    session_data = c.execute("SELECT id, user_uid, bot_uid, bot_password, instance_id FROM bot_sessions WHERE id = ? AND username = ? AND is_active = 1", (session_id, username)).fetchone()
    
    if not session_data:
        conn.close()
        return jsonify({'error': 'No active session found'}), 400
    
    session_db_id, user_uid, bot_uid, bot_password, instance_id = session_data
    
    # Force stop - session ko inactive mark karo pehle
    c.execute("UPDATE bot_sessions SET is_active = 0 WHERE id = ?", (session_db_id,))
    conn.commit()
    
    # Update stats
    bot_id = c.execute("SELECT bot_id FROM bot_sessions WHERE id = ?", (session_db_id,)).fetchone()
    if bot_id:
        c.execute("UPDATE bot_usage_stats SET total_uses = total_uses - 1 WHERE bot_id = ?", (bot_id[0],))
        conn.commit()
    
    # Now try to stop instance and remove friend (errors ignored)
    try:
        if instance_id and instance_id != 'unknown':
            try:
                stop_url = f"{API_URLS['level_stop']}/{instance_id}"
                requests.get(stop_url, timeout=10)
            except Exception as e:
                print(f"Stop instance error (ignored): {e}")
        
        try:
            remove_url = f"{API_URLS['friend_remove']}?uid={bot_uid}&password={bot_password}&friend_uid={user_uid}"
            requests.get(remove_url, timeout=10)
        except Exception as e:
            print(f"Remove friend error (ignored): {e}")
            
    except Exception as e:
        print(f"Stop cleanup error (ignored): {e}")
    
    conn.close()
    return jsonify({'success': True, 'message': '✅ Bot stopped successfully!'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'bots': len(get_bots_list())})

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    init_db()
    start_bot_removal_thread()
    print(f"\n🔥 SUMAN TOOLS STARTED WITH {len(get_bots_list())} BOTS!")
    print("📍 Open http://127.0.0.1:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=True)