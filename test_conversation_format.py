"""
Script para probar el formato de conversación y verificar que se guarda correctamente.
"""
import time
from database import create_call, update_call_interaction, SessionLocal
from models import Call


def test_conversation_format():
    """Prueba el formato de conversación como debe guardarse."""
    
    # Crear una llamada de prueba
    test_call_sid = f"TEST_CALL_{int(time.time())}"
    test_phone = "+1234567890"
    
    print(f"📞 Creando llamada de prueba: {test_call_sid}")
    call_id = create_call(test_call_sid, test_phone)
    
    if not call_id:
        print("❌ Error: No se pudo crear la llamada")
        return
    
    # Simular una conversación completa con el formato correcto
    conversation_log = [
        {
            "user": "Hola, qué productos tienes.",
            "ai": "Ofrezco ORISOD Enzyme®, un complejo bioactivo fermentado de olivo y romero diseñado para mejorar la capacidad antioxidante, proteger contra el daño celular y optimizar la función mitocondrial, entre otros beneficios. Su innovación clave es el ADS®, que aumenta la biodisponibilidad de los compuestos.",
            "timestamp": 1764311500.7389648
        },
        {
            "user": "Hola.",
            "ai": "Hola. Ofrezco ORISOD Enzyme®, un producto 100% vegetal y seguro que ahora viene en cápsulas de menor tamaño.",
            "timestamp": 1764311531.5316098
        },
        {
            "user": "este accidente",
            "ai": "No tengo esa información.",
            "timestamp": 1764311549.351979
        },
        {
            "user": "Es antioxidante.",
            "ai": "Sí, ORISOD Enzyme® es un antioxidante profundo, tanto enzimático como celular, que activa las defensas internas del organismo.",
            "timestamp": 1764311558.8930223
        },
        {
            "user": "en estudios clínicos",
            "ai": "Ensayos clínicos confirmaron el aumento de la actividad antioxidante, la reducción del daño al ADN, efectos antiinflamatorios, protección celular frente al estrés oxidativo, beneficios metabólicos y protección mitocondrial. También se ha observado la modulación de microRNA asociado a cáncer.",
            "timestamp": 1764311577.1043847
        }
    ]
    
    print(f"\n💬 Guardando conversación con {len(conversation_log)} interacciones...")
    update_call_interaction(test_call_sid, conversation_log)
    
    # Verificar que se guardó correctamente
    print(f"\n🔍 Verificando que se guardó correctamente...")
    db = SessionLocal()
    try:
        call = db.query(Call).filter(Call.call_sid == test_call_sid).first()
        if call:
            print(f"✅ Llamada encontrada: ID={call.id}")
            print(f"✅ Número de interacciones guardadas: {len(call.interaction_log)}")
            print(f"\n📋 Conversación guardada:")
            print("=" * 80)
            
            for i, interaction in enumerate(call.interaction_log, 1):
                print(f"\n--- Interacción #{i} ---")
                print(f"👤 Usuario: {interaction['user']}")
                print(f"🤖 IA: {interaction['ai']}")
                print(f"⏰ Timestamp: {interaction['timestamp']}")
            
            print("\n" + "=" * 80)
            
            # Verificar que cada interacción tenga los campos correctos
            all_valid = True
            for i, interaction in enumerate(call.interaction_log, 1):
                if "user" not in interaction or "ai" not in interaction or "timestamp" not in interaction:
                    print(f"❌ Interacción #{i} tiene campos faltantes")
                    all_valid = False
                elif not isinstance(interaction["user"], str) or not isinstance(interaction["ai"], str):
                    print(f"❌ Interacción #{i} tiene tipos incorrectos")
                    all_valid = False
            
            if all_valid:
                print("\n✅ ¡Todas las interacciones tienen el formato correcto!")
                print("✅ Cada interacción tiene: user (str), ai (str), timestamp (float)")
            else:
                print("\n❌ Algunas interacciones tienen problemas de formato")
        else:
            print(f"❌ No se encontró la llamada con SID: {test_call_sid}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🧪 Iniciando prueba de formato de conversación...\n")
    test_conversation_format()
    print("\n✅ Prueba completada!")
