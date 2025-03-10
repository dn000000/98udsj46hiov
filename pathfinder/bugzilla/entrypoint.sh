#!/bin/bash

# Установка таймаута для ожидания базы данных (300 секунд = 5 минут)
TIMEOUT=300
COUNTER=0

echo "Ждем готовности базы данных..."
while ! mysql -h db -u root -p${DB_ROOT_PASSWORD} -e "SELECT 1" >/dev/null 2>&1; do
  sleep 5
  COUNTER=$((COUNTER + 5))
  echo "Ожидание базы данных... ${COUNTER}/${TIMEOUT} секунд"
  
  if [ $COUNTER -ge $TIMEOUT ]; then
    echo "Ошибка: истекло время ожидания готовности базы данных!"
    exit 1
  fi
done

echo "База данных готова, продолжаем настройку"

# Создание базы данных и пользователя, если они не существуют
mysql -h db -u root -p${DB_ROOT_PASSWORD} <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME};
CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'%';
FLUSH PRIVILEGES;
EOF

cd /var/www/html/bugzilla

# Создание каталога data если его нет
mkdir -p data
chmod 755 data

# Создание правильного localconfig с поддержкой REST API
cat > localconfig <<EOF
\$webservergroup = 'apache';
\$db_driver = 'mysql';
\$db_host = 'db';
\$db_name = '${DB_NAME}';
\$db_user = '${DB_USER}';
\$db_pass = '${DB_PASS}';
\$create_htaccess = 0;

# Настройки для REST API
\$webservice_email_filter = 0;
\$webservice_default_text_field_size = 255;
\$webservice_force_rest = 0;

# Разрешить вход без шифрования
\$ssl_redirect = 0;

# Включить поддержку REST API
\$urlbase = 'http://localhost/';
\$use_suexec = 0;
\$debug = 1;
\$auth_delegation = 0;
EOF

echo "Установка правильных прав доступа..."
chown -R apache:apache .

echo "Запуск checksetup.pl для инициализации..."
./checksetup.pl

# Если params.json еще не создан, запустим с ответами для создания администратора
if [ ! -f "./data/params.json" ]; then
  echo "Создание файла params.json и администратора..."
  
  cat > ./answers.txt <<EOF
\$answer{'ADMIN_EMAIL'} = 'admin@example.com';
\$answer{'ADMIN_PASSWORD'} = 'admin123';
\$answer{'ADMIN_REALNAME'} = 'Administrator';
\$answer{'urlbase'} = 'http://localhost/';
\$answer{'create_htaccess'} = 0;
EOF

  ./checksetup.pl ./answers.txt
  
  if [ ! -f "./data/params.json" ]; then
    echo "ОШИБКА: Файл params.json не был создан!"
    # Создаем базовый params.json вручную
    echo "{}" > ./data/params.json
    chown apache:apache ./data/params.json
    chmod 644 ./data/params.json
  fi
fi

# Перед настройкой REST API устанавливаем необходимые модули
echo "Установка необходимых Perl модулей для REST API..."
./install-module.pl JSON::RPC Test::Taint JSON::XS

# Настройка REST API
echo "Настройка REST API для Bugzilla 5.0.4..."
cat > /tmp/enable_rest.pl <<EOF
#!/usr/bin/perl
use strict;
use warnings;
use lib qw(/var/www/html/bugzilla);
use Bugzilla;
BEGIN { Bugzilla->extensions(); }
use Bugzilla::Constants;
use Bugzilla::Util;
use Bugzilla::Config qw(:admin);

# Настройки для Bugzilla 5.0.4
Bugzilla->usage_mode(USAGE_MODE_CMDLINE);

# REST API настройки
SetParam('urlbase', 'http://localhost/');
SetParam('cookiepath', '/');
SetParam('maintenance', 0);

# Отключение проверки логина для REST API
SetParam('requirelogin', 0);
SetParam('webservice_email_filter', 0);

# WebService настройки
SetParam('debug_group', 'admin');
SetParam('editmilestones', 0);
SetParam('insidergroup', '');

write_params();
print "REST API настройки успешно применены\n";
EOF

