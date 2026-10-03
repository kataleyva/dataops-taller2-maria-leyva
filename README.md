# Parte II: Caso DataCorp Analytics

## Actividad 1: Diseño de Entornos Aislados

### 1.1. Tabla definida de entornos:

| Entorno | Propósito | Acceso | Datos | Infraestructura | Control de código |
|---|---|---|---|---|---|
| DEV | Experimentación: se pueden hacer todo tipo de pruebas con diferentes variables, algoritmos y transformaciones para los modelos predictivos de retail sin afectar a nadie. | Todo el equipo de desarrollo (ingenieros y científicos de datos); cada uno tiene su propio entorno. | Muestras pequeñas de ventas anonimizadas y datos sintéticos de clientes. No se usan datos de producción. | Instancias de cómputo pequeñas por persona y un bucket de almacenamiento de desarrollo. | Ramas `feature/*` en Git con commits en ciclos cortos. |
| QA | Simular producción lo más fielmente posible para detectar errores antes de que lleguen a los clientes. | Equipo de QA y auditores, sin despliegues manuales (solo el pipeline despliega). | Snapshot periódico de producción con la PII de clientes anonimizada o seudonimizada. | Espejo de producción: mismos módulos de Terraform y especificaciones, a menor escala. | Rama `main` en Git; cada pull request pasa por revisión. |
| PROD | Servir los pronósticos de ventas, las APIs y los dashboards a los clientes retail de DataCorp. | Únicamente el pipeline de CD y el equipo de monitoreo. El equipo de desarrollo no tiene acceso. | Datos reales y operacionales de las transacciones de los clientes. | Base de datos de alta disponibilidad, con monitoreo, alertas y respaldos automáticos. | Versiones etiquetadas desplegadas desde `main`. Cualquier cambio requiere un nuevo despliegue. |

### 1.2. Tabla definida de entornos:
![Flujo de un cambio entre entornos](docs/images/d-flujo-1.png)

### 1.3 Simulación de escenario de error:

Supongamos que un científico de datos mejora un modelo que pronostica ventas agregando una variable que tiene en cuenta la estacionalidad. El cambio pasa las pruebas en DEV, aprobando pull request y promoviendo a QA. Cuando el modelo se entrena con el snapshot de producción, el modelo obtiene un MAPE de 18%, mientras que el modeo actual en producción tiene 12% y un umbral máximo de 15%, inidican que el modelo se equivoca en el pronóstico más en producción.

Protocolo de actuación:

1. Detectar mediante las etapas de Train & Validate, se compara el MAPE contra el umbral y contra el modelo en producción, por lo que si no cumple, el job termina como error.
Herramientas: GitHub Actions, MLflow.
2. Bloquear el pipeline si la versión no funciona ni mejora.
Herramientas: Protección de cada rama y entornos de git.
3. Tener notificaciones de alerta al equipo con el enlace de cuando las métricas y commit generan un error.
Herramientas: Slack o correo.
4. Registrar incidencia de métricas, con la versión de los datos, commit e hiperparámetros utilizados.
Herramientas: GitHub Issues, y MLFlow.
5. Diagnosticar reproduce el entrenamiento en DEV manteniendo versiones de código y datos para encontrar la causa: data drift, sobreajuste o eeror en la distribución de las variables.
Herramientas: DVC y MLflow.
6. Corregir sobre rama con error generando nuevo commit y pull request
Herramientas: Git.

Validaciones:

1. Evaluación del desempeño del modelo con MAPE menor o igual a 15% y no menor que el desplegado.
2. Verificación de datos de entrada con esquema correcto, no nulos y valores dentro de rangos.
3. Detección de data drift, es decir, distribución de entrenamiento de conjunto de datos, similar a conjunto de pruebas.
4. API responde en menos de 300ms con volumen proporiconado con QA.
5. Aprobación explícita de líder técnico.

## Actividad 2: Implementación de MDM

### 2.1. Entidades maestras

1. Cliente:
- ATributos clave: id o llave del cliente, tipo y número de documento, nombre completo, correo, cidudad, etc.
- Fuentes de datos: Sistemas de las tiendas, e-commerce, programas de fidelización.
- Reglas de calidad: Documento único y obligatorio, correos con formato válidos sin duplicados y consentimientos diligenciados.
- Responsable: Director CRM.

2. Producto:
- Atributos clave: id o llave del producto, nombre, categoría, marca, precio, stock, etc.
- Fuentes de datos: ERP, sistemas de inventarios, catálogos de e-commerce, fichas de proveedores.
- Reglas de calidad: Elemento único dentro un catálogo verificado y que sea un producto activo.
- Responsable: Genrente de categorías.

3. Proveedor:
- ATributos clave: id o llave del proveedor, NIT, razón social, contacto, correo, condiciones de pago, tiempo de entrega, etc.
- Fuentes de datos:  contratos, portal de proveedores.
- Reglas de calidad:NIT único y válido, razón social estandarizada y correo con formato válido.
- Responsable: Gerente de Compras.

4. Ubicación:
- ATributos clave: id o llave de la ubicación, código de tienda, tipo (tienda, bodega o centro de distribución), dirección, ciudad, región, etc.
- Fuentes de datos: sistema de operaciones, registros de aperturas y cierres de tiendas.
- Reglas de calidad: código de tienda único, ciudad según la codificación oficial (DANE), no tener en cuenta ubicaciones inactivas.
- Responsable: Gerente de Operaciones.

5. Finanzas:
- ATributos clave: centro de costo, moneda, tasa de cambio, etc.
- Fuentes de datos: tasas oficiales como la del banco de la república.
- Reglas de calidad: cada venta asociada a un centro de costo válido, moneda en formato estándar.
- Responsable: Director financiero.

### 2.2. Entidades maestras
![Flujo de un cambio entre entornos](docs/images/d-flujo-2.png)

### 2.3. Políticas de gobernanza

1. Definición de cliente activo: Un cliente es activo si realizó al menos una compra en los últimos 6 meses en cualquier canal (tiendas o e-commerce). Asimismo, su fecha de corte es el último día de cada mes y las interacciones sin compra no lo convierten en un cliente en activo.

2. Reglas de limpieza y duplicación: Para la limpieza, los documento se guarda sin puntos ni espacios. Por otro lado, los nombres se estandarizan en mayúscula inicial y sin espacios dobles. En el caso de los registros sin documento o sin consentimiento diligenciado se rechazan y se reportan a la fuente. Para la detección de duplicados: dos registros son el mismo cliente si tienen el mismo tipo y número de documento. Si hay un caso en que el documento no coincide pero el correo sí, el caso se marca como posible duplicado y es revisado por el equipo de calidad. Se debe conservar un único registro con una sola llave de cliente, mientras que, para cada atributo se toma el valor más reciente y completo.

3. Flujo de aprobación para cambios: 
![Flujo de un cambio entre entornos](docs/images/d-flujo-3.png)
Cualquier cambio en la definición de "cliente activo", en las reglas de calidad o en los atributos del cliente debe funciona a través de este flujo. Asimismo, El análisis de impacto identifica qué modelos, dashboards y reportes se verían afectadosy ningún cambio se aplica directamente en producción.

4. Políticas de acceso y seguridad: Cada rol tiene derecho a acceder exclusivamente a lo que requiere para completar sus tareas. El Director CRM puede consultar los datos y es quien aprueba los cambios. El equipo de calidad de datos puede consultarlos y corregir registros. Los científicos de datos trabajan únicamente con datos anonimizados, y los analistas y dashboards solo reciben datos agregados. Los sistemas de las tiendas y el e-commerce leen el registro maestro mediante la sincronización. Además, los datos personales se cifran tanto en reposo como en tránsito, y en los entornos de DEV y QA solo se usan datos anonimizados o seudonimizados. Solo se tratan datos de clientes que diligenciaron el consentimiento informado.

### 2.4. Simulación de caso

Caso: Los sistemas de las tiendas consideran activo a un cliente que compró en tienda en los últimos 6 meses, mientras que los programas de fidelización consideran activo a quien acumuló o redimió puntos en los últimos 12 meses. Por ejemplo, una cliente aparece en los sistemas de las tiendas con el documento 1.020.304.050 y su última compra fue hace 8 meses, por lo que allí figura como inactiva. En los programas de fidelización aparece con el documento 1020304050 y redimió puntos hace 3 meses, por lo que allí figura como activa. Así, la misma persona es activa para un sistema e inactiva para el otro. Además, como su documento viene con formatos distintos, sin MDM no es posible reconocer que es el mismo cliente. Si el modelo de pronóstico usa una fuente y el dashboard de marketing usa otra, el número de clientes activos no coincide.

Resolución: Inicialmente, al limpiar el documento y dejarlo sin puntos, las dos fuentes se reconocen como la misma cliente y se fusionan en un solo registro con una llave. Luego se aplica la definición oficial aprobada por el Director CRM. Como el cliente compró hace 8 meses, queda como activa. Así, el modelo, dashboard y los reportes leen el estado de la cliente desde el registro maestro y ya no lo calculan a parte. Si se desea que redimir puntos cuente como actividad, debe solicitarlo mediante el flujo de aprobación. Si se aprueba, se crea una nueva versión de la definición sin borrar la anterior.

Impacto: Si la definición cambia sin control, no es posible recrear un modelo antiguo, porque ya no está definido con qué criterio fueron identificados los clientes activos. Con MDM, cada versión de la definición queda registrada con su fecha de vigencia y cada modelo guarda qué versión utilizó. Por lo que permite comparar las diferentes versiones de los modelos de forma justa, partiendo de que la diferencia entre ellos se debe al cambio de definición y no solo al algoritmo.

## Actividad 3: Control de versiones para todo

### 3.1 Estructura de git simulada

### 3.2 Archivo README.md

### 3.3 Simulación commit y pull request

## Actividad 4: Infraestructura como Código (IaC)

### 4.1 Archivo Terraform

### 4.2 Replicación de entornos

### 4.3 Flujo de trabajo

## Actividad 5: Continuous para DataOps

### 5.1 Pipeline CD

### 5.2 Definiciones

### 5.3 Simulación fallo

### 5.4 Diagrama del pipeline

## Actividad 6: Integración final

### 6.1 Elaboración de plan

### 6.2 Definicón métricas

### 6.3 Informe

### 6.4 Diagrama final
