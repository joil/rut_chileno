# Copyright (c) 2026, Jose Pino and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

from rut_chileno.install import setup_rut_chileno_app
from rut_chileno.utils.rut import compact_rut, compute_dv, formatea_rut, valida_rut
from rut_chileno.validations import validate_party_rut


class TestRutChileno(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		setup_rut_chileno_app()

	def test_known_check_digits(self):
		self.assertEqual(compute_dv("11111111"), "1")
		self.assertEqual(compute_dv("12345678"), "5")
		self.assertEqual(compute_dv("1"), "9")

	def test_accepts_and_canonicalizes_formats(self):
		expected = "12.345.678-5"
		for value in ("12.345.678-5", "12345678-5", "123456785", " 12.345.678-5 ", "012345678-5"):
			self.assertEqual(valida_rut(value), expected)

		self.assertEqual(valida_rut("11.111.111-1"), "11.111.111-1")
		self.assertEqual(valida_rut("1-9"), "1-9")

	def test_compact_rut_strips_separators(self):
		self.assertEqual(compact_rut("12.345.678-5"), "123456785")
		self.assertEqual(compact_rut("12345678-k"), "12345678K")

	def test_formatea_rut_groups_thousands(self):
		self.assertEqual(formatea_rut("12345678", "5"), "12.345.678-5")
		self.assertEqual(formatea_rut("1234567", "K"), "1.234.567-K")
		self.assertEqual(formatea_rut("1", "9"), "1-9")

	def test_invalid_check_digit_uses_calculated_value(self):
		with self.assertRaises(frappe.ValidationError) as ctx:
			valida_rut("12.345.678-9")
		self.assertIn("5", str(ctx.exception))
		self.assertIn("9", str(ctx.exception))

	def test_empty_rut_is_rejected_when_throwing(self):
		self.assertRaises(frappe.ValidationError, valida_rut, "")
		self.assertIsNone(valida_rut("", throw=False))
		self.assertIsNone(valida_rut("12.345.678-9", throw=False))

	def test_employee_has_rut_custom_field(self):
		field = frappe.get_meta("Employee").get_field("rut")
		self.assertIsNotNone(field)
		self.assertEqual(field.fieldtype, "Data")
		self.assertEqual(field.label, "RUT")
		self.assertFalse(field.reqd)

	def test_tax_id_is_labelled_rut(self):
		for doctype in ("Customer", "Supplier", "Company"):
			field = frappe.get_meta(doctype).get_field("tax_id")
			self.assertIsNotNone(field)
			self.assertEqual(field.label, "RUT")

	def test_legacy_party_rut_custom_field_removed(self):
		for doctype in ("Customer", "Supplier", "Company"):
			self.assertFalse(frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "rut"}))
			self.assertIsNone(frappe.get_meta(doctype).get_field("rut"))

	def test_validate_formats_customer_tax_id(self):
		doc = frappe.new_doc("Customer")
		doc.tax_id = "123456785"
		validate_party_rut(doc)
		self.assertEqual(doc.tax_id, "12.345.678-5")

	def test_chile_company_requires_rut(self):
		doc = frappe.new_doc("Company")
		doc.country = "Chile"
		self.assertRaises(frappe.ValidationError, validate_party_rut, doc)

	def test_foreign_company_allows_empty_tax_id(self):
		doc = frappe.new_doc("Company")
		doc.country = "United States"
		validate_party_rut(doc)
		self.assertFalse(doc.tax_id)

	def test_duplicate_rut_is_rejected(self):
		name = "_Test RUT Duplicate Customer"
		existing = frappe.db.exists("Customer", {"customer_name": name})
		if existing:
			frappe.delete_doc("Customer", existing, force=True, ignore_permissions=True)

		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": name,
				"customer_type": "Company",
				"tax_id": "11.111.111-1",
			}
		)
		customer.insert(ignore_permissions=True)
		self.addCleanup(lambda: frappe.delete_doc("Customer", customer.name, force=True, ignore_permissions=True))

		dup = frappe.new_doc("Customer")
		dup.tax_id = "11111111-1"
		self.assertRaises(frappe.ValidationError, validate_party_rut, dup)
