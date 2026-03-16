FROM php:8.2-apache

# System dependencies for Moodle
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libzip-dev \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libxml2-dev \
    libssl-dev \
    libicu-dev \
    libxslt-dev \
    libonig-dev \
    wget \
    unzip \
    cron \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# PHP extensions required by Moodle
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) \
        pdo \
        pdo_pgsql \
        pgsql \
        zip \
        gd \
        intl \
        soap \
        xsl \
        opcache \
        mbstring \
        exif

# PHP configuration for Moodle
RUN { \
    echo "max_input_vars = 5000"; \
    echo "upload_max_filesize = 50M"; \
    echo "post_max_size = 50M"; \
    echo "memory_limit = 256M"; \
    echo "max_execution_time = 300"; \
    echo "opcache.enable = 1"; \
    echo "opcache.memory_consumption = 128"; \
} > /usr/local/etc/php/conf.d/moodle.ini

# Apache configuration
RUN a2enmod rewrite
RUN sed -i 's|DocumentRoot /var/www/html|DocumentRoot /var/www/html|' /etc/apache2/sites-available/000-default.conf \
    && sed -i 's|AllowOverride None|AllowOverride All|g' /etc/apache2/apache2.conf

# Entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

VOLUME ["/var/www/moodledata"]
EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
