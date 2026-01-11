import frappe

def valida_rut(rut: str):
    if not rut:
        frappe.throw("El RUT no puede ser vacío")

    # Normalizar
    rut = rut.replace(".", "").replace(" ", "").upper()

    if "-" not in rut and len(rut) > 1:
        frappe.throw("El RUT debe tener un guión")

    cuerpo, dv = rut.split("-")

    if not cuerpo.isdigit():
        frappe.throw("El RUT contiene caracteres no válidos")

    # Calcular el dígito verificador
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    dv_calc = 11 - (suma % 11)
    dv_calc = "0" if dv_calc == 11 else "K" if dv_calc == 10 else str(dv_calc)

    if dv_calc != dv:
        frappe.throw("El RUT no es válido, se esperaba {dv_calc} y se obtuvo {dv}")

    return f"{cuerpo}-{dv_calc}"