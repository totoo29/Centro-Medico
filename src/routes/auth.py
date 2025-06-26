from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Por favor, complete todos los campos', 'error')
            return render_template('auth/login.html')
        
        try:
            from src.models.usuario import Usuario
            from src.database import db
            
            usuario = Usuario.query.filter(
                db.or_(
                    Usuario.username == username,
                    Usuario.email == username
                ),
                Usuario.activo == True
            ).first()
            
            if usuario and usuario.check_password(password):
                usuario.ultimo_login = datetime.utcnow()
                db.session.commit()
                
                login_user(usuario, remember=remember)
                
                flash(f'¡Bienvenido, {usuario.nombre_completo}!', 'success')
                
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('main.index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        except Exception as e:
            flash('Error en el sistema de autenticación', 'error')
            print(f"Error de login: {e}")
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    try:
        nombre = current_user.nombre_completo
        logout_user()
        flash(f'Sesión cerrada. ¡Hasta luego, {nombre}!', 'info')
    except:
        logout_user()
        flash('Sesión cerrada', 'info')
    
    return redirect(url_for('auth.login'))