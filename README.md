

# Sistema de Gestión de Inventarios

Este es un proyecto en Python que proporciona una interfaz gráfica para gestionar inventarios de productos. Permite agregar, editar, eliminar y visualizar productos almacenados en una base de datos SQLite de manera sencilla.

## Características principales

- Interfaz gráfica amigable con Tkinter.
- Registro de productos con campos: ID, nombre, descripción, cantidad, precio unitario, almacén y fecha de última actualización.
- Manejo de IDs normalizados para evitar problemas con ceros a la izquierda (p. ej. "06" leído como "6").
- Funciones para buscar, filtrar y ordenar productos en la tabla.
- Edición y eliminación directa desde la tabla con doble clic.
- Exportación de inventario a archivo CSV.
- Validaciones de entrada para evitar datos inválidos.

## Requisitos

- Python 3.x
- Biblioteca Tkinter (normalmente incluida en Python)
- Biblioteca Pillow para manejo de imágenes (logo)
- SQLite (normalmente incluida en Python)

## Instalación y ejecución

1. Clonar o descargar el repositorio.
2. Instalar Pillow si no está instalado:
   ```
   pip install Pillow
   ```
3. Ejecutar el archivo principal:
   ```
   python grafic.py
   ```
4. La aplicación abrirá una ventana con el gestor de inventarios.

## Estructura del proyecto

- `product.py`: Clase Product para representar productos.
- `database.py`: Clase InventoryDatabase para gestión de la base de datos SQLite.
- `grafic.py`: Interfaz gráfica desarrollada con Tkinter para interactuar con el inventario.
- `app.py`: Archivo simple para pruebas o carga inicial de productos.

## Uso básico

- Para agregar un producto, use el botón "Agregar Producto" y complete el formulario.
- Para editar o eliminar, haga doble clic en el ícono correspondiente en la tabla.
- Use el campo de búsqueda para filtrar productos por cualquier campo.
- Exportar inventario a CSV con el botón "Exportar CSV".

