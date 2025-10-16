# Azure AI Foundry Te Ayuda a Pasar Mensajes Entre Agentes

## 🎯

Azure AI Foundry Agent Service **te hace el trabajo pesado de comunicación entre agentes automáticamente**. No necesitas escribir código para pasar mensajes - lo hace por ti.

---

## ✨ Lo Que Hace Por Ti

### 1. **Connected Agents** - Sin Código de Orquestación

Azure AI Foundry permite que "un agente principal delegue inteligentemente a sub-agentes especializados, sin necesidad de un orquestador personalizado o lógica de enrutamiento codificada manualmente".

**En palabras simples:** 
- ❌ NO escribes código para pasar mensajes
- ✅ SÍ configuras agentes en el portal
- ✅ El sistema pasa los datos automáticamente

```python
# ❌ SIN Azure AI Foundry - Tú haces todo esto:
result1 = agente1.procesar(query)
result2 = agente2.procesar(result1)  # ← Tú pasas manualmente
result3 = agente3.procesar(result2)  # ← Tú pasas manualmente

# ✅ CON Azure AI Foundry - Automático:
# Solo defines los agentes en el portal
# El sistema se encarga de pasar los mensajes
response = orchestrator.process(query)  # ← Todo automático
```

---

## 🛠️ Cómo Lo Usas en Tu Caso

### Configuración Visual (Portal)

Azure AI Foundry te permite "configurar agentes usando una interfaz sin código en el portal Foundry o programáticamente a través del SDK de Python".

**Pasos en el Portal:**

1. **Creas tu Agente Principal (Orquestador)**
   ```
   Nombre: "Agente Consultas SQL"
   Prompt: "Eres un asistente que responde consultas de datos"
   ```

2. **Creas Agentes Especializados**
   ```
   - Agente 1: "Enriquecimiento de Contexto"
   - Agente 2: "Generador SQL"  
   - Agente 3: "Ejecutor Fabric"
   - Agente 4: "Transformador Respuesta"
   ```

3. **Conectas los Agentes**
   - En la configuración del Agente Principal
   - Sección "Connected Agents"
   - Agregas cada agente y describes qué hace
   - **Azure AI Foundry automáticamente pasa los mensajes entre ellos**

### Con Código (SDK Python)

```python
# Configuración con Azure AI Foundry SDK
from azure.ai.foundry import AIProjectClient
from azure.identity import DefaultAzureCredential

# Conectar a tu proyecto
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    credential=credential,
    subscription_id="tu-subscription",
    resource_group="tu-resource-group",
    project_name="tu-proyecto"
)

# Crear Agente Principal
orchestrator = project_client.agents.create_agent(
    model="gpt-4",
    name="SQL Query Orchestrator",
    instructions="""
    Eres un orquestador que coordina consultas SQL.
    Tienes agentes especializados para ayudarte.
    """
)

# Crear Agentes Especializados
context_agent = project_client.agents.create_agent(
    model="gpt-4",
    name="Context Enrichment",
    instructions="Enriqueces consultas con contexto y sinónimos"
)

sql_agent = project_client.agents.create_agent(
    model="gpt-4",
    name="SQL Generator",
    instructions="Generas SQL seguro basado en contexto"
)

# Conectar agentes al orquestador
# Azure AI Foundry maneja la comunicación automáticamente
orchestrator.add_connected_agent(
    agent_id=context_agent.id,
    description="Enriquece la consulta del usuario con contexto"
)

orchestrator.add_connected_agent(
    agent_id=sql_agent.id,
    description="Genera SQL cuando sea necesario"
)

# USAR - Azure AI Foundry pasa mensajes automáticamente
thread = project_client.agents.create_thread()

# Solo envías la consulta inicial
message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="¿Cuáles fueron las ventas del mes pasado?"
)

# Azure AI Foundry:
# 1. Pasa mensaje al orquestador
# 2. Orquestador llama a context_agent automáticamente
# 3. Toma resultado y llama a sql_agent automáticamente
# 4. Compone respuesta final
run = project_client.agents.create_run(
    thread_id=thread.id,
    agent_id=orchestrator.id
)

# Esperar resultado
run = project_client.agents.wait_for_run_completion(
    thread_id=thread.id,
    run_id=run.id
)

# Obtener respuesta final
messages = project_client.agents.list_messages(thread_id=thread.id)
print(messages[0].content)  # Respuesta procesada por todos los agentes
```

---

## 💡 Ventajas vs Hacerlo Manual

| Aspecto | Manual (Tu Código) | Azure AI Foundry |
|---------|-------------------|------------------|
| **Pasar mensajes** | Tu escribes el código | Automático ✅ |
| **Gestionar estado** | Tu implementas | Incluido ✅ |
| **Manejar errores** | Tu implementas reintentos | Incluido ✅ |
| **Observabilidad** | Tu instrumentas | Incluido ✅ |
| **Seguridad** | Tu configuras RBAC | Integrado con Entra ID ✅ |
| **Logging** | Tu implementas | Application Insights ✅ |

---

## 🔌 Herramientas que Incluye

Azure AI Foundry se integra con "más de 1,400 conectores en Azure Logic Apps, Azure Functions, Bing, SharePoint, Microsoft Fabric, Azure AI Search".

**Para tu caso específico:**

