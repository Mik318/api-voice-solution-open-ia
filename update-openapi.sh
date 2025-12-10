#!/bin/bash

# Script para actualizar OpenAPI YAML desde la API desplegada

API_URL="https://api-voice-orisod.sistems-mik3.com"
OUTPUT_FILE="/home/mik318/Documentos/personal-proyects/front-ia-call/tools/ia-call-api/openapi.yaml"

echo "🔄 Descargando OpenAPI desde $API_URL..."

# Intentar descargar el OpenAPI en formato YAML
if curl -f -s "$API_URL/api/openapi.yaml" -o "$OUTPUT_FILE"; then
    echo "✅ OpenAPI YAML descargado exitosamente"
    echo "📄 Guardado en: $OUTPUT_FILE"
    
    # Verificar que no esté vacío
    if [ -s "$OUTPUT_FILE" ]; then
        echo "✅ Archivo válido ($(wc -l < "$OUTPUT_FILE") líneas)"
        
        # Verificar que no tenga operationId duplicados
        if grep -q "operationId.*handle_outgoing_call" "$OUTPUT_FILE"; then
            echo "✅ operationId correcto encontrado"
        else
            echo "⚠️  WARNING: operationId 'handle_outgoing_call' no encontrado"
        fi
    else
        echo "❌ ERROR: Archivo vacío"
        exit 1
    fi
else
    echo "❌ ERROR: No se pudo descargar el OpenAPI"
    echo "Verifica que la API esté corriendo en: $API_URL"
    exit 1
fi

echo ""
echo "🚀 Ahora puedes ejecutar:"
echo "   cd /home/mik318/Documentos/personal-proyects/front-ia-call"
echo "   npm run generate:auth-api"
