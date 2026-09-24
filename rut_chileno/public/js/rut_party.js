// Copyright (c) 2026, Jose Pino and contributors
// For license information, please see license.txt

const RUT_FIELD_BY_DOCTYPE = {
	Customer: "tax_id",
	Supplier: "tax_id",
	Company: "tax_id",
	Employee: "rut",
};

function compact_rut(value) {
	if (!value) {
		return "";
	}
	return String(value)
		.toUpperCase()
		.replace(/[.\s–—−-]/g, "")
		.replace(/[^0-9K]/g, "");
}

function compute_dv(cuerpo) {
	let suma = 0;
	let multiplicador = 2;
	for (let i = cuerpo.length - 1; i >= 0; i--) {
		suma += parseInt(cuerpo[i], 10) * multiplicador;
		multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
	}
	const resto = 11 - (suma % 11);
	if (resto === 11) {
		return "0";
	}
	if (resto === 10) {
		return "K";
	}
	return String(resto);
}

function formatea_rut(cuerpo, dv) {
	const groups = [];
	let pending = cuerpo;
	while (pending) {
		groups.push(pending.slice(-3));
		pending = pending.slice(0, -3);
	}
	return `${groups.reverse().join(".")}-${dv}`;
}

function try_formatea_rut(value) {
	const compact = compact_rut(value);
	if (compact.length < 2) {
		return value;
	}
	let cuerpo = compact.slice(0, -1).replace(/^0+/, "");
	const dv = compact.slice(-1);
	if (!cuerpo || !/^\d{1,8}$/.test(cuerpo) || !/^[0-9K]$/.test(dv)) {
		return value;
	}
	if (compute_dv(cuerpo) !== dv) {
		return value;
	}
	return formatea_rut(cuerpo, dv);
}

function apply_rut_format(frm) {
	const fieldname = RUT_FIELD_BY_DOCTYPE[frm.doctype];
	if (!fieldname || !frm.doc[fieldname]) {
		return;
	}
	const formatted = try_formatea_rut(frm.doc[fieldname]);
	if (formatted && formatted !== frm.doc[fieldname]) {
		frm.set_value(fieldname, formatted);
	}
}

function is_chile_country(country) {
	if (!country) {
		return false;
	}
	const value = String(country).trim().toLowerCase();
	return value === "chile" || value === "cl" || value === "chl";
}

function toggle_rut_required(frm, country) {
	const fieldname = RUT_FIELD_BY_DOCTYPE[frm.doctype];
	if (!fieldname || !frm.fields_dict[fieldname]) {
		return;
	}
	frm.toggle_reqd(fieldname, is_chile_country(country));
}

function apply_rut_required(frm) {
	if (frm.doctype === "Company" || frm.doctype === "Supplier") {
		toggle_rut_required(frm, frm.doc.country);
		return;
	}
	if (frm.doctype === "Employee" && frm.doc.company) {
		frappe.db.get_value("Company", frm.doc.company, "country", (r) => {
			toggle_rut_required(frm, r && r.country);
		});
		return;
	}
	if (frm.doctype === "Customer") {
		if (frm.doc.customer_primary_address) {
			frappe.db.get_value("Address", frm.doc.customer_primary_address, "country", (r) => {
				toggle_rut_required(frm, r && r.country);
			});
			return;
		}
		const company = frappe.defaults.get_user_default("Company");
		if (company) {
			frappe.db.get_value("Company", company, "country", (r) => {
				toggle_rut_required(frm, r && r.country);
			});
			return;
		}
	}
	toggle_rut_required(frm, null);
}

["Customer", "Supplier", "Company", "Employee"].forEach((doctype) => {
	const fieldname = RUT_FIELD_BY_DOCTYPE[doctype];
	frappe.ui.form.on(doctype, {
		[fieldname]: apply_rut_format,
		country: apply_rut_required,
		company: apply_rut_required,
		customer_primary_address: apply_rut_required,
		refresh(frm) {
			if (frm.fields_dict[fieldname]) {
				frm.set_df_property(fieldname, "description", __("RUT chileno. Ejemplo: 12.345.678-5"));
			}
			apply_rut_required(frm);
		},
	});
});
