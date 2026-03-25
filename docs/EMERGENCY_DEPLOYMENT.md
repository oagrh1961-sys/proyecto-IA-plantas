# 🆘 Deployments de Emergencia y Troubleshooting

Procedimientos rápidos para resolver problemas en producción y hacer deployments manuales cuando el pipeline falla.

## 📋 Tabla de Contenidos

1. [Deployment Manual de Emergencia](#deployment-manual-de-emergencia)
2. [Troubleshooting de Problemas Comunes](#troubleshooting-de-problemas-comunes)
3. [Casos de Uso Específicos](#casos-de-uso-específicos)
4. [Comandos Útiles](#comandos-útiles)

---

## 🚨 Deployment Manual de Emergencia

### Situación: Pipeline Fallido, Necesitas Desplegar YA

#### Paso 1: Conectarse al Servidor

```bash
# Reemplazar con tu IP/dominio
ssh -i ~/.ssh/gitlab-runner.pem root@123.45.67.89

# O si tienes un .pem temporal
ssh -i ~/Downloads/key.pem root@servidor.com
```

#### Paso 2: Actualizar Código

```bash
# Ir a directorio de la app
cd /app/proyecto_deteccion_plantas

# Actualizar desde GitLab/GitHub
git fetch origin
git checkout main
git pull origin main
```

#### Paso 3: Actualizar Imagen Docker

```bash
# Opción A: Descargar imagen pre-construida
docker login  # Ingresar credenciales de Docker Hub
docker pull tu-usuario/proyecto-deteccion-plantas:latest

# Opción B: Construir localmente en el server (MÁS LENTO)
docker build -t proyecto-deteccion-plantas:latest .
```

#### Paso 4: Desplegar

```bash
# Detener contenedores antiguos
cd config
docker-compose down

# Iniciar nuevos contenedores
docker-compose up -d

# Verificar que están funcionando
sleep 10
docker-compose ps

# Ver logs
docker-compose logs
```

#### Paso 5: Verificar Funcionamiento

```bash
# Ver logs de la app
docker logs proyecto-app

# Probar conectividad (desde local)
curl http://tu-ip:8501

# Probar gRPC (desde dentro del server)
python -c "import socket; socket.create_connection(('localhost', 50052), timeout=2)"
```

**¡Listo!** Tu app está actualizada. ✅

---

## 🔧 Troubleshooting de Problemas Comunes

### ❌ Problema: "Connection refused" al acceder a http://ip:8501

**Causa probable:** Contenedor no está corriendo

```bash
# 1. Verificar estado
docker-compose -f config/docker-compose.yml ps

# 2. Si muestra "Exit", ver por qué falló
docker-compose logs app

# 3. Posibles soluciones:
# a) Error de puerto en uso
docker ps -a | grep 8501
docker kill <container-id>

# b) Falta de memoria/recursos
docker stats

# c) Error en configuración .env
cat config/.env | grep "GRPC"

# 4) Reiniciar
docker-compose restart
```

---

### ❌ Problema: Imagen Docker no se descarga

**Causa probable:** Credenciales de Docker Hub inválidas

```bash
# 1. Verificar login
docker login
# Username: tu-usuario
# Password: tu-token-docker-hub (NO password, token)
# Si falla: regenerar token en Docker Hub

# 2. Reintentar
docker pull tu-usuario/proyecto-deteccion-plantas:latest

# 3. Si sigue fallando, construir localmente
cd /app/proyecto_deteccion_plantas
docker build -t proyecto-deteccion-plantas:latest .
```

---

### ❌ Problema: Pipeline no se ejecuta después de push

**Causa probable:** Runner no está registrado o no está corriendo

```bash
# 1. Verificar runner desde el server
gitlab-runner verify
gitlab-runner list

# 2. Verificar que está activo
gitlab-runner status

# 3. Si no está:
systemctl start gitlab-runner
systemctl enable gitlab-runner

# 4. Ver logs
journalctl -u gitlab-runner -f

# 5. Si runner no aparece en GitLab:
# → Volver a registrar:
gitlab-runner register
```

---

### ❌ Problema: Servicio gRPC no responde

**Desde dentro del server:**

```bash
# 1. Verificar que el container está corriendo
docker-compose ps | grep server

# 2. Verificar puerto
docker port proyecto-server 50052

# 3. Probar conexión
python -c "
import socket
try:
    s = socket.create_connection(('localhost', 50052), timeout=2)
    print('✅ Servidor gRPC respondiendo')
    s.close()
except:
    print('❌ No responde')
"

# 4. Ver logs del server
docker logs -f proyecto-server

# 5. Reiniciar servidor
docker-compose restart server
```

---

### ❌ Problema: Modelo no se carga

**Síntoma:** Logs muestran "Model: FileNotFoundError"

```bash
# 1. Verificar que modelo existe
ls -lh /app/proyecto_deteccion_plantas/modelo_entrenado/

# 2. Si no existe, descargar
cd /app/proyecto_deteccion_plantas
python scripts/descargar_modelo.py

# 3. Verificar permisos
chmod -R 755 modelo_entrenado/

# 4. Reiniciar server
docker-compose restart server
```

---

### ❌ Problema: Out of Memory

**Síntoma:** Contenedores se cierren inesperadamente

```bash
# 1. Ver consumo
docker stats

# 2. Ver límites actuales en docker-compose.yml
cat config/docker-compose.yml | grep -A5 "mem_limit"

# 3. Reducir limites o actualizar droplet
# Opción A: Actualizar Droplet en DigitalOcean (resize)
# Opción B: Reducir capacidad en config

# 4. Cambiar docker-compose.yml
nano config/docker-compose.yml
# Agregar al service:
# mem_limit: 1g
# cpus: '1.0'

# 5. Reiniciar
docker-compose down
docker-compose up -d
```

---

## 📋 Casos de Uso Específicos

### Caso 1: Rollback a Versión Anterior

Necesitas volver a la versión anterior porque la nueva tiene bugs.

```bash
# 1. Ver versiones disponibles
docker images
# O en Docker Hub: https://hub.docker.com/r/tu-usuario/proyecto-deteccion-plantas

# 2. Detener actual
docker-compose -f config/docker-compose.yml down

# 3. Cambiar imagen en docker-compose.yml
nano config/docker-compose.yml
# Cambiar: image: tu-usuario/proyecto:latest
# A:       image: tu-usuario/proyecto:v1.0

# 4. Iniciar
docker-compose up -d

# 5. Verificar
docker-compose logs app | tail -20
```

---

### Caso 2: Actualizar Solo Configuración (.env)

No cambió el código, solo necesitas actualizar variables de entorno.

```bash
# 1. Editar .env
nano config/.env
# Cambiar valores necesarios

# 2. Reiniciar sin rebuild
docker-compose restart
# O más agresivo:
docker-compose down
docker-compose up -d
```

---

### Caso 3: Migración a Nuevo Droplet

Necesitas mover tu app a un servidor nuevo.

```bash
# EN SERVIDOR VIEJO:
# 1. Hacer backup de datos
docker cp proyecto-mlruns:/app/mlruns ./mlruns-backup
tar -czf proyecto-backup-$(date +%Y%m%d).tar.gz ./mlruns-backup ./config/.env

# 2. Descargar backup a local
scp -i key.pem root@ip-viejo:proyecto-backup*.tar.gz ./

# EN SERVIDOR NUEVO:
# 1. Instalar runner (ver paso anterior)
bash scripts/setup-gitlab-runner.sh

# 2. Registrar runner
gitlab-runner register

# 3. Descargar código
git clone https://gitlab.com/tu-usuario/proyecto-deteccion-plantas.git /app/proyecto_deteccion_plantas

# 4. Restaurar backup
scp -i key.pem proyecto-backup*.tar.gz root@ip-nuevo:
# Dentro del server:
tar -xzf proyecto-backup*.tar.gz
cp -r mlruns-backup/* config/

# 5. Actualizar DNS/IP en GitLab
# GitLab → Settings → CI/CD → Variables
# Cambiar SERVER_HOST a nueva IP

# 6. Deploy
docker-compose -f config/docker-compose.yml up -d
```

---

### Caso 4: Actualizar Sistema Operativo del Droplet

```bash
# ⚠️ PRECAUCIÓN: Esto causa downtime

# 1. Backup completo
ssh root@server "
  cd /app && \
  tar -czf proyecto-backup-completo.tar.gz proyecto_deteccion_plantas/
"

# 2. Actualizar en DigitalOcean panel
# DigitalOcean → Droplet → Power → Power Cycle
# O usar snapshots

# 3. Después de update, reconectar y:
cd /app/proyecto_deteccion_plantas
docker-compose up -d

# 4. Verificar
curl http://localhost:8501
```

---

## 🔍 Comandos Útiles

### Debugging General

```bash
# Ver estado completo de los contenedores
docker-compose -f config/docker-compose.yml ps -a

# Ver logs de un servicio específico
docker-compose logs server -f  # -f = follow (en vivo)
docker-compose logs app
docker-compose logs mlflow

# Ejecutar comando dentro de contenedor
docker exec -it proyecto-server bash
# Luego: python --version, ls, etc.

# Ver estadísticas de recursos
docker stats

# Ver inspección detallada de un contenedor
docker inspect proyecto-server | grep -E "State|Image|Ports"

# Limpiar recursos no usados
docker system prune -a
```

### Network Debugging

```bash
# Ver puertos en uso
netstat -tulpn | grep -E "8501|50052|5000|9000"
# O en MacOS:
lsof -i -P -n | grep LISTEN

# Probar conectividad a gRPC
python -c "
import socket
try:
    s = socket.create_connection(('localhost', 50052), timeout=2)
    print('✅ gRPC OK')
    s.close()
except Exception as e:
    print(f'❌ gRPC Fail: {e}')
"

# Probar HTTP
curl -I http://localhost:8501

# Ver tráfico en vivo (Linux)
tcpdump -i eth0 -nn port 50052
```

### Git Debugging

```bash
# Ver historial de deployments
git log --oneline | head -20

# Ver cambios entre versiones
git diff v1.0 v1.1

# Crear tag (versión) para marking deployments
git tag -a v1.1 -m "Versión 1.1 - Deploy a prod"
git push origin v1.1
```

---

## 🆘 Matriz de Decisión

```
¿Problema?
│
├─ Test falla en pipeline
│  └─ Revisar logs en GitLab
│     └─ make test localmente
│        
├─ Build Docker falla
│  └─ Revisar logs de build
│     └─ docker build . localmente
│
├─ Deploy falla
│  └─ SSH a servidor
│     └─ Ver docker-compose logs
│        └─ Hacer deployment manual
│
├─ App no responde en producción
│  └─ SSH a servidor
│     └─ docker-compose ps
│        └─ docker logs
│           └─ Reiniciar o rollback
│
└─ Datos perdidos/corrompidos
   └─ Restaurar desde backup
      └─ Verify integridad
         └─ Reiniciar servicios
```

---

## 📞 Soporte Rápido

| Problema | Comando | Documentación |
|----------|---------|---------------|
| Tests fallan | `make test` | [MAKEFILE_GUIDE](MAKEFILE_GUIDE.md) |
| Docker no inicia | `docker-compose logs` | [CI_CD_GITLAB_DIGITALOCEAN](CI_CD_GITLAB_DIGITALOCEAN.md) |
| Runner no registra | `gitlab-runner register` | scripts/setup-gitlab-runner.sh |
| Credenciales inválidas | `docker login` | [VARIABLES_SECRETOS](VARIABLES_SECRETOS.md) |
| gRPC no responde | `curl localhost:50052` | [Anterior doc] |

---

¡Espero no necesites estos comandos muy a menudo! 🤞

