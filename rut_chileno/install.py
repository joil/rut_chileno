# Copyright (c) 2026, Jose Pino and contributors
# For license information, please see license.txt

import frappe

from rut_chileno.custom_fields import migrate_legacy_rut_to_tax_id, setup_custom_fields
from rut_chileno.utils.rut import valida_rut
from rut_chileno.validations import RUT_FIELDS


def after_install():
	setup_rut_chileno_app()


def after_migrate():
	setup_rut_chileno_app()


def before_tests():
	setup_rut_chileno_app()


def setup_rut_chileno_app():
	migrate_legacy_rut_to_tax_id()
	setup_custom_fields()
	reformat_stored_ruts()


def reformat_stored_ruts():
	"""Normaliza RUT ya guardados al formato 12.345.678-5. No aborta si hay inválidos."""
	for doctype, fieldname in RUT_FIELDS.items():
		if not frappe.db.has_column(doctype, fieldname):
			continue

		rows = frappe.db.sql(
			f"""
			SELECT name, `{fieldname}`
			FROM `tab{doctype}`
			WHERE IFNULL(`{fieldname}`, '') != ''
			"""
		)
		for name, value in rows:
			formatted = valida_rut(value, throw=False)
			if formatted and formatted != value:
				frappe.db.set_value(doctype, name, fieldname, formatted, update_modified=False)
			elif not formatted:
				frappe.logger("rut_chileno").warning(
					"RUT inválido en %s %s (%s=%s); se dejó sin cambios.",
					doctype,
					name,
					fieldname,
					value,
				)
