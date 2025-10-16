# Cómo Pasar Mensajes Entre Agentes - Respuesta Directa

## 🎯 **2 opciones principales**:

### Opción 1: **Variables en Memoria** (Monolito Modular)
Los agentes son **clases en el mismo proceso**, te pasas objetos Python directamente.

```python
# ✅ OPCIÓN 1: Variables en memoria (más simple)

# Los agentes están en el mismo proyecto
result1 = agente1.procesar(query)          # Retorna un dict
result2 = agente2.procesar(result1)        # Le pasas el dict directamente
result3 = agente3.procesar(result2)        # Así sucesivamente
```

### Opción 2: **APIs REST** (Microservicios)
Cada agente es un **servicio separado**, te comunicas con HTTP.

```python
# ✅ OPCIÓN 2: APIs REST (más complejo pero escalable)

# Cada agente es un servicio independiente
response1 = requests.post("http://agente1:8000/process", json={"query": query})
response2 = requests.post("http://agente2:8001/process", json=response1.json())
response3 = requests.post("http://agente3:8002/process", json=response2.json())
```

---

## 📝 Ejemplos Concretos

### OPCIÓN 1: Variables (Recomendado para Empezar)

```python
# main.py - Todo en el mismo proyecto

class AgenteContexto:
    def procesar(self, query: str) -> dict:
        return {
            "query_enriquecida": f"{query} con contexto",
            "metadata": {"agent": "contexto"}
        }

class AgenteSQL:
    def procesar(self, data: dict) -> dict:
        query = data["query_enriquecida"]
        return {
            "sql": f"SELECT * FROM tabla WHERE ...",
            "query_original": query
        }

class AgenteEjecutor:
    def procesar(self, data: dict) -> dict:
        sql = data["sql"]
        # Ejecutar SQL...
        return {
            "resultados": [{"id": 1, "nombre": "Juan"}],
            "rows": 1
        }

# USAR LOS AGENTES
agente1 = AgenteContexto()
agente2 = AgenteSQL()
agente3 = AgenteEjecutor()

# Pasar mensajes con variables
paso1 = agente1.procesar("¿ventas del mes?")
paso2 = agente2.procesar(paso1)              # ← Pasas el dict
paso3 = agente3.procesar(paso2)              # ← Pasas el dict

print(paso3)  # Resultado final
```

**Ventajas:**
- ✅ Más rápido (sin latencia de red)
- ✅ Más simple de debuggear
- ✅ No necesitas desplegar múltiples servicios

**Cuándo usar:** Tu caso actual, empezar con esto

---

### OPCIÓN 2: APIs REST

```python
# ========================================
# AGENTE 1 - Servicio separado en puerto 8001
# ========================================
# agente_contexto/app.py

from fastapi import FastAPI

app = FastAPI()

@app.post("/procesar")
def procesar(data: dict):
    query = data["query"]
    return {
        "query_enriquecida": f"{query} con contexto",
        "metadata": {"agent": "contexto"}
    }

# Ejecutar: uvicorn app:app --port 8001


# ========================================
# AGENTE 2 - Servicio separado en puerto 8002
# ========================================
# agente_sql/app.py

from fastapi import FastAPI

app = FastAPI()

@app.post("/procesar")
def procesar(data: dict):
    query = data["query_enriquecida"]
    return {
        "sql": f"SELECT * FROM tabla WHERE ...",
        "query_original": query
    }

# Ejecutar: uvicorn app:app --port 8002


# ========================================
# ORQUESTADOR - Llama a las APIs
# ========================================
# orchestrator.py

import requests

def procesar_query(query: str):
    # Llamar Agente 1 por API
    response1 = requests.post(
        "http://localhost:8001/procesar",
        json={"query": query}
    )
    data1 = response1.json()
    
    # Llamar Agente 2 por API
    response2 = requests.post(
        "http://localhost:8002/procesar",
        json=data1                    # ← Pasas el JSON
    )
    data2 = response2.json()
    
    return data2

# Usar
resultado = procesar_query("¿ventas del mes?")
```

**Ventajas:**
- ✅ Cada agente se despliega independiente
- ✅ Puedes escalar agentes por separado
- ✅ Diferentes lenguajes por agente

**Desventajas:**
- ❌ Más latencia (red)
- ❌ Más complejo de debuggear
- ❌ Necesitas manejar errores de red

**Cuándo usar:** Cuando tengas equipos separados o necesites escalar

---

## 🎯 Recomendación de Microsoft

Microsoft recomienda: "Muchos sistemas exitosos comienzan como monolitos modulares y evolucionan extrayendo gradualmente agentes en servicios a medida que la escala, el tamaño del equipo o los requisitos comerciales cambian"

**Traducción:** Empieza con variables, cambia a APIs solo si lo necesitas.

---

## 📊 Tabla Comparativa

| Aspecto | Variables (Opción 1) | APIs (Opción 2) |
|---------|---------------------|-----------------|
| **Velocidad** | ⚡ Rápido | 🐌 Más lento (red) |
| **Complejidad** | 😊 Simple | 😰 Compleja |
| **Despliegue** | 1 aplicación | N servicios |
| **Debugging** | Fácil | Difícil |
| **Escalabilidad** | Limitada | Alta |
| **Para empezar** | ✅ Sí | ❌ No |

---

## 💡 Mi Recomendación para Ti

```python
# FASE 1: Empieza con esto (Variables)
class Orquestador:
    def __init__(self):
        self.agente_contexto = AgenteContexto()
        self.agente_sql = AgenteSQL()
        self.agente_ejecutor = AgenteEjecutor()
    
    def procesar(self, query):
        # Pasar con variables
        r1 = self.agente_contexto.procesar(query)
        r2 = self.agente_sql.procesar(r1)
        r3 = self.agente_ejecutor.procesar(r2)
        return r3

# Usar
orq = Orquestador()
resultado = orq.procesar("ventas del mes")
```

**Cuando necesites escalar** → Migra a APIs uno por uno.

---

## 🔗 Link Oficial

**[Microsoft: Monolith vs Microservices](https://microsoft.github.io/multi-agent-reference-architecture/docs/design-options/Microservices.html)**

> "Consider starting with microservices when: teams require autonomy, deployment velocity, and continuous evolution"

**Traducción:** Solo usa APIs/microservicios si tienes equipos grandes o necesitas desplegar independientemente.
