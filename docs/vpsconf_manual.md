Pasos manuales a realizar

# Clonar repo

La instancia de EC2 fue creada ejecutando los pasos en la guías [Set up to use Amazon EC2 - Amazon Elastic Compute Cloud](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html#create-an-admin) y [Tutorial: Get started with Amazon EC2 Linux instances - Amazon Elastic Compute Cloud](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html)

Importante: en el security group se habilito trafico para http, https y ssh

# Setup DNS

Configurar record DNS de tipo A para que apunte a la ip publica de la instancia de EC2

Este paso es requerido para los certificados https

# Generar certificados https

Cargar variables de entorno necesarias para los comandos de abajo

```bash
load_env env/production/host
```

Si los contenedores están activos, hay que pararlos y después activarlos, para que ngnix pueda leer el nuevo certificado.

```bash
sudo --preserve-env docker compose stop
```

```bash
sudo --preserve-env docker compose --file "$REPODIR"/docker/production/docker-compose.yml run \
  --rm --interactive -p "80:80" \
  certbot certonly --standalone \
  -d tesis.diegojsanchez.com
```

El comando de arriba sirve también para renovar el certificado del dominio tesis.diegojsanchez.com. 

Alternativamente, si se quire renovar todos los certificados previamente obtenidos:

```bash
sudo --preserve-env docker compose --file "$REPODIR"/docker/production/docker-compose.yml run \
  --rm --interactive -p "80:80" \
  certbot renew --standalone
```

Para comprobar que el certificado se haya renovado nuevamente, el output del comando en `Expiry Date`, debería de decir `(VALID: 89 days)`

```
Found the following certs:
  Certificate Name:
    Expiry Date: 2025-03-03 10:49:46+00:00 (VALID: 89 days)
```

**Reiniciar nuevamente** los contenedores o el contenedor de nginx

```bash
sudo --preserve-env docker compose start
```


# Generar usuario superadmin
```bash
sudo --preserve-env docker compose run --rm --interactive --tty django \
  python manage.py createsuperuser
```

# Backups

```bash
cd tesis
sudo --preserve-env docker compose run --rm \
  --env "ENVIRONMENT=production" \
  --user "$(id -u)" \
  --volume "$HOME/fixture_backups:/app/fixture_backups" \
  --volume "./shscripts/:/app/shscripts/" \
  django python -m shscripts.backup
```
