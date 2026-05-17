#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analizar estructura del template Word"""

import xml.etree.ElementTree as ET
from zipfile import ZipFile
import os

docx_file = 'INFORME_MENSUAL_ACEROS AREQUIPA_ABRIL_2026.docx'

# Definir namespaces
ns = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
}

print("\n" + "="*80)
print("ANÁLISIS DETALLADO DEL TEMPLATE WORD")
print("="*80)

tree = ET.parse('template_extracted/word/document.xml')
root = tree.getroot()

body = root.find('w:body', ns)
if body is not None:
    elements = list(body)
    print(f"\n📊 TOTAL DE ELEMENTOS: {len(elements)}\n")

    print("ESTRUCTURA DEL DOCUMENTO:")
    print("-" * 80)

    for i, elem in enumerate(list(body)):
        tag_name = elem.tag.split('}')[1] if '}' in elem.tag else elem.tag

        if tag_name == 'p':
            # Párrafo
            text_content = ''.join(elem.itertext()).strip()
            if text_content:
                display_text = (text_content[:70] + '...') if len(text_content) > 70 else text_content
                print(f"{i:3d}: [P] {display_text}")
            else:
                print(f"{i:3d}: [P] (vacío)")

        elif tag_name == 'tbl':
            # Tabla
            rows = len(elem.findall('.//w:tr', ns))
            cols = len(elem.findall('.//w:tr[1]/w:tc', ns))
            print(f"{i:3d}: [T] TABLA - {rows} filas x {cols} columnas")

        elif tag_name == 'sectPr':
            print(f"{i:3d}: [S] SECTION PROPERTIES")

        else:
            print(f"{i:3d}: [{tag_name[:3].upper()}]")

print("\n" + "="*80)
print("ANÁLISIS DE TABLAS")
print("="*80)

tabla_num = 0
for elem in body.findall('.//w:tbl', ns):
    tabla_num += 1
    rows = elem.findall('.//w:tr', ns)
    cols = len(rows[0].findall('w:tc', ns)) if rows else 0
    print(f"\n📋 TABLA {tabla_num}:")
    print(f"   - Filas: {len(rows)}")
    print(f"   - Columnas: {cols}")

    # Mostrar primeras 2 filas
    for row_idx, row in enumerate(rows[:2]):
        cells = row.findall('w:tc', ns)
        row_text = []
        for cell in cells:
            cell_text = ''.join(cell.itertext()).strip()
            row_text.append(cell_text[:20] if cell_text else '')
        print(f"   - Fila {row_idx}: {row_text[:3]}")

print("\n" + "="*80)
print("IMÁGENES ENCONTRADAS")
print("="*80)

media_path = 'template_extracted/word/media'
if os.path.exists(media_path):
    images = os.listdir(media_path)
    print(f"📷 Total de imágenes: {len(images)}")
    for img in images[:5]:
        print(f"   - {img}")
    if len(images) > 5:
        print(f"   ... y {len(images) - 5} más")

print("\n" + "="*80)

