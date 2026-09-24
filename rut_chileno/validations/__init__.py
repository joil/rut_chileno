# Copyright (c) 2026, Jose Pino and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from rut_chileno.utils.rut import compact_rut, valida_rut

CHILE_COUNTRY_CODES = {"CL", "CHL"}
CHILE_COUNTRY_NAMES = {"chile"}

RUT_FIELDS = {
	"Customer": "tax_id",
	"Supplier": "tax_id",
	"Company": "tax_id",
	"Employee": "rut",
}


def is_chile_country(country: str | None) -> bool:
	if not country:
		return False

	if str(country).strip().lower() in CHILE_COUNTRY_NAMES:
		return True

	if str(country).strip().upper() in CHILE_COUNTRY_CODES:
		return True

	code = frappe.db.get_value("Country", country, "code")
	return bool(code) and str(code).upper() in CHILE_COUNTRY_CODES


def company_is_chile(company: str | None) -> bool:
	if not company:
		return False
	return is_chile_country(frappe.db.get_value("Company", company, "country"))


def validate_party_rut(doc, method=None):
	fieldname = RUT_FIELDS.get(doc.doctype)
	if not fieldname:
		return

	value = (getattr(doc, fieldname, None) or "").strip()
	if not value:
		if _rut_is_required(doc):
			frappe.throw(_("El RUT es obligatorio para registros de Chile."))
		return

	formatted = valida_rut(value)
	setattr(doc, fieldname, formatted)
	_assert_unique_rut(doc, fieldname, formatted)


def _rut_is_required(doc) -> bool:
	if doc.doctype == "Company":
		return is_chile_country(getattr(doc, "country", None))
	if doc.doctype == "Supplier":
		return is_chile_country(getattr(doc, "country", None))
	if doc.doctype == "Employee":
		return company_is_chile(getattr(doc, "company", None))
	if doc.doctype == "Customer":
		return _customer_is_chile(doc)
	return False


def _customer_is_chile(doc) -> bool:
	address = getattr(doc, "customer_primary_address", None)
	if address:
		country = frappe.db.get_value("Address", address, "country")
		if country:
			return is_chile_country(country)

	company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)
	return company_is_chile(company)


def _assert_unique_rut(doc, fieldname: str, formatted: str):
	if not frappe.db.has_column(doc.doctype, fieldname):
		return

	compact = compact_rut(formatted)
	existing = frappe.db.sql(
		f"""
		SELECT name FROM `tab{doc.doctype}`
		WHERE name != %s
		AND IFNULL({fieldname}, '') != ''
		AND REPLACE(REPLACE(REPLACE(UPPER({fieldname}), '.', ''), '-', ''), ' ', '') = %s
		LIMIT 1
		""",
		(doc.name or "", compact),
	)
	if existing:
		frappe.throw(
			_("El RUT {0} ya está registrado en {1} {2}.").format(formatted, _(doc.doctype), existing[0][0])
		)
