from rut_chileno.utils.rut import valida_rut

def validate_employee_rut(doc, method):
    if not getattr(doc, "rut", None):
        return

    doc.rut = valida_rut(doc.rut)