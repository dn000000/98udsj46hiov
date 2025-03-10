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

# Получаем пользователя developer
my $dbh = Bugzilla->dbh;
my $user_id = $dbh->selectrow_array(
    "SELECT userid FROM profiles WHERE login_name = ?",
    undef, 'developer@example.com'
);

unless ($user_id) {
    die "Пользователь developer@example.com не найден!\n";
}

# Установка API ключа
my $api_key = "DevAPIKey12345";

# Проверка существующего ключа
my $existing = $dbh->selectrow_array(
    "SELECT COUNT(*) FROM profiles WHERE userid = ? AND api_key = ?",
    undef, $user_id, $api_key
);

if ($existing) {
    print "API ключ уже установлен\n";
} else {
    # Устанавливаем API ключ напрямую в таблицу profiles
    $dbh->do("UPDATE profiles SET api_key = ? WHERE userid = ?", 
            undef, $api_key, $user_id);
    print "API ключ установлен\n";
}

print "API_KEY=$api_key\n"; 