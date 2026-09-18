# Copyright (c) 2026, Jose Pino and contributors
# For license information, please see license.txt

"""Validación y formato del RUT chileno (módulo 11)."""

import re

import frappe
from frappe import _

# Guiones ASCII, en, em y menos tipográfico.
_DASHES = ("-", "–", "—", "−")
_NON_RUT_CHARS = re.compile(r"[^0-9K]")


def compact_rut(value: str | None) -> str:
	"""Devuelve cuerpo + DV en mayúsculas, sin puntos, espacios ni guiones."""
	if value is None:
		return ""

	text = str(value).strip().upper()
	for dash in _DASHES:
		text = text.replace(dash, "")
	text = text.replace(".", "").replace(" ", "").replace("\t", "")
	return _NON_RUT_CHARS.sub("", text)


def compute_dv(cuerpo: str) -> str:
	"""Calcula el dígito verificador (módulo 11) del cuerpo numérico del RUT."""
	if not cuerpo or not str(cuerpo).isdigit():
		frappe.throw(_("El cuerpo del RUT debe ser numérico."))

	suma = 0
	multiplicador = 2
	for digito in reversed(str(cuerpo)):
		suma += int(digito) * multiplicador
		multiplicador = 2 if multiplicador == 7 else multiplicador + 1

	resto = 11 - (suma % 11)
	if resto == 11:
		return "0"
	if resto == 10:
		return "K"
	return str(resto)


def formatea_rut(cuerpo: str | None, dv: str | None = None) -> str:
	"""Formato canónico con puntos de miles y guión: 12.345.678-5."""
	if cuerpo is None or not str(cuerpo).strip():
		return ""

	if dv is None:
		parsed_cuerpo, parsed_dv = _split_rut(cuerpo)
		dv = parsed_dv
		cuerpo = parsed_cuerpo

	groups = []
	pending = str(cuerpo)
	while pending:
		groups.append(pending[-3:])
		pending = pending[:-3]
	cuerpo_fmt = ".".join(reversed(groups))
	return f"{cuerpo_fmt}-{str(dv).upper()}"


def valida_rut(rut: str | None, throw: bool = True) -> str | None:
	"""Valida el RUT y lo devuelve en formato canónico.

	Acepta 12.345.678-5, 12345678-5, 123456785 y variantes con espacios.
	"""
	if rut is None or not str(rut).strip():
		if throw:
			frappe.throw(_("El RUT no puede ser vacío."))
		return None

	try:
		cuerpo, dv = _split_rut(rut)
		dv_calc = compute_dv(cuerpo)
		if dv_calc != dv:
			frappe.throw(
				_("El RUT no es válido: se esperaba dígito verificador {0} y se obtuvo {1}.").format(
					dv_calc, dv
				)
			)
		return formatea_rut(cuerpo, dv_calc)
	except frappe.ValidationError:
		if throw:
			raise
		return None


@frappe.whitelist()
def normalize_rut(rut: str | None = None) -> str:
	"""Normaliza un RUT desde el cliente. Cadena vacía si no hay valor."""
	if rut is None or not str(rut).strip():
		return ""
	return valida_rut(rut) or ""


def _split_rut(value: str) -> tuple[str, str]:
	compact = compact_rut(value)
	if len(compact) < 2:
		frappe.throw(_("El RUT es demasiado corto."))

	dv = compact[-1]
	cuerpo = compact[:-1]
	if not cuerpo.isdigit():
		frappe.throw(_("El RUT contiene caracteres no válidos."))

	cuerpo = cuerpo.lstrip("0")
	if not cuerpo:
		frappe.throw(_("El RUT no es válido."))
	if len(cuerpo) > 8:
		frappe.throw(_("El cuerpo del RUT no puede tener más de 8 dígitos."))
	if dv not in "0123456789K":
		frappe.throw(_("El dígito verificador del RUT no es válido."))

	return cuerpo, dv