```python
# Conectar a Fabric directamente desde Azure AI Foundry
sql_agent = project_client.agents.create_agent(
    model="gpt-4",
    name="Fabric SQL Agent",
    tools=[
        {
            "type": "fabric",  # ← Conector nativo a Fabric
            "fabric": {
                "workspace_id": "tu-workspace",
                "lakehouse_id": "tu-lakehouse"
            }
        }
    ]
)

# El agente puede ejecutar SQL directamente en Fabric
# Sin que escribas código de conexión
```

### Herramientas Disponibles para Ti:

- ✅ **Microsoft Fabric** - Ejecutar SQL directamente
- ✅ **SharePoint** - Acceder documentos
- ✅ **Azure AI Search** - Buscar en tus datos
- ✅ **Azure Functions** - Lógica custom
- ✅ **Logic Apps** - Workflows complejos (1400+ conectores)
- ✅ **Bing Search** - Búsquedas web

---

## 🔐 Seguridad Incluida

Azure AI Foundry "aplica características de confianza de nivel empresarial que incluyen identidad a través de Microsoft Entra, RBAC, filtros de contenido, cifrado y aislamiento de red".

**Lo que significa:**
- Azure Entra ID (Active Directory) integrado
- Control de acceso basado en roles automático
- No necesitas Azure Key Vault manualmente (usa Managed Identity)
- Red privada virtual opcional

```python
# Seguridad automática por usuario
context_for_user = {
    "user_id": "user123",
    "user_roles": ["sucursal"]  # ← Azure AI Foundry filtra datos automáticamente
}

# Los agentes respetan automáticamente los permisos
response = orchestrator.process(query, user_context=context_for_user)
```

---

## 📊 Observabilidad Automática

Azure AI Foundry "captura logs, trazas y evaluaciones en cada paso. Con visibilidad a nivel de hilo completo e integración con Application Insights".

**Qué obtienes gratis:**
- Trazas de cada llamada entre agentes
- Latencia por agente
- Tokens consumidos
- Errores y reintentos
- Todo en Application Insights

```python
# Ver trazas automáticamente en Azure Portal
# No necesitas instrumentar manualmente
```

---

## 🆚 Comparación: Manual vs Azure AI Foundry

### Escenario: Tu Pipeline SQL

**Opción 1: Manual (lo que preguntaste antes)**
```python
# Tu escribes todo esto:
result1 = context_agent.enrich(query)          # ← Tú pasas
result2 = sql_agent.generate(result1)          # ← Tú pasas
result3 = executor.execute(result2)            # ← Tú pasas
result4 = transformer.transform(result3)       # ← Tú pasas

# Y también manejas:
# - Errores entre agentes
# - Timeouts
# - Logs
# - Seguridad
# - Estado de conversación
```

**Opción 2: Azure AI Foundry**
```python
# Solo defines y usas:
response = orchestrator.process(query, user_context)
# ✅ Pasa mensajes automáticamente
# ✅ Maneja errores automáticamente
# ✅ Logs automáticos
# ✅ Seguridad integrada
# ✅ Estado manejado automáticamente
```

---

## 🎓 Recomendación Práctica

### Para Tu Caso (SQL + Fabric):

**Usa Azure AI Foundry si:**
- ✅ Quieres empezar rápido (menos código)
- ✅ Necesitas integración nativa con Fabric
- ✅ Quieres seguridad enterprise automática
- ✅ Tu equipo prefiere configuración visual
- ✅ Necesitas observabilidad sin esfuerzo

**Usa código manual si:**
- ❌ Necesitas control total de cada paso
- ❌ Tienes lógica muy específica que Azure AI Foundry no soporta
- ❌ Quieres minimizar dependencia de Azure

### Mejor Enfoque: Híbrido

```python
# Usa Azure AI Foundry para orquestación
orchestrator = AIFoundryOrchestrator()

# Pero implementa lógica específica como Azure Functions
@app.function_name("CustomSQLValidation")
def validate_sql(sql: str, user_roles: list) -> bool:
    # Tu lógica específica de negocio
    return is_valid

# Conéctalo como herramienta
orchestrator.add_tool(
    type="azure_function",
    function_name="CustomSQLValidation"
)
```

---

## 📚 Links Oficiales

1. **[Azure AI Foundry Agent Service - Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)**
   - Qué es y cómo funciona

2. **[How to use Connected Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/connected-agents)**
   - Tutorial paso a paso

3. **[Azure AI Foundry Product Page](https://azure.microsoft.com/en-us/products/ai-agent-service/)**
   - Características y precios

4. **[Multi-Agent Orchestration Guide](https://techcommunity.microsoft.com/blog/azureinfrastructureblog/multi%E2%80%91agent-orchestration-with-azure-ai-foundry-from-idea-to-production/4449925)**
   - De idea a producción

5. **[Microsoft Agent Framework](https://azure.microsoft.com/en-us/blog/introducing-microsoft-agent-framework/)**
   - Framework open-source que usa Azure AI Foundry

---

## ✅ Resumen de 3 Puntos

1. **Azure AI Foundry pasa mensajes entre agentes automáticamente** - No escribes código de orquestación

2. **Incluye todo lo que necesitas** - Seguridad, observabilidad, manejo de errores, integración con Fabric

3. **Configuras visualmente o con SDK** - Portal sin código o Python SDK según prefieras

---

**¿Siguiente paso?** Prueba el [Azure AI Foundry Free Tier](https://azure.microsoft.com/en-us/products/ai-agent-service/) para ver si se ajusta a tu caso de uso antes de escribir todo el código manualmente.
