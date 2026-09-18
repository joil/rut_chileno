# Copyright (c) 2026, Jose Pino and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields, delete_custom_fields
from frappe.custom.doctype.property_setter.property_setter import delete_property_setter, make_property_setter

MODULE = "Rut Chileno"

TAX_ID_DOCTYPES = ("Customer", "Supplier", "Company")
RUT_DESCRIPTION = "RUT chileno. Se acepta con o sin puntos y guión; se guarda como 12.345.678-5."


def get_custom_fields() -> dict[str, list[dict]]:
	return {
		"Employee": [
			{
				"fieldname": "rut",
				"label": "RUT",
				"fieldtype": "Data",
				"insert_after": "employee_name",
				"reqd": 0,
				"unique": 0,
				"bold": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"translatable": 0,
				"is_system_generated": 1,
				"module": MODULE,
				"description": RUT_DESCRIPTION,
			}
		]
	}


def setup_custom_fields():
	create_custom_fields(get_custom_fields(), ignore_validate=True, update=True)
	setup_tax_id_property_setters()


def setup_tax_id_property_setters():
	for doctype in TAX_ID_DOCTYPES:
		_upsert_property_setter(doctype, "tax_id", "label", "RUT", "Data")
		_upsert_property_setter(doctype, "tax_id", "description", RUT_DESCRIPTION, "Small Text")


def remove_custom_fields():
	delete_custom_fields({"Employee": ["rut"]})
	remove_legacy_party_rut_fields()
	for doctype in TAX_ID_DOCTYPES:
		delete_property_setter(doctype, "label", "tax_id")
		delete_property_setter(doctype, "description", "tax_id")


def remove_legacy_party_rut_fields():
	delete_custom_fields({doctype: ["rut"] for doctype in TAX_ID_DOCTYPES})


def migrate_legacy_rut_to_tax_id():
	"""Copia el custom field `rut` a `tax_id` nativo antes de eliminarlo."""
	for doctype in TAX_ID_DOCTYPES:
		if not frappe.db.has_column(doctype, "rut") or not frappe.db.has_column(doctype, "tax_id"):
			continue
		frappe.db.sql(
			f"""
			UPDATE `tab{doctype}`
			SET tax_id = rut
			WHERE IFNULL(TRIM(tax_id), '') = ''
			AND IFNULL(TRIM(rut), '') != ''
			"""
		)
	remove_legacy_party_rut_fields()


def create_rut_field():
	"""Compatibilidad con el hook/execute anterior."""
	setup_custom_fields()


def _upsert_property_setter(doctype: str, fieldname: str, prop: str, value: str, property_type: str):
	existing = frappe.db.exists(
		"Property Setter",
		{"doc_type": doctype, "field_name": fieldname, "property": prop},
	)
	if existing:
		ps = frappe.get_doc("Property Setter", existing)
		if ps.value != value or ps.property_type != property_type:
			ps.value = value
			ps.property_type = property_type
			ps.is_system_generated = 1
			ps.save(ignore_permissions=True)
		return

	make_property_setter(doctype, fieldname, prop, value, property_type)
