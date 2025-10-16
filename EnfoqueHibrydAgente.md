# Estrategia Híbrida: Código + Foundry

## 🎯 Estrategia Recomendada

### Opción 1: Agentes Custom como Azure Functions

```python
# Tu agente custom con lógica específica
# custom_agent/function_app.py

import azure.functions as func

@func.route(route="sql_agent")
def sql_agent_custom(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    
    # TU LÓGICA ESPECÍFICA
    enriched_query = data['enriched_query']
    user_roles = data['user_roles']
    
    # Conexión custom a Fabric (si Foundry no lo soporta como necesitas)
    sql = generate_sql_with_custom_logic(enriched_query, user_roles)
    
    return func.HttpResponse(
        json.dumps({"sql": sql}),
        mimetype="application/json"
    )
```

```python
# En Foundry - Conectas tu Azure Function
orchestrator = project_client.agents.create_agent(
    name="Orchestrator",
    tools=[
        {
            "type": "azure_function",
            "azure_function": {
                "function_url": "https://tu-function.azurewebsites.net/api/sql_agent",
                "method": "POST"
            }
        }
    ]
)
```

---

### Opción 2: OpenAPI Custom

```python
# 1. Tu API custom con FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.post("/enrich")
def enrich_context(query: str, user_context: dict):
    # Tu lógica específica de negocio
    return {"enriched": query + " con contexto custom"}

@app.post("/validate_sql")
def validate_sql(sql: str, roles: list):
    # Validación específica que Foundry no tiene
    return {"valid": True, "filtered_sql": sql}
```

```python
# 2. Registras tu API en Foundry
orchestrator.add_tool(
    type="openapi",
    openapi_spec="https://tu-api.com/openapi.json"
)
```

---

### Opción 3: Mix - Algunos en Foundry, Otros en Código

```python
# Agentes SIMPLES en Foundry (portal/SDK)
context_agent = foundry.create_agent(
    name="Context Enrichment",
    tools=["bing_search", "sharepoint"]  # ← Conectores nativos
)

# Agentes COMPLEJOS en tu código
class CustomSQLAgent:
    def __init__(self, fabric_client):
        self.fabric = fabric_client
        self.custom_logic = YourBusinessLogic()
    
    def process(self, data: dict) -> dict:
        # Lógica que Foundry no soporta
        return self.custom_logic.generate_sql(data)

# Orquestador híbrido
class HybridOrchestrator:
    def __init__(self):
        self.foundry_agent = context_agent  # ← De Foundry
        self.custom_agent = CustomSQLAgent()  # ← Tu código
    
    async def process(self, query: str):
        # Paso 1: Usa Foundry
        enriched = await self.foundry_agent.run(query)
        
        # Paso 2: Usa tu código custom
        sql = self.custom_agent.process(enriched)
        
        return sql
```

---

## 📊 Tabla de Decisión

| Componente | Usar Foundry | Usar Código Custom |
|------------|--------------|-------------------|
| **Enriquecimiento simple** | ✅ Foundry | Si necesitas lógica compleja |
| **Búsqueda (Bing, SharePoint)** | ✅ Foundry | - |
| **SQL Generator** | ❌ No existe | ✅ Tu código |
| **Conexión específica Fabric** | Depende | ✅ Probablemente tu código |
| **Validaciones de negocio** | ❌ | ✅ Tu código |
| **Transformación respuesta** | ✅ Foundry | - |

---

## 🔗 Patrón Recomendado

```python
# Foundry como coordinador, tu código como herramientas

# 1. Tus agentes custom como Azure Functions
azure_function_1 = "https://func.azure.com/sql-generator"
azure_function_2 = "https://func.azure.com/fabric-executor"

# 2. Orchestrator en Foundry usa tus funciones
orchestrator = foundry_client.agents.create_agent(
    model="gpt-4",
    name="Main Orchestrator",
    instructions="Coordinas agentes custom",
    tools=[
        {"type": "azure_function", "url": azure_function_1},
        {"type": "azure_function", "url": azure_function_2},
        {"type": "bing_search"},  # ← Native de Foundry
    ]
)

# 3. Usas Foundry normalmente
response = orchestrator.run(thread_id, "query del usuario")
```

---

## ✅ Ventajas del Híbrido

- ✅ Usas conectores nativos de Foundry donde existen
- ✅ Tu lógica específica como Azure Functions/APIs
- ✅ Foundry maneja orquestación y observabilidad
- ✅ Control total donde lo necesitas

---

## 📚 Link Oficial

**[Azure Functions as Agent Tools](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools-azure-functions)**

**Respuesta:** SÍ, estrategia híbrida es la más común y recomendada.
