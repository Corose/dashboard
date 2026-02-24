from app import app, login_manager
from flask import render_template, redirect, request, url_for, send_file
from models import db, User, AuthUser
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from sqlalchemy import func
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import requests
import os
import io
import pandas as pd
from flask import flash

# =========================
# LOGIN MANAGER
# =========================
@login_manager.user_loader
def load_user(user_id):
    return AuthUser.query.get(int(user_id))


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    # 🔒 Si ya está autenticado, no puede volver al login
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = AuthUser.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            return redirect(url_for("loading"))

        return render_template(
            "login.html",
            error="ACCESS DENIED – INVALID CREDENTIALS"
        )

    return render_template("login.html")



# =========================
# CRAGANDO...
# =========================

@app.route("/loading")
@login_required
def loading():
    return render_template("loading.html")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# =========================
# DASHBOARD
# =========================
@app.route("/")
@login_required
def dashboard():

    users = User.query.all()
    total_users = len(users)

    activos = User.query.filter_by(activo=True).count()
    inactivos = User.query.filter_by(activo=False).count()

    equipos = db.session.query(
        User.equipo,
        func.count(User.id)
    ).group_by(User.equipo).all()

    return render_template(
        "dashboard.html",
        users=users,
        total_users=total_users,
        activos=activos,
        inactivos=inactivos,
        equipos=equipos
    )


# =========================
# CREAR USUARIO
# =========================
@app.route("/create", methods=["POST"])
@login_required
def create_user():

    accesos = ",".join(request.form.getlist("accesos"))

    new_user = User(
        nombre=request.form["nombre"],
        usuario=request.form["usuario"],
        correo=request.form["correo"],
        equipo=request.form["equipo"],
        jefe=request.form["jefe"],
        accesos=accesos,
        comentarios=request.form.get("comentarios", ""),
        activo=True
    )

    db.session.add(new_user)
    db.session.commit()

    # Notificación Teams si es invitado
    if current_user.role == "invitado":
        webhook = os.environ.get("TEAMS_WEBHOOK_URL")
        if webhook:
            requests.post(
                webhook,
                json={"text": f"Nuevo usuario agregado: {new_user.nombre}"}
            )

    return redirect(url_for("dashboard"))


# =========================
# ELIMINAR USUARIO
# =========================
@app.route("/delete_user/<int:id>", methods=["POST"])
def delete_user(id):
    user = User.query.get(id)
    if user:
        deleted_data = {
            "success": True,
            "nombre": user.nombre,
            "usuario": user.usuario
        }
        db.session.delete(user)
        db.session.commit()
        return deleted_data

    return {"success": False}, 404



# =========================
# EDITAR USUARIO
# =========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_user(id):

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    user = User.query.get_or_404(id)

    if request.method == "POST":

        user.nombre = request.form["nombre"]
        user.usuario = request.form["usuario"]
        user.correo = request.form["correo"]
        user.equipo = request.form["equipo"]
        user.jefe = request.form["jefe"]
        user.accesos = ",".join(request.form.getlist("accesos"))
        user.comentarios = request.form.get("comentarios", "")
        user.activo = True if request.form.get("activo") == "true" else False

        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("edit_user.html", user=user)


# =========================
# EXPORTAR EXCEL
# =========================
@app.route("/export-excel")
@login_required
def export_excel():

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    users = User.query.all()

    wb = Workbook()

    # -------------------------
    # HOJA 1 - LISTADO
    # -------------------------
    ws = wb.active
    ws.title = "Usuarios"

    headers = [
        "ID",
        "Nombre",
        "Usuario",
        "Correo",
        "Equipo",
        "Jefe",
        "Accesos",
        "Comentarios",
        "Fecha Creación"
    ]

    ws.append(headers)

    header_fill = PatternFill(
        start_color="1F4E78",
        end_color="1F4E78",
        fill_type="solid"
    )

    header_font = Font(color="FFFFFF", bold=True)

    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for user in users:
        ws.append([
            user.id,
            user.nombre,
            user.usuario,
            user.correo,
            user.equipo,
            user.jefe,
            user.accesos,
            user.comentarios,
            user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else ""
        ])

    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
        col_letter = get_column_letter(column_cells[0].column)
        ws.column_dimensions[col_letter].width = length + 2

    # -------------------------
    # HOJA 2 - ESTADÍSTICAS
    # -------------------------
    stats_ws = wb.create_sheet(title="Estadísticas")
    stats_ws.append(["Equipo", "Cantidad de Usuarios"])

    stats_ws["A1"].fill = header_fill
    stats_ws["A1"].font = header_font
    stats_ws["B1"].fill = header_fill
    stats_ws["B1"].font = header_font

    equipos = db.session.query(
        User.equipo,
        func.count(User.id)
    ).group_by(User.equipo).all()

    for equipo, cantidad in equipos:
        stats_ws.append([equipo, cantidad])

    for column_cells in stats_ws.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
        col_letter = get_column_letter(column_cells[0].column)
        stats_ws.column_dimensions[col_letter].width = length + 2

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Reporte_Usuarios_Corporativo.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
   # -------------------------
    # IMPORTAR EXCEL
    # -------------------------

@app.route("/import_excel", methods=["POST"])
@login_required
def import_excel():
    

    file = request.files.get("file")

    if not file:
        flash("No se seleccionó archivo")
        return redirect(url_for("dashboard"))

    try:
        df = pd.read_excel(file)

        # 🔥 OPCIONAL: limpiar tabla antes de importar
        User.query.delete()
        db.session.commit()

        for _, row in df.iterrows():

            new_user = User(
                nombre=row.get("Nombre", ""),
                usuario=row.get("Usuario", ""),
                correo=row.get("Correo", ""),
                equipo=row.get("Equipo", ""),
                jefe=row.get("Jefe", ""),
                accesos=row.get("Accesos", "")
            )

            db.session.add(new_user)

        db.session.commit()

        flash("Usuarios importados correctamente")

    except Exception as e:
        print(e)
        flash("Error al importar archivo")

    return redirect(url_for("dashboard"))

