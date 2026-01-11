import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_rut_field():
    """
    Crea (o actualiza) un campo 'rut' en el Doctype 'Employee'.

    Para ejecutarlo:
        bench --site [site_name] execute chile_custom.scripts.employee_rut_custom_fields.create_employee_rut_field
    """
    # Employee
    field_definition_employee = {
        "doctype": "Custom Field",
        "dt": "Employee",                  # Target DocType (e.g., "Customer", "Sales Order")
        "fieldname": "rut", # Field name (must start with 'custom_')
        "label": "RUT",       # Field label
        "fieldtype": "Data",           # Field type (e.g., "Int", "Check", "Link", "Select")
        "insert_after": "employee_name",   # Existing field to insert after
        "reqd": 1,  #0: no requerido, 1: requerido
        "unique": 1,
        "bold": 1,
        "translatable": 0,
        "options": "",                 # Options (if applicable, e.g., for Link or Select)
        "hidden": 0,                   # Set to 1 to hide the field
        "description": "RUT chileno del empleado. Ejemplo: 12345678-9",
    }
    
    #Verificar si ya existe
    existing_employee = frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": "rut"})
    if existing_employee:
        # Si existe, actualizar
        cf = frappe.get_doc("Custom Field", existing_employee)
        cf.update(field_definition_employee)
        cf.save()
        frappe.msgprint("El campo 'rut' actualizado exitosamente")
    else:
        # Crear el campo
#        create_custom_fields("Employee", field, ignore_validate=False)
#        frappe.db.commit()
#        frappe.msgprint("Campo 'rut' creado exitosamente")
        try:
            # Create and insert the Custom Field document
            custom_field_doc = frappe.get_doc(field_definition_employee)
            custom_field_doc.insert()
            frappe.db.commit() # Commit the changes
            frappe.msgprint(f"Custom field {field_definition_employee['fieldname']} created successfully.")
        except Exception as e:
            frappe.msgprint(f"Failed to create custom field: {e}")

    frappe.clear_cache(doctype="Employee")

    # Customer
    field_definition_customer = {
        "doctype": "Custom Field",
        "dt": "Customer",                  # Target DocType (e.g., "Customer", "Sales Order")
        "fieldname": "rut", # Field name (must start with 'custom_')
        "label": "RUT",       # Field label
        "fieldtype": "Data",           # Field type (e.g., "Int", "Check", "Link", "Select")
        "insert_after": "customer_name",   # Existing field to insert after
        "reqd": 1,  #0: no requerido, 1: requerido
        "unique": 1,
        "bold": 1,
        "translatable": 0,
        "options": "",                 # Options (if applicable, e.g., for Link or Select)
        "hidden": 0,                   # Set to 1 to hide the field
        "description": "RUT chileno del cliente. Ejemplo: 12345678-9",
    }
    
    #Verificar si ya existe
    existing_customer = frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": "rut"})
    if existing_customer:
        # Si existe, actualizar
        cf = frappe.get_doc("Custom Field", existing_customer)
        cf.update(field_definition_customer)
        cf.save()
        frappe.msgprint("El campo 'rut' actualizado exitosamente")
    else:
        try:
            # Create and insert the Custom Field document
            custom_field_doc = frappe.get_doc(field_definition_customer)
            custom_field_doc.insert()
            frappe.db.commit() # Commit the changes
            frappe.msgprint(f"Custom field {field_definition_customer['fieldname']} created successfully.")
        except Exception as e:
            frappe.msgprint(f"Failed to create custom field: {e}")

    frappe.clear_cache(doctype="Customer")

    # Supplier
    field_definition_supplier = {
        "doctype": "Custom Field",
        "dt": "Supplier",                  # Target DocType (e.g., "Customer", "Sales Order")
        "fieldname": "rut", # Field name (must start with 'custom_')
        "label": "RUT",       # Field label
        "fieldtype": "Data",           # Field type (e.g., "Int", "Check", "Link", "Select")
        "insert_after": "supplier_name",   # Existing field to insert after
        "reqd": 1,  #0: no requerido, 1: requerido
        "unique": 1,
        "bold": 1,
        "translatable": 0,
        "options": "",                 # Options (if applicable, e.g., for Link or Select)
        "hidden": 0,                   # Set to 1 to hide the field
        "description": "RUT chileno del proveedor. Ejemplo: 12345678-9",
    }
    
    #Verificar si ya existe
    existing_supplier = frappe.db.exists("Custom Field", {"dt": "Supplier", "fieldname": "rut"})
    if existing_supplier:
        # Si existe, actualizar
        cf = frappe.get_doc("Custom Field", existing_supplier)
        cf.update(field_definition_supplier)
        cf.save()
        frappe.msgprint("El campo 'rut' actualizado exitosamente")
    else:
        try:
            # Create and insert the Custom Field document
            custom_field_doc = frappe.get_doc(field_definition_supplier)
            custom_field_doc.insert()
            frappe.db.commit() # Commit the changes
            frappe.msgprint(f"Custom field {field_definition_supplier['fieldname']} created successfully.")
        except Exception as e:
            frappe.msgprint(f"Failed to create custom field: {e}")

    frappe.clear_cache(doctype="Supplier")

    # Company
    field_definition_company = {
        "doctype": "Custom Field",
        "dt": "Company",                  # Target DocType (e.g., "Customer", "Sales Order")
        "fieldname": "rut", # Field name (must start with 'custom_')
        "label": "RUT",       # Field label
        "fieldtype": "Data",           # Field type (e.g., "Int", "Check", "Link", "Select")
        "insert_after": "company_name",   # Existing field to insert after
        "reqd": 1,  #0: no requerido, 1: requerido
        "unique": 1,
        "bold": 1,
        "translatable": 0,
        "options": "",                 # Options (if applicable, e.g., for Link or Select)
        "hidden": 0,                   # Set to 1 to hide the field
        "description": "RUT chileno de la empresa. Ejemplo: 12345678-9",
    }
    
    #Verificar si ya existe
    existing_company = frappe.db.exists("Custom Field", {"dt": "Company", "fieldname": "rut"})
    if existing_company:
        # Si existe, actualizar
        cf = frappe.get_doc("Custom Field", existing_company)
        cf.update(field_definition_company)
        cf.save()
        frappe.msgprint("El campo 'rut' actualizado exitosamente")
    else:
        try:
            # Create and insert the Custom Field document
            custom_field_doc = frappe.get_doc(field_definition_company)
            custom_field_doc.insert()
            frappe.db.commit() # Commit the changes
            frappe.msgprint(f"Custom field {field_definition_company['fieldname']} created successfully.")
        except Exception as e:
            frappe.msgprint(f"Failed to create custom field: {e}")

    frappe.clear_cache(doctype="Company")