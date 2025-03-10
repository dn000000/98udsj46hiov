#!/usr/bin/perl
use strict;
use warnings;
use lib qw(/var/www/html/bugzilla);
use Bugzilla;
BEGIN { Bugzilla->extensions(); }
use Bugzilla::Constants;
use Bugzilla::User;
use Bugzilla::Config qw(:admin);
use Bugzilla::Group;

Bugzilla->usage_mode(USAGE_MODE_CMDLINE);

my $dbh = Bugzilla->dbh;

# Получаем пользователя developer
my $login = 'developer@example.com';
my $user_id = $dbh->selectrow_array(
    "SELECT userid FROM profiles WHERE login_name = ?",
    undef, $login
);

unless ($user_id) {
    die "Пользователь $login не найден!\n";
}

# Убедимся, что пользователь имеет права администратора
print "Предоставление прав администратора для $login...\n";
$dbh->do(
    "INSERT INTO user_group_map (user_id, group_id, isbless, grant_type) 
     SELECT ?, id, 0, 0 FROM groups WHERE name = 'admin' 
     AND NOT EXISTS (
        SELECT 1 FROM user_group_map 
        WHERE user_id = ? AND group_id = (SELECT id FROM groups WHERE name = 'admin')
     )",
    undef, $user_id, $user_id
);

print "Настройка прав завершена!\n"; 