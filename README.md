# Rut Chileno

RUT chileno (Rol Único Tributario) para ERPNext v16: valida el formato y el dígito verificador (módulo 11) y lo guarda de forma canónica.

Requiere **ERPNext**. Compatible con Frappe/ERPNext version-16.

## Qué hace

| DocType | Campo | Comportamiento |
| --- | --- | --- |
| Customer | `tax_id` (nativo, etiqueta **RUT**) | Primera pestaña y creación rápida. Obligatorio si la dirección o la compañía por defecto es Chile |
| Supplier | `tax_id` (nativo, etiqueta **RUT**) | Primera pestaña y creación rápida. Obligatorio si el país es Chile |
| Company | `tax_id` (nativo, etiqueta **RUT**) | Primera pestaña y creación rápida. Obligatorio si el país es Chile |
| Employee | Custom Field `rut` | Primera pestaña (Overview) y creación rápida. Obligatorio si la compañía del empleado es de Chile |

En Cliente, Proveedor y Compañía **no se crea un segundo campo RUT**: ERPNext ya tiene `tax_id`, que usan reportes, impresión y otras apps. Si existía un Custom Field `rut` de una versión anterior, su valor se copia a `tax_id` (si este estaba vacío) y el campo extra se elimina.

## Formato

Se aceptan estas entradas:

- `12.345.678-5`
- `12345678-5`
- `123456785`
- con espacios o ceros a la izquierda

Se guarda siempre como **`12.345.678-5`** (puntos de miles, guión y `K` mayúscula).

El dígito verificador se calcula con el algoritmo módulo 11 del SII. Un RUT con DV incorrecto se rechaza y el mensaje indica el dígito esperado.

El RUT es **obligatorio solo para Chile** (país de la compañía, del proveedor, de la dirección del cliente o de la compañía del empleado). En terceros extranjeros puede quedar vacío. Si tiene valor, **debe ser un RUT chileno válido**.

## Instalación

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench --site $SITE install-app rut_chileno
```

Al instalar (y en cada `bench migrate`) la app:

1. Crea o actualiza el campo **RUT** en Employee (primera pestaña, creación rápida; obligatorio si la compañía es de Chile).
2. Relabela `tax_id` como **RUT**, lo mueve a Detalles y lo incluye en creación rápida. Es obligatorio solo si el país es Chile.
3. Migra datos del Custom Field `rut` antiguo hacia `tax_id`.
4. Reformatea RUT ya guardados al formato canónico (los inválidos se dejan y se registran en el log).

Para desinstalar:

```bash
bench --site $SITE uninstall-app rut_chileno
```

Se elimina el Custom Field de Employee y los Property Setter de `tax_id`. Los valores de `tax_id` no se borran.

## Impresión (Jinja)

En formatos de impresión:

```jinja
{{ doc.tax_id }}
{{ doc.tax_id | formatea_rut }}
```

## Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/rut_chileno
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

## License

mit
