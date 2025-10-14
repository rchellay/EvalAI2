import sqlite3

conn = sqlite3.connect('backend/eduapp.db')
cursor = conn.cursor()

# Ver usuarios admin y profesor
cursor.execute("SELECT id, username FROM users WHERE username = 'admin' OR username = 'profesor' ORDER BY id")
print('ID | Username')
print('-'*30)
for row in cursor.fetchall():
    print(f'{row[0]} | {row[1]}')

print('\n' + '='*50)
print('Asignando todos los grupos al usuario "admin"...')

# Obtener ID del admin
cursor.execute("SELECT id FROM users WHERE username = 'admin'")
admin_id = cursor.fetchone()[0]
print(f'Admin ID: {admin_id}')

# Actualizar todos los grupos para que pertenezcan al admin
cursor.execute("UPDATE groups SET teacher_id = ?", (admin_id,))
conn.commit()

print(f'\n✅ {cursor.rowcount} grupos actualizados')

# Verificar
cursor.execute('SELECT id, name, teacher_id FROM groups')
print('\n' + '='*50)
print('Grupos actualizados:')
print('ID | Nombre | Teacher ID')
print('-'*50)
for row in cursor.fetchall():
    print(f'{row[0]} | {row[1]} | {row[2]}')

conn.close()
print('\n✅ ¡Listo! Ahora todos los grupos pertenecen a admin')
