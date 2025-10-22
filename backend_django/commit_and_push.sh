#!/bin/bash
# Script para hacer commit y push de los cambios

echo "Agregando cambios..."
git add .

echo "Haciendo commit..."
git commit -m "Fix syntax error in diagnostic_views.py - Move cursor operations inside with block"

echo "Haciendo push..."
git push

echo "Completado!"
