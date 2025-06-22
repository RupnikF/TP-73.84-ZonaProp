# Despliegue de la API

## Propuesta de Despliegue
La API desarrollada en este proyecto puede ser desplegada en un entorno real utilizando un servidor de aplicaciones compatible con Python, como Uvicorn, que ya está especificado en los requisitos del proyecto. A continuación, se describe una propuesta teórica para su despliegue:

1. **Contenedorización con Docker**:
   - Crear un archivo `Dockerfile` que contenga las instrucciones para construir una imagen de Docker con la API y sus dependencias.
   - Utilizar `docker-compose` para orquestar el despliegue si se requieren múltiples servicios (por ejemplo, base de datos, balanceadores de carga).

2. **Infraestructura en la Nube**:
   - Utilizar un proveedor de nube como AWS, Google Cloud Platform (GCP) o Microsoft Azure para alojar la API.
   - Configurar una instancia de máquina virtual o un servicio de contenedores como AWS ECS, Google Kubernetes Engine (GKE) o Azure Kubernetes Service (AKS).

3. **Balanceo de Carga y Escalabilidad**:
   - Implementar un balanceador de carga (por ejemplo, AWS Elastic Load Balancer o NGINX) para distribuir el tráfico entre múltiples instancias de la API.
   - Configurar escalado automático basado en métricas como el uso de CPU o la cantidad de solicitudes por segundo.

4. **Seguridad**:
   - Configurar HTTPS utilizando un certificado SSL/TLS.
   - Implementar autenticación y autorización en la API para proteger los endpoints.

5. **Monitoreo y Logs**:
   - Utilizar herramientas como Prometheus y Grafana para monitorear el rendimiento de la API.
   - Configurar un sistema de logs centralizado como ELK Stack (Elasticsearch, Logstash, Kibana) o servicios en la nube como CloudWatch (AWS).

6. **Manejo de Versiones de Modelos y Pipeline con MLflow**:
   - Integrar MLflow para realizar un seguimiento de los experimentos, registrar métricas y almacenar versiones de los modelos y el pipeline de preprocesamiento.
   - Configurar un servidor MLflow para centralizar el almacenamiento de modelos y facilitar su recuperación durante el despliegue.
   - Etiquetar cada versión del modelo y pipeline con un identificador único para facilitar el seguimiento y la recuperación.
   - Implementar un sistema de pruebas automatizadas para validar nuevas versiones del modelo y pipeline antes de su despliegue.
   - Documentar los experimentos, cambios realizados y resultados directamente en MLflow para mantener un historial claro y detallado.

## Recursos Requeridos

Dado que el modelo LightGBM es relativamente liviano, los recursos necesarios son mínimos:

1. **Hardware**:
   - Servidor con al menos 1 CPU y 2 GB de RAM para entornos de desarrollo o pruebas.
   - Para producción, los recursos dependerán del tráfico esperado, pero se recomienda comenzar con 2 CPU y 4 GB de RAM.

2. **Software**:
   - Docker y Docker Compose para contenedorización.
   - Uvicorn como servidor ASGI para ejecutar la API.
   - Sistema operativo basado en Linux (por ejemplo, Ubuntu).

3. **Servicios en la Nube**:
   - Instancias de máquinas virtuales o servicios de contenedores.
   - Almacenamiento para bases de datos y backups si fueran necesarios en el futuro.

## Alternativas para Escalar

1. **Escalado Horizontal**:
   - Añadir más instancias de la API detrás de un balanceador de carga.
   - Utilizar Kubernetes para gestionar el escalado automático y la alta disponibilidad.

2. **Escalado Vertical**:
   - Aumentar los recursos de las instancias existentes (CPU, RAM).

3. **Optimización del Código**:
   - Mejorar la eficiencia del código para reducir el tiempo de respuesta y el uso de recursos.

Esta propuesta proporciona una base sólida para desplegar y escalar la API en un entorno real, asegurando su disponibilidad, rendimiento y seguridad.