chmod +x /tmp/enable_rest.pl
perl /tmp/enable_rest.pl

# Создаем правильный .htaccess для rest API
cat > /var/www/html/bugzilla/rest/.htaccess <<EOF
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /bugzilla/rest.cgi/$1 [L,QSA]

# Используем CGI для обработки REST запросов
AddHandler cgi-script .cgi

# Важные настройки для разрешения BasicAuth
RewriteCond %{HTTP:Authorization} ^(.+)
RewriteRule .* - [E=HTTP_AUTHORIZATION:%1]
EOF

# Устанавливаем права на .htaccess
chmod 644 /var/www/html/bugzilla/.htaccess
chown apache:apache /var/www/html/bugzilla/.htaccess

# После всех настроек проверяем, что mod_rewrite активен
echo "Проверка активации mod_rewrite..."
if [ -f /etc/httpd/conf.modules.d/00-base.conf ]; then
    grep -q "mod_rewrite" /etc/httpd/conf.modules.d/00-base.conf || echo "LoadModule rewrite_module modules/mod_rewrite.so" >> /etc/httpd/conf.modules.d/00-base.conf
fi

# Создание дополнительных пользователей через SQL и скрипт генерации хешей
echo "Создание дополнительных пользователей через SQL..."

# Получаем полный путь к Perl модулю Bugzilla::Util, чтобы использовать его для генерации хешей
PERL_MODULE_PATH=$(find /var/www/html/bugzilla -name "Util.pm" | grep Bugzilla)
PERL_LIB_DIR=$(dirname $(dirname $PERL_MODULE_PATH))

# Создаём скрипт для генерации хешей паролей в формате Bugzilla
cat > /tmp/generate_password.pl <<EOF
#!/usr/bin/perl
use lib '/var/www/html/bugzilla';
use Bugzilla::Util;

# Создаем хеши для наших паролей (используем правильную функцию)
my \$dev_hash = bz_crypt('developer123');
my \$tester_hash = bz_crypt('tester123');
my \$user_hash = bz_crypt('user123');

# Выводим хеши для использования в SQL-запросе
print "DEV_HASH:\$dev_hash\n";
print "TESTER_HASH:\$tester_hash\n";
print "USER_HASH:\$user_hash\n";
EOF

chmod +x /tmp/generate_password.pl

# Запускаем скрипт для получения хешей паролей
echo "Генерация хешей паролей..."
PASSWORDS=$(perl /tmp/generate_password.pl)
DEV_HASH=$(echo "$PASSWORDS" | grep "DEV_HASH:" | cut -d':' -f2)
TESTER_HASH=$(echo "$PASSWORDS" | grep "TESTER_HASH:" | cut -d':' -f2)
USER_HASH=$(echo "$PASSWORDS" | grep "USER_HASH:" | cut -d':' -f2)

echo "Хеши паролей сгенерированы"

# Вставляем пользователей в базу данных
mysql -h db -u ${DB_USER} -p${DB_PASS} ${DB_NAME} <<EOF
-- Проверяем, существуют ли пользователи
SET @dev_exists = (SELECT COUNT(*) FROM profiles WHERE login_name = 'developer@example.com');
SET @test_exists = (SELECT COUNT(*) FROM profiles WHERE login_name = 'tester@example.com');
SET @user_exists = (SELECT COUNT(*) FROM profiles WHERE login_name = 'user@example.com');

-- Вставляем пользователя developer, если он не существует
INSERT INTO profiles 
(login_name, cryptpassword, realname, disabledtext, mybugslink, extern_id, is_enabled)
SELECT 
'developer@example.com', '$DEV_HASH', 'Developer', '', 1, NULL, 1
WHERE @dev_exists = 0;

-- Вставляем пользователя tester, если он не существует
INSERT INTO profiles 
(login_name, cryptpassword, realname, disabledtext, mybugslink, extern_id, is_enabled)
SELECT 
'tester@example.com', '$TESTER_HASH', 'Tester', '', 1, NULL, 1
WHERE @test_exists = 0;

-- Вставляем пользователя user, если он не существует
INSERT INTO profiles 
(login_name, cryptpassword, realname, disabledtext, mybugslink, extern_id, is_enabled)
SELECT 
'user@example.com', '$USER_HASH', 'User', '', 1, NULL, 1
WHERE @user_exists = 0;

-- Добавляем пользователей в группу canconfirm (исправлено поле group_id на id)
INSERT IGNORE INTO user_group_map (user_id, group_id, isbless, grant_type)
SELECT 
    p.userid, g.id, 0, 0
FROM 
    profiles p, groups g
WHERE 
    p.login_name IN ('developer@example.com', 'tester@example.com') 
    AND g.name = 'canconfirm';

-- Добавляем разработчика в группу editbugs
INSERT IGNORE INTO user_group_map (user_id, group_id, isbless, grant_type)
SELECT 
    p.userid, g.id, 0, 0
FROM 
    profiles p, groups g
WHERE 
    p.login_name = 'developer@example.com' 
    AND g.name = 'editbugs';
EOF

# Создаем проект PathFinder
echo "Создание проекта PathFinder..."
mysql -h db -u ${DB_USER} -p${DB_PASS} ${DB_NAME} <<EOF
-- Получаем ID администратора
SET @admin_id = (SELECT userid FROM profiles WHERE login_name = 'admin@example.com');

-- Проверка существования проекта
SET @pathfinder_exists = (SELECT COUNT(*) FROM products WHERE name = 'PathFinder');

-- Если проект не существует, создаем его
INSERT INTO products (name, description, isactive, defaultmilestone)
SELECT 'PathFinder', 'PathFinder Project - Maze solving algorithms', 1, 'MVP'
WHERE @pathfinder_exists = 0;

-- Получаем ID проекта
SET @product_id = (SELECT id FROM products WHERE name = 'PathFinder');

-- Создаем компоненты
SET @core_exists = (SELECT COUNT(*) FROM components WHERE name = 'Core' AND product_id = @product_id);
SET @ui_exists = (SELECT COUNT(*) FROM components WHERE name = 'UI' AND product_id = @product_id);
SET @doc_exists = (SELECT COUNT(*) FROM components WHERE name = 'Documentation' AND product_id = @product_id);

INSERT INTO components (name, product_id, description, initialowner)
SELECT 'Core', @product_id, 'Core functionality of the application', @admin_id
WHERE @core_exists = 0;

INSERT INTO components (name, product_id, description, initialowner)
SELECT 'UI', @product_id, 'User interface components', @admin_id
WHERE @ui_exists = 0;

INSERT INTO components (name, product_id, description, initialowner)
SELECT 'Documentation', @product_id, 'Project documentation', @admin_id
WHERE @doc_exists = 0;

-- Создаем версии
SET @v10_exists = (SELECT COUNT(*) FROM versions WHERE value = '1.0' AND product_id = @product_id);
SET @v11_exists = (SELECT COUNT(*) FROM versions WHERE value = '1.1' AND product_id = @product_id);
SET @v20_exists = (SELECT COUNT(*) FROM versions WHERE value = '2.0' AND product_id = @product_id);

INSERT INTO versions (value, product_id)
SELECT '1.0', @product_id
WHERE @v10_exists = 0;

INSERT INTO versions (value, product_id)
SELECT '1.1', @product_id
WHERE @v11_exists = 0;

INSERT INTO versions (value, product_id)
SELECT '2.0', @product_id
WHERE @v20_exists = 0;

-- Создаем вехи (milestones)
SET @mvp_exists = (SELECT COUNT(*) FROM milestones WHERE value = 'MVP' AND product_id = @product_id);
SET @beta_exists = (SELECT COUNT(*) FROM milestones WHERE value = 'Beta' AND product_id = @product_id);
SET @release_exists = (SELECT COUNT(*) FROM milestones WHERE value = 'Release' AND product_id = @product_id);

INSERT INTO milestones (product_id, value, sortkey, isactive)
SELECT @product_id, 'MVP', 0, 1
WHERE @mvp_exists = 0;

INSERT INTO milestones (product_id, value, sortkey, isactive)
SELECT @product_id, 'Beta', 1, 1
WHERE @beta_exists = 0;

INSERT INTO milestones (product_id, value, sortkey, isactive)
SELECT @product_id, 'Release', 2, 1
WHERE @release_exists = 0;

-- Проверка доступа к продукту
INSERT IGNORE INTO group_control_map (group_id, product_id, entry, membercontrol, othercontrol, canedit)
SELECT group_id, @product_id, 0, 0, 0, 0 FROM groups WHERE name = 'editbugs';

INSERT IGNORE INTO group_control_map (group_id, product_id, entry, membercontrol, othercontrol, canedit)
SELECT group_id, @product_id, 0, 0, 0, 0 FROM groups WHERE name = 'canconfirm';

-- Создаем демо-ошибки
-- Получаем ID компонентов
SET @core_id = (SELECT id FROM components WHERE name = 'Core' AND product_id = @product_id);
SET @ui_id = (SELECT id FROM components WHERE name = 'UI' AND product_id = @product_id);

-- Проверяем и добавляем ошибки
SET @bug1_exists = (SELECT COUNT(*) FROM bugs WHERE short_desc = 'BFS algorithm fails to find path in some cases');
SET @bug2_exists = (SELECT COUNT(*) FROM bugs WHERE short_desc = 'Path visualization incorrect');
SET @bug3_exists = (SELECT COUNT(*) FROM bugs WHERE short_desc = 'Add support for A* algorithm');
SET @bug4_exists = (SELECT COUNT(*) FROM bugs WHERE short_desc = 'Application crashes with empty maze');

INSERT INTO bugs (
    bug_status, resolution, short_desc, 
    product_id, component_id, version, 
    op_sys, rep_platform, reporter, 
    assigned_to, bug_severity, priority, 
    creation_ts, delta_ts
)
SELECT 
    'NEW', '', 'BFS algorithm fails to find path in some cases', 
    @product_id, @core_id, '1.0', 
    'All', 'All', @admin_id, 
    @admin_id, 'major', 'High', 
    NOW(), NOW()
WHERE @bug1_exists = 0;

INSERT INTO bugs (
    bug_status, resolution, short_desc, 
    product_id, component_id, version, 
    op_sys, rep_platform, reporter, 
    assigned_to, bug_severity, priority, 
    creation_ts, delta_ts
)
SELECT 
    'NEW', '', 'Path visualization incorrect', 
    @product_id, @ui_id, '1.0', 
    'All', 'All', @admin_id, 
    @admin_id, 'normal', 'Medium', 
    NOW(), NOW()
WHERE @bug2_exists = 0;

INSERT INTO bugs (
    bug_status, resolution, short_desc, 
    product_id, component_id, version, 
    op_sys, rep_platform, reporter, 
    assigned_to, bug_severity, priority, 
    creation_ts, delta_ts
)
SELECT 
    'NEW', '', 'Add support for A* algorithm', 
    @product_id, @core_id, '1.0', 
    'All', 'All', @admin_id, 
    @admin_id, 'enhancement', 'Low', 
    NOW(), NOW()
WHERE @bug3_exists = 0;

INSERT INTO bugs (
    bug_status, resolution, short_desc, 
    product_id, component_id, version, 
    op_sys, rep_platform, reporter, 
    assigned_to, bug_severity, priority, 
    creation_ts, delta_ts
)
SELECT 
    'NEW', '', 'Application crashes with empty maze', 
    @product_id, @core_id, '1.0', 
    'All', 'All', @admin_id, 
    @admin_id, 'critical', 'Highest', 
    NOW(), NOW()
WHERE @bug4_exists = 0;
EOF

# Проверка результата
echo "Проверка создания params.json..."
if [ -f "./data/params.json" ]; then
  echo "Файл params.json успешно создан."
else
  echo "ОШИБКА: Не удалось создать params.json!"
fi

# Убедимся, что проект PathFinder существует
echo "Проверка создания проекта PathFinder..."
if mysql -h db -u ${DB_USER} -p${DB_PASS} ${DB_NAME} -e "SELECT name FROM products WHERE name='PathFinder'" | grep -q "PathFinder"; then
  echo "Проект PathFinder успешно создан."
