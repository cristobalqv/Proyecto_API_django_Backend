# Proyecto Sistema de Reportes PPDA - Entrega Parcial 1

## Desarrollo Back-End Python - Talento Futuro
### Grupo 2
- Alexis Quiroz
- Cristobal Quiroz
- Estefania Manriquez
- Oscar Torres
- Patricio Vera
- Rodrigo Araya
- Yerko Gallardo
- Victor Meza

### Gestión de Historias de Usuario
🌲 [Taiga](https://tree.taiga.io/project/pveraicind-clase4-sistemadereportesppda/backlog)

### Documentación
Una vez iniciado el servidor se puede acceder en el entorno local a:

📋 [Swagger](http://localhost:8000/api/schema/swagger-ui/)

## 1. Problemática
La Superintendencia del Medio Ambiente (SMA) necesita un sistema de reporte que permita a las entidades sectoriales registrar y reportar medidas de avance de los Planes de Prevención y Descontaminación Ambiental (PPDA). La SMA debe poder verificar el estado de avance de estos planes y controlar el cumplimiento de las normativas ambientales del país.

## 2. Objetivos
1. Desarrollar una API RESTful que permita a las entidades sectoriales enviar reportes sobre el estado de cumplimiento de medidas ambientales.
2. Estandarizar la recopilación de datos sobre el avance de los PPDA para facilitar a la SMA el acceso a estos reportes para fiscalizar y sancionar en caso de incumplimiento.


## 3. Stack Tecnológico
🐍 **Programación:** Python  
🎯 **Framework:** Django  
🗄️ **Base de datos:** PostgreSQL  
📜 **Documentación:** Swagger  


## 4. Modelos y su Interacción
El sistema maneja cuatro modelos principales:

1. **OrganismoSectorial:** Representa a cada entidad gubernamental encargada de fiscalizar el cumplimiento de normativas ambientales.
2. **Usuario:** Usuarios de los organismos sectoriales, con permisos específicos para subir reportes.
3. **Medidas:** Acciones ambientales específicas que las entidades deben cumplir y reportar.
4. **Reporte:**  Documentos subidos por los organismos sectoriales para evidenciar el cumplimiento de una medida.

### 4.1. OrganismoSectorial
Este modelo representa a los organismos encargados de fiscalizar normativas ambientales.
Cada organismo tiene un código único y puede (o no) estar asociado a una región.

Relación uno a muchos con Usuario: Un organismo puede tener varios usuarios que reportan en su nombre.
🔗 Relación clave:

Usuarios (Usuario.organismo_sectorial) pueden pertenecer a un solo organismo sectorial.
Medidas (Medidas.organismos_permitidos) define qué medidas pueden reportar los organismos.

### 4.2. Usuario
Extiende el modelo de usuario de Django (AbstractUser).

Puede estar vinculado a un OrganismoSectorial.
Puede o no estar autorizado para subir reportes (autorizado_para_reportes).
Usa groups y permissions para gestionar permisos (ejemplo: can_upload_reports).
🔗 Relación clave:

Relación uno a muchos con Reporte (Reporte.usuario): Cada usuario puede subir múltiples reportes.
Relación muchos a muchos con Group y Permission, lo que permite control de acceso granular.

### 4.3. Medidas
Define las acciones ambientales que deben cumplir los organismos sectoriales.

Cada medida tiene un nombre único, una descripción y una extensión de archivo permitida (ejemplo: PDF, Excel). Puede ser de cumplimiento obligatorio o no.

Relación muchos a muchos con OrganismoSectorial: Una medida puede ser exigida a múltiples organismos.

🔗 Relación clave:

- Relación uno a muchos con Reporte (Reporte.tipo_medida): Un reporte está asociado a una sola medida.
- Relación muchos a muchos con OrganismoSectorial: Define qué organismos pueden subir reportes para una medida específica.

📌 Ejemplo de interacción:

***Control de emisiones en termoeléctricas*** puede ser reportado solo por la Superintendencia de Electricidad y Combustibles.

### 4.4. Reporte
Representa los archivos subidos por los organismos sectoriales para evidenciar el cumplimiento de una medida.

Está asociado a un usuario y a una medida ambiental específica.
Tiene un estado de revisión (PENDIENTE, APROBADO, RECHAZADO).
La ruta de almacenamiento del archivo está personalizada según el organismo y la medida.

🔗 Relación clave:

- Usuario (Reporte.usuario) sube el reporte.
- Medida (Reporte.tipo_medida) define qué se está reportando.


## 5.  Validaciones:

- Solo usuarios autorizados pueden subir reportes.
- Solo pueden subir medidas que su organismo tenga permitidas.
- Validación del formato del archivo basado en la medida.

**Interacción entre los modelos 🔄**
- Un Usuario (de un OrganismoSectorial) inicia sesión y sube un Reporte asociado a una Medida.
- La Superintendencia revisa los reportes (PENDIENTE, APROBADO, RECHAZADO).

Si hay incumplimiento, puede solicitar más información o tomar medidas sancionatorias.

🛠 Ejemplo de flujo:

1. El Ministerio de Energía (OrganismoSectorial) debe reportar sobre el "Consumo de Energía en Termoeléctricas" (Medida).
2. Un usuario del ministerio sube un reporte en formato PDF.
3. La Superintendencia revisa el archivo y aprueba o rechaza el cumplimiento


# Instalación

Sigue estos pasos para configurar el entorno y ejecutar el proyecto en tu máquina local:

**1. Clonar el repositorio**

Clonar el repositorio desde GitHub  https://github.com/cristobalqv/Proyecto_API_django_Backend.git

**2. Crear ambiente virtual**

Clear ambiente virtual dentro de la carpeta del repositorio clonado y activa el entorno virtual.

**3. Instalar dependencias**

Instalar dependencias ejecutando el comando *pip install -r requirements.txt*

Este archivo incluye Django, Django REST Framework (DRF), psycopg2-binary, Spectacular, y django-environ.

**4. Crear Base de Datos**

Para crear la base de datos, crear un archivo llamado *.env*  dentro del directorio del proyecto,con la siguiente estructura:
```env
DB_NAME=proyecto
DB_USER=postgres
DB_PASSWORD="password"
DB_HOST=localhost
DB_PORT=5432
```
Esto permite configurar las credenciales de la base de datos de forma segura.

**5. Configurar la base de datos**

Crea una base de datos llamada ***proyecto*** en PostgreSQL. Luego, dentro de la base de datos, crea un esquema llamado ***app***.

**6. Aplicar migraciones**

Ejecuta los siguientes comandos para crear las tablas en la base de datos:
```env
python manage.py makemigrations*
python manage.py migrate*
```
**7. Crear superusuario**

Para acceder al panel de administración, crea un superusuario con:
```env
python manage.py createsuperuser*
```
**8. Iniciar el servidor**

Finalmente, ejecuta el servidor local con:
-*python manage.py runserver*
