# Copyright (c) 2026, Jose Pino and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields, delete_custom_fields
from frappe.custom.doctype.property_setter.property_setter import delete_property_setter, make_property_setter

MODULE = "Rut Chileno"

TAX_ID_DOCTYPES = ("Customer", "Supplier", "Company")
QUICK_ENTRY_DOCTYPES = ("Company", "Employee")
RUT_DESCRIPTION = "RUT chileno. Se acepta con o sin puntos y guión; se guarda como 12.345.678-5."

CHILE_MANDATORY = 'eval:doc.country=="Chile"'

TAX_ID_FIELD_PROPERTIES = {
	"label": ("RUT", "Data"),
	"description": (RUT_DESCRIPTION, "Small Text"),
	"reqd": ("0", "Check"),
	"allow_in_quick_entry": ("1", "Check"),
	"bold": ("1", "Check"),
	"in_list_view": ("1", "Check"),
}

# El asterisco del formulario solo aparece si el país del registro es Chile.
TAX_ID_MANDATORY_DEPENDS_ON = {
	"Supplier": CHILE_MANDATORY,
	"Company": CHILE_MANDATORY,
}

# Mueve tax_id a la primera pestaña (Detalles), justo después del nombre.
TAX_ID_INSERT_AFTER = {
	"Customer": "customer_name",
	"Supplier": "supplier_name",
	"Company": "company_name",
}


def get_custom_fields() -> dict[str, list[dict]]:
	return {
		"Employee": [
			{
				"fieldname": "rut",
				"label": "RUT",
				"fieldtype": "Data",
				"insert_after": "last_name",
				"reqd": 0,
				"unique": 0,
				"bold": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"allow_in_quick_entry": 1,
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
	setup_quick_entry()
	move_tax_id_to_details_tab()


def setup_tax_id_property_setters():
	for doctype in TAX_ID_DOCTYPES:
		for prop, (value, property_type) in TAX_ID_FIELD_PROPERTIES.items():
			_upsert_property_setter(doctype, "tax_id", prop, value, property_type)
		depends = TAX_ID_MANDATORY_DEPENDS_ON.get(doctype, "")
		_upsert_property_setter(doctype, "tax_id", "mandatory_depends_on", depends, "Data")


def setup_quick_entry():
	for doctype in QUICK_ENTRY_DOCTYPES:
		_upsert_doctype_property_setter(doctype, "quick_entry", "1", "Check")


def move_tax_id_to_details_tab():
	for doctype, insert_after in TAX_ID_INSERT_AFTER.items():
		_move_field_after(doctype, "tax_id", insert_after)


def remove_custom_fields():
	delete_custom_fields({"Employee": ["rut"]})
	remove_legacy_party_rut_fields()
	for doctype in TAX_ID_DOCTYPES:
		for prop in (*TAX_ID_FIELD_PROPERTIES, "mandatory_depends_on"):
			delete_property_setter(doctype, prop, "tax_id")
		delete_property_setter(doctype, "field_order")
	for doctype in QUICK_ENTRY_DOCTYPES:
		delete_property_setter(doctype, "quick_entry")


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


def _move_field_after(doctype: str, fieldname: str, insert_after: str):
	order = [df.fieldname for df in frappe.get_meta(doctype).fields]
	if fieldname not in order or insert_after not in order:
		return

	order.remove(fieldname)
	order.insert(order.index(insert_after) + 1, fieldname)
	_upsert_doctype_property_setter(doctype, "field_order", json.dumps(order), "Small Text")
	frappe.clear_cache(doctype=doctype)


def _upsert_doctype_property_setter(doctype: str, prop: str, value: str, property_type: str):
	existing = frappe.db.exists(
		"Property Setter",
		{"doc_type": doctype, "doctype_or_field": "DocType", "property": prop},
	)
	if existing:
		ps = frappe.get_doc("Property Setter", existing)
		if ps.value != value or ps.property_type != property_type:
			ps.value = value
			ps.property_type = property_type
			ps.is_system_generated = 1
			ps.save(ignore_permissions=True)
		return

	make_property_setter(doctype, None, prop, value, property_type, for_doctype=True)


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
