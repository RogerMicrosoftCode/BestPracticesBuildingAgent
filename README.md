# BestPracticesBuildingAgents
Best practices for building agents on Aure

# Arquitectura de Agentes de IA - Guía de Implementación

Análisis y recomendaciones basadas en la documentación de [Microsoft Azure - Patrones de Orquestación de Agentes de IA](https://learn.microsoft.com/es-es/azure/architecture/ai-ml/guide/ai-agent-design-patterns)

---

## 1. Patrón de Orquestación Recomendado: Secuencial + Entrega (Handoff)

Tu flujo actual (pregunta → enriquecimiento → SQL → ejecución → transformación) se alinea perfectamente con una **orquestación secuencial**, donde:

### Arquitectura de Agentes Propuesta

- **Agente 1 - Contextualizador**: Recibe la pregunta y la enriquece con contexto relevante
- **Agente 2 - Generador SQL**: Decide si necesita SQL y lo genera
- **Agente 3 - Ejecutor**: Interactúa con Fabric para ejecutar consultas
- **Agente 4 - Transformador**: Convierte la respuesta técnica en lenguaje natural

### Ventajas Clave

- **Especialización**: Cada agente se enfoca en una tarea específica, reduciendo complejidad
- **Mantenibilidad**: Puedes probar y depurar cada agente independientemente
- **Escalabilidad**: Agregar nuevas capacidades sin rediseñar todo el sistema

### Patrón de Entrega (Handoff)

Considera el **patrón de Entrega** para casos donde el agente contextualizador detecte que la consulta requiere un agente especializado diferente (por ejemplo, consultas de análisis predictivo vs consultas descriptivas).

---

## 2. Gestión de Prompts e Ingeniería de Prompts

Los agentes pueden optimizarse usando modelos distintos, enfoques de resolución de tareas, conocimientos, herramientas y procesos específicos para lograr sus resultados.

### Estructura Sugerida para Gestión de Prompts

```python
# Estructura sugerida para gestión de prompts
prompts_db = {
    "agente_contexto": {
        "version": "2.0",
        "template": "Eres un experto en...",
        "variables": ["user_role", "query_domain"],
        "synonyms_ref": "synonyms_v1"
    },
    "agente_sql": {
        "version": "1.5",
        "template": "Genera SQL válido para...",
        "schema_ref": "fabric_schema_v3"
    }
}
```

### Diccionarios de Sinónimos

```json
{
  "sinonimos_financieros": {
    "ventas": ["revenue", "ingresos", "facturación"],
    "cliente": ["customer", "comprador", "consumidor"],
    "periodo": ["trimestre", "Q1", "quarter"]
  }
}
```

**Beneficios:**
- ✅ Versionamiento de prompts independiente del código
- ✅ Mejora continua sin deployments
- ✅ A/B testing de diferentes versiones
- ✅ Gestión centralizada y auditable

---

## 3. Seguridad y Control de Acceso

El filtrado de seguridad debe implementarse en todos los agentes del patrón. Los agentes deben tener acceso amplio a los almacenes de conocimiento para controlar las solicitudes de todos los usuarios, pero no deben devolver datos inaccesibles para el usuario.

### Arquitectura de Seguridad Recomendada

```python
# Implementación con Azure
class SecureAgentOrchestrator:
    def __init__(self):
        # Servicios de identidad
        self.identity_service = EntraID()  # Azure Active Directory
        
        # Bóveda de credenciales
        self.vault = AzureKeyVault()
        
    async def process_query(self, query, user_context):
        # 1. Validar identidad
        user_roles = self.identity_service.get_user_roles(
            user_context.token
        )
        
        # 2. Filtrar datos según rol
        access_level = self._determine_access(user_roles)
        # call_center: datos básicos
        # sucursal: datos de sucursal específica
        # direccion: datos completos
        
        # 3. Pasar contexto de seguridad entre agentes
        secure_context = {
            "user_id": user_context.id,
            "roles": user_roles,
            "data_filter": access_level
        }
        
        return await self.execute_agent_chain(
            query, 
            secure_context
        )
    
    def _determine_access(self, roles):
        """Determina nivel de acceso basado en roles"""
        if "direccion" in roles:
            return "full"
        elif "sucursal" in roles:
            return "branch_limited"
        elif "call_center" in roles:
            return "basic"
        return "none"
```

### Componentes de Seguridad Esenciales

| Componente | Servicio Azure | Propósito |
|------------|---------------|-----------|
| **Identidad** | Azure Entra ID (Active Directory) | Autenticación y roles de usuario |
| **Credenciales** | Azure Key Vault | Almacenamiento seguro de API keys y secretos |
| **Filtrado de Datos** | Row-Level Security (Fabric) | Control de acceso a nivel de registro |
| **Auditoría** | Azure Monitor | Trazabilidad de accesos y operaciones |

---

## 4. Integración con LangChain y Fabric

Implementación práctica para tu stack tecnológico específico.

### Agente Especializado para SQL

```python
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from azure.ai.ml import MLClient

class FabricSQLAgent:
    def __init__(self, fabric_client):
        self.fabric = fabric_client
        self.prompt_template = load_from_db("agente_sql")
        self.synonyms = load_from_db("synonyms_dict")
        
    def enrich_query(self, user_query):
        """Aplicar diccionario de sinónimos"""
        enriched = self._apply_synonyms(user_query)
        return enriched
    
    def _apply_synonyms(self, query):
        """Reemplaza términos con sinónimos conocidos"""
        for term, synonyms in self.synonyms.items():
            for syn in synonyms:
                if syn.lower() in query.lower():
                    query = query.replace(syn, term)
        return query
    
    def generate_sql(self, enriched_query, user_context):
        """Generar SQL con control de acceso"""
        # Filtrar esquema según permisos
        allowed_tables = self._get_allowed_tables(
            user_context.roles
        )
        
        # Generar SQL con LangChain
        sql_chain = create_sql_chain(
            allowed_tables=allowed_tables
        )
        return sql_chain.run(enriched_query)
    
    def _get_allowed_tables(self, roles):
        """Determina qué tablas puede consultar el usuario"""
        base_tables = ["productos", "categorias"]
        
        if "sucursal" in roles:
            base_tables.extend(["ventas_sucursal", "inventario_sucursal"])
        
        if "direccion" in roles:
            base_tables.extend(["ventas_global", "finanzas", "nomina"])
        
        return base_tables
```

### Orquestador Principal con LangChain

```python
from langchain.chains import SequentialChain
from langchain.memory import ConversationBufferMemory

class AgentOrchestrator:
    def __init__(self):
        self.context_agent = ContextEnrichmentAgent()
        self.sql_agent = FabricSQLAgent()
        self.executor_agent = QueryExecutorAgent()
        self.transformer_agent = ResponseTransformerAgent()
        
    async def process(self, user_query, user_context):
        """Pipeline secuencial de agentes"""
        
        # Paso 1: Enriquecimiento de contexto
        enriched_query = await self.context_agent.enrich(
            user_query,
            user_context
        )
        
        # Paso 2: Generación de SQL (si aplica)
        if self._requires_sql(enriched_query):
            sql_query = await self.sql_agent.generate_sql(
                enriched_query,
                user_context
            )
            
            # Paso 3: Ejecución
            raw_results = await self.executor_agent.execute(
                sql_query,
                user_context
            )
        else:
            # Handoff a agente conversacional
            raw_results = await self._handle_non_sql_query(
                enriched_query
            )
        
        # Paso 4: Transformación de respuesta
        final_response = await self.transformer_agent.transform(
            raw_results,
            user_query
        )
        
        return final_response
```

---

## 5. Consideraciones Críticas Base Microsoft

Aspectos que debes considerar en tu implementación: ventana de contexto, confiabilidad, observabilidad y pruebas.

### Ventana de Contexto

**Principio:** No pases todo el historial entre agentes si no es necesario.

```python
# ❌ INCORRECTO - Pasar todo el contexto
agent_2_input = {
    "full_conversation_history": [...],  # Innecesario
    "user_profile": {...},
    "system_logs": [...]
}

# ✅ CORRECTO - Solo lo necesario
agent_2_input = {
    "enriched_query": "SELECT ventas WHERE...",
    "user_roles": ["sucursal"],
    "allowed_tables": ["ventas_sucursal"]
}
```

### Confiabilidad

Implementar timeouts, reintentos y degradación elegante.

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def execute_fabric_query(sql, timeout=30):
    """Ejecutar consulta con reintentos automáticos"""
    try:
        return await fabric_client.execute(sql, timeout=timeout)
    except FabricTimeoutError:
        # Degradación elegante
        logger.warning("Fabric timeout, usando caché")
        return {
            "error": "timeout",
            "fallback": get_cached_results(sql)
        }
    except FabricConnectionError as e:
        logger.error(f"Error de conexión: {e}")
        raise
```

### Observabilidad

Instrumentación completa de todos los agentes.

```python
import opentelemetry
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# Configurar Azure Monitor
configure_azure_monitor()
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("contextualizador")
def contextualize_query(query):
    """Agente con observabilidad completa"""
    span = trace.get_current_span()
    
    # Registrar métricas
    span.set_attribute("query.length", len(query))
    span.set_attribute("query.language", detect_language(query))
    
    # Proceso del agente
    synonyms_count = apply_synonyms(query)
    span.set_attribute("synonyms.applied", synonyms_count)
    
    enriched = enrich_with_context(query)
    span.set_attribute("context.added", True)
    
    return enriched
```

### Dashboard de Observabilidad Sugerido

Métricas clave a monitorear:

- **Latencia por agente**: Tiempo de ejecución de cada agente
- **Tasa de éxito**: % de consultas completadas exitosamente
- **Cache hit rate**: Eficiencia del caché de resultados
- **Errores por tipo**: Timeouts, permisos, SQL inválido
- **Uso de sinónimos**: Efectividad del diccionario

---

## 6. Antipatrones a Evitar

La documentación advierte contra crear complejidad de coordinación innecesaria mediante un patrón complejo cuando bastaría una orquestación secuencial o simultánea simple.

### ✅ Buenas Prácticas

| Práctica | Descripción |
|----------|-------------|
| **Separación clara** | Mantén agente contexto + agente SQL con responsabilidades bien definidas |
| **Handoff inteligente** | Si consultas NO requieren SQL, implementa handoff para evitar pasos innecesarios |
| **Especialización** | Cada agente debe tener un propósito único y claro |
| **Pruebas unitarias** | Cada agente debe poder probarse independientemente |

### ❌ Antipatrones Comunes

| Antipatrón | Por qué evitarlo |
|------------|------------------|
| **Agente para todo** | Un solo agente con muchas herramientas es difícil de mantener |
| **Agente innecesario** | No crear agentes solo para logging o validaciones simples |
| **Contexto excesivo** | Pasar información innecesaria entre agentes |
| **Estado compartido mutable** | Puede causar inconsistencias en orquestación simultánea |

---

## 7. Recursos y Frameworks Disponibles

Según tu stack, te recomiendo explorar:

### Microsoft Agent Framework

**Ideal para:** Implementación con código declarativo

```yaml
# Ejemplo de workflow declarativo
workflow:
  name: consultas-inteligentes
  agents:
    - name: contextualizador
      type: sequential
      model: gpt-4
      prompts: db://prompts/contexto
      
    - name: generador-sql
      type: sequential
      model: gpt-4
      prompts: db://prompts/sql
      tools:
        - fabric-connector
```

**Documentación:** [Agent Framework Implementation](https://learn.microsoft.com/es-es/agent-framework/user-guide/workflows/overview)

### Semantic Kernel

**Ideal para:** Control programático completo

```csharp
// Ejemplo con Semantic Kernel
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(deploymentName, endpoint, apiKey)
    .Build();

var contextAgent = kernel.CreateFunctionFromPrompt(
    await LoadPromptFromDB("agente_contexto")
);

var sqlAgent = kernel.CreateFunctionFromPrompt(
    await LoadPromptFromDB("agente_sql")
);
```

**Documentación:** [Semantic Kernel Agent Orchestration](https://learn.microsoft.com/es-es/semantic-kernel/frameworks/agent/agent-orchestration/)

### Azure AI Foundry

**Ideal para:** Orquestaciones sin código (limitado a patrones simples)

**Limitaciones:** Solo para flujos no deterministas y relativamente simples

---

## 8. Patron Usual en la construccion de Agentes AI

### Fase 1: Fundamentos 

- [ ] Configurar Azure Key Vault para credenciales
- [ ] Implementar servicio de identidad con Entra ID
- [ ] Crear esquema de base de datos para prompts
- [ ] Definir diccionarios de sinónimos iniciales

### Fase 2: Agentes Core 

- [ ] Desarrollar Agente Contextualizador
- [ ] Desarrollar Agente Generador SQL
- [ ] Implementar filtrado de seguridad por rol
- [ ] Crear suite de pruebas unitarias

### Fase 3: Orquestación 

- [ ] Implementar orquestador secuencial
- [ ] Agregar Agente Ejecutor (Fabric)
- [ ] Agregar Agente Transformador
- [ ] Implementar handoff para casos no-SQL

### Fase 4: Producción

- [ ] Configurar observabilidad completa
- [ ] Implementar reintentos y fallbacks
- [ ] Pruebas de integración end-to-end
- [ ] Documentación y capacitación

---

## 9. Checklist de Seguridad

Antes de ir a producción, verifica:

- [ ] **Autenticación**: Todos los agentes validan identidad del usuario
- [ ] **Autorización**: Filtrado de datos según rol implementado
- [ ] **Credenciales**: Ningún secreto en código o configuración local
- [ ] **Auditoría**: Logs de todas las consultas y accesos
- [ ] **Cifrado**: Datos sensibles cifrados en tránsito y reposo
- [ ] **Rate Limiting**: Protección contra abuso del sistema
- [ ] **Input Validation**: Sanitización de entradas de usuario
- [ ] **SQL Injection**: Queries parametrizadas, no concatenación

---

## 10. Preguntas Frecuentes

### ¿Cuándo usar orquestación simultánea en lugar de secuencial?

Usa simultánea cuando:
- Las tareas son independientes entre sí
- Necesitas reducir latencia
- Requieres múltiples perspectivas del mismo problema

Para tu caso de SQL, secuencial es más apropiado porque cada paso depende del anterior.

### ¿Cómo manejar consultas que no requieren SQL?

Implementa el patrón de Handoff:

```python
def route_query(enriched_query):
    if requires_database_query(enriched_query):
        return sql_agent_pipeline(enriched_query)
    else:
        return conversational_agent(enriched_query)
```

### ¿Qué hacer si Fabric tiene un outage?

Implementa estrategia de fallback:

1. **Reintentos exponenciales** (3 intentos)
2. **Cache de resultados frecuentes**
3. **Respuesta degradada** informando al usuario
4. **Alertas a equipo técnico**

---

## Referencias

- [Microsoft Azure - Patrones de Orquestación de Agentes de IA](https://learn.microsoft.com/es-es/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Microsoft Agent Framework](https://learn.microsoft.com/es-es/agent-framework/overview/agent-framework-overview)
- [Semantic Kernel Documentation](https://learn.microsoft.com/es-es/semantic-kernel/)
- [Azure AI Foundry Agents](https://learn.microsoft.com/es-es/azure/ai-foundry/agents/overview)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)

---

**Última actualización:** Octubre 2025  
**Versión:** 1.0