else
  echo "ОШИБКА: Проект PathFinder не создан!"
fi

# Проверка наличия пользователей
echo "Проверка создания пользователей..."
mysql -h db -u ${DB_USER} -p${DB_PASS} ${DB_NAME} -e "SELECT login_name FROM profiles WHERE login_name IN ('developer@example.com', 'tester@example.com', 'user@example.com')"

# Обновляем кэш и перезагружаем Bugzilla
echo "Перезагрузка Bugzilla..."
touch data/params

# Создаем API ключ (это должно быть перед запуском Apache!)
echo "Настройка API ключа напрямую в базе данных..."
cat > /tmp/setup_api_key.pl <<'EOL'
#!/usr/bin/perl
use strict;
use warnings;
use lib qw(/var/www/html/bugzilla);
use Bugzilla;
BEGIN { Bugzilla->extensions(); }
use Bugzilla::Constants;
use Bugzilla::User;
use Bugzilla::Config qw(:admin);

Bugzilla->usage_mode(USAGE_MODE_CMDLINE);

# Получаем пользователя developer - используем экранирование для @
my $dbh = Bugzilla->dbh;
my $login_name = 'developer@example.com';

my $user_id = $dbh->selectrow_array(
    "SELECT userid FROM profiles WHERE login_name = ?",
    undef, $login_name
);

unless ($user_id) {
    die "Пользователь $login_name не найден!\n";
}

# Проверяем структуру таблицы profiles
my $has_api_key_column = 0;
my $columns = $dbh->selectcol_arrayref("SHOW COLUMNS FROM profiles");
foreach my $column (@$columns) {
    if ($column eq 'api_key') {
        $has_api_key_column = 1;
        last;
    }
}

# Если колонки api_key нет, добавляем её
unless ($has_api_key_column) {
    print "Добавляем колонку api_key в таблицу profiles...\n";
    $dbh->do("ALTER TABLE profiles ADD COLUMN api_key VARCHAR(40)");
}

# Установка API ключа
my $api_key = "DevAPIKey12345";

# Устанавливаем API ключ напрямую в таблицу profiles
$dbh->do("UPDATE profiles SET api_key = ? WHERE userid = ?", 
        undef, $api_key, $user_id);

print "API ключ установлен напрямую: $api_key\n";

# Проверка установки
my $check = $dbh->selectrow_array(
    "SELECT api_key FROM profiles WHERE userid = ?",
    undef, $user_id
);

if ($check eq $api_key) {
    print "API ключ успешно установлен и проверен\n";
} else {
    print "ОШИБКА: API ключ не установлен\n";
}
EOL

chmod +x /tmp/setup_api_key.pl
perl /tmp/setup_api_key.pl

# Записываем API ключ в файл
echo "DevAPIKey12345" > /var/www/html/bugzilla/api_key.txt
chmod 644 /var/www/html/bugzilla/api_key.txt
chown apache:apache /var/www/html/bugzilla/api_key.txt

echo "API ключ успешно создан и сохранен в файле api_key.txt: DevAPIKey12345"

# Обновление настроек для включения API ключей
cat > /tmp/enable_api_keys.pl <<EOF
#!/usr/bin/perl
use strict;
use warnings;
use lib qw(/var/www/html/bugzilla);
use Bugzilla;
BEGIN { Bugzilla->extensions(); }
use Bugzilla::Constants;
use Bugzilla::Util;
use Bugzilla::Config qw(:admin);

Bugzilla->usage_mode(USAGE_MODE_CMDLINE);

# Настройки API
SetParam('webservice_error_mask', 0);  # Не скрывать ошибки API
SetParam('user_info_class', 'CGI,Env,Cookie');  # Включаем получение информации о пользователе

# Сохраняем параметры
write_params();
print "Настройки API ключей включены\n";
EOF

chmod +x /tmp/enable_api_keys.pl
perl /tmp/enable_api_keys.pl

# Запуск Apache в фоновом режиме
exec httpd -D FOREGROUND 