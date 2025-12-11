# Ejemplos de Uso - API de Conversaciones

## 📞 Consultar Conversaciones Guardadas

### 1. Listar Todas las Llamadas

```bash
curl -X GET "http://localhost:8000/api/calls" \
  -H "Content-Type: application/json"
```

**Respuesta:**

```json
{
  "calls": [
    {
      "id": 1,
      "call_sid": "CA1234567890abcdef",
      "user_phone": "+1234567890",
      "start_time": "2025-12-10T21:00:00",
      "status": "completed",
      "duration": 120,
      "interaction_log": [
        {
          "user": "Hola, qué productos tienes.",
          "ai": "Ofrezco ORISOD Enzyme®, un complejo bioactivo fermentado...",
          "timestamp": 1764311500.7389648
        },
        {
          "user": "Es antioxidante.",
          "ai": "Sí, ORISOD Enzyme® es un antioxidante profundo...",
          "timestamp": 1764311558.8930223
        }
      ]
    }
  ],
  "total": 1
}
```

### 2. Obtener una Llamada Específica

```bash
curl -X GET "http://localhost:8000/api/calls/1" \
  -H "Content-Type: application/json"
```

### 3. Buscar Llamadas por Número de Teléfono

```bash
curl -X GET "http://localhost:8000/api/calls/search?phone=%2B1234567890" \
  -H "Content-Type: application/json"
```

## 🔍 Analizar Conversaciones

### Ejemplo en Python

```python
import requests
import json

# Obtener todas las llamadas
response = requests.get("http://localhost:8000/api/calls")
data = response.json()

# Analizar cada conversación
for call in data["calls"]:
    print(f"\n📞 Llamada {call['call_sid']}")
    print(f"   Teléfono: {call['user_phone']}")
    print(f"   Duración: {call['duration']}s")
    print(f"   Interacciones: {len(call['interaction_log'])}")

    # Mostrar cada interacción
    for i, interaction in enumerate(call['interaction_log'], 1):
        print(f"\n   --- Interacción #{i} ---")
        print(f"   👤 Usuario: {interaction['user']}")
        print(f"   🤖 IA: {interaction['ai'][:50]}...")  # Primeros 50 caracteres
```

### Ejemplo en JavaScript

```javascript
// Obtener todas las llamadas
fetch("http://localhost:8000/api/calls")
  .then((response) => response.json())
  .then((data) => {
    data.calls.forEach((call) => {
      console.log(`📞 Llamada ${call.call_sid}`);
      console.log(`   Interacciones: ${call.interaction_log.length}`);

      // Mostrar conversación
      call.interaction_log.forEach((interaction, i) => {
        console.log(`\n   Interacción #${i + 1}`);
        console.log(`   👤 ${interaction.user}`);
        console.log(`   🤖 ${interaction.ai}`);
      });
    });
  });
```

## 📊 Estadísticas de Conversaciones

### Script de Análisis

```python
import requests
from collections import Counter
from datetime import datetime

def analyze_conversations():
    """Analiza las conversaciones guardadas."""

    # Obtener todas las llamadas
    response = requests.get("http://localhost:8000/api/calls")
    calls = response.json()["calls"]

    # Estadísticas generales
    total_calls = len(calls)
    total_interactions = sum(len(call["interaction_log"]) for call in calls)
    avg_interactions = total_interactions / total_calls if total_calls > 0 else 0

    print(f"📊 Estadísticas Generales")
    print(f"   Total de llamadas: {total_calls}")
    print(f"   Total de interacciones: {total_interactions}")
    print(f"   Promedio de interacciones por llamada: {avg_interactions:.2f}")

    # Palabras más comunes en preguntas de usuarios
    user_words = []
    for call in calls:
        for interaction in call["interaction_log"]:
            words = interaction["user"].lower().split()
            user_words.extend(words)

    common_words = Counter(user_words).most_common(10)
    print(f"\n🔤 Palabras más comunes en preguntas:")
    for word, count in common_words:
        print(f"   {word}: {count}")

    # Duración promedio de llamadas
    durations = [call["duration"] for call in calls if call["duration"]]
    avg_duration = sum(durations) / len(durations) if durations else 0

    print(f"\n⏱️  Duración promedio de llamadas: {avg_duration:.2f}s")

if __name__ == "__main__":
    analyze_conversations()
```

## 🧪 Pruebas de Integración

### Test Completo de Flujo

```python
import requests
import time

def test_complete_flow():
    """Prueba el flujo completo de una llamada."""

    base_url = "http://localhost:8000"

    # 1. Iniciar una llamada
    print("📞 Iniciando llamada...")
    response = requests.post(
        f"{base_url}/make-call",
        json={"to_phone_number": "+1234567890"}
    )
    call_data = response.json()
    call_sid = call_data["call_sid"]
    print(f"   ✅ Llamada iniciada: {call_sid}")

    # 2. Esperar a que termine la llamada (en producción)
    print("\n⏳ Esperando a que termine la llamada...")
    time.sleep(5)  # Simular espera

    # 3. Buscar la llamada en la BD
    print("\n🔍 Buscando llamada en la base de datos...")
    response = requests.get(f"{base_url}/api/calls")
    calls = response.json()["calls"]

    # Encontrar nuestra llamada
    our_call = next((c for c in calls if c["call_sid"] == call_sid), None)

    if our_call:
        print(f"   ✅ Llamada encontrada!")
        print(f"   Interacciones guardadas: {len(our_call['interaction_log'])}")

        # Verificar formato
        for i, interaction in enumerate(our_call['interaction_log'], 1):
            assert "user" in interaction, f"Falta campo 'user' en interacción {i}"
            assert "ai" in interaction, f"Falta campo 'ai' en interacción {i}"
            assert "timestamp" in interaction, f"Falta campo 'timestamp' en interacción {i}"

        print("   ✅ Todas las interacciones tienen el formato correcto!")
    else:
        print("   ❌ No se encontró la llamada")

if __name__ == "__main__":
    test_complete_flow()
```

## 📈 Exportar Conversaciones

### Exportar a CSV

```python
import requests
import csv
from datetime import datetime

def export_to_csv(filename="conversations.csv"):
    """Exporta todas las conversaciones a CSV."""

    response = requests.get("http://localhost:8000/api/calls")
    calls = response.json()["calls"]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Call SID', 'Phone', 'Start Time', 'Duration',
            'Interaction #', 'User Message', 'AI Response', 'Timestamp'
        ])

        for call in calls:
            for i, interaction in enumerate(call['interaction_log'], 1):
                writer.writerow([
                    call['call_sid'],
                    call['user_phone'],
                    call['start_time'],
                    call['duration'],
                    i,
                    interaction['user'],
                    interaction['ai'],
                    datetime.fromtimestamp(interaction['timestamp']).isoformat()
                ])

    print(f"✅ Conversaciones exportadas a {filename}")

if __name__ == "__main__":
    export_to_csv()
```

### Exportar a JSON

```python
import requests
import json

def export_to_json(filename="conversations.json"):
    """Exporta todas las conversaciones a JSON."""

    response = requests.get("http://localhost:8000/api/calls")
    data = response.json()

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Conversaciones exportadas a {filename}")

if __name__ == "__main__":
    export_to_json()
```

## 🔧 Utilidades

### Limpiar Conversaciones de Prueba

```python
import requests

def clean_test_calls():
    """Elimina llamadas de prueba."""

    response = requests.get("http://localhost:8000/api/calls")
    calls = response.json()["calls"]

    for call in calls:
        if call['call_sid'].startswith('TEST_'):
            print(f"🗑️  Eliminando llamada de prueba: {call['call_sid']}")
            requests.delete(f"http://localhost:8000/api/calls/{call['id']}")

    print("✅ Llamadas de prueba eliminadas")

if __name__ == "__main__":
    clean_test_calls()
```

---

## 📚 Recursos Adicionales

- **Documentación de la API**: `http://localhost:8000/docs` (Swagger UI)
- **OpenAPI YAML**: `http://localhost:8000/openapi.yaml`
- **Esquemas Pydantic**: Ver archivo `schemas.py`

## 🆘 Solución de Problemas

### Problema: No se guardan las conversaciones

**Solución:**

1. Verificar que `DATABASE_URL` esté configurado en `.env`
2. Verificar que la base de datos esté accesible
3. Revisar los logs del servidor para errores

### Problema: Conversaciones incompletas

**Solución:**

- ✅ **Ya resuelto** con la nueva implementación
- El sistema ahora solo guarda pares completos user → ai

### Problema: Timestamps incorrectos

**Solución:**

- Los timestamps ahora están en formato float (segundos desde epoch)
- Para convertir a fecha legible: `datetime.fromtimestamp(timestamp)`

---

**Última actualización**: 2025-12-10
