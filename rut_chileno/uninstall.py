# Copyright (c) 2026, Jose Pino and contributors
# For license information, please see license.txt

from rut_chileno.custom_fields import remove_custom_fields


def before_uninstall():
	remove_custom_fields()
