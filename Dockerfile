FROM php:8.1-apache

# Abilita il modulo rewrite di Apache
RUN a2enmod rewrite

# Installa estensioni PHP necessarie
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Copia i file del progetto nella directory del server
COPY . /var/www/html/

# Imposta i permessi corretti
RUN chown -R www-data:www-data /var/www/html

# Esponi la porta 80
EXPOSE 80

# Configura Apache per usare index.php come file predefinito
RUN echo 'DirectoryIndex index.php' >> /etc/apache2/apache2.conf
