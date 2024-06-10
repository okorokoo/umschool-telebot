from db import conn, cursor


def is_user_exists(user_id: int) -> bool:
    try:
        cursor.execute('''
            SELECT user_id
            FROM users
            WHERE user_id = ?
            ''', (user_id,))

        is_user_exists = cursor.fetchone()[0]

        return True

    except:
        return False


def store_user(user_id: int, user_first_name: str, user_last_name: str, user_password: str) -> bool:
    try:
        cursor.execute('''
                INSERT INTO users (user_id, first_name, last_name, password)
                VALUES (?, ?, ?, ?)
                ''', (user_id, user_first_name, user_last_name, user_password))

        conn.commit()

        return True

    except:
        return False


def get_hash(user_id: int) -> str:
    cursor.execute(f'''
                    SELECT password
                    FROM users
                    WHERE user_id = {user_id}
                    ''')

    password_hash = cursor.fetchone()[0]

    return password_hash


def set_user_logged_in(user_id: int):
    cursor.execute(f'''
                    UPDATE users
                    SET logged_in = 1
                    WHERE user_id = {user_id}
                    ''')
    conn.commit()


def set_user_logged_out(user_id: int):
    cursor.execute(f'''
                    UPDATE users
                    SET logged_in = 0
                    WHERE user_id = {user_id}
                    ''')
    conn.commit()


def add_score(user_id, subject_id, score):
    cursor.execute('''
                   INSERT INTO user_subjects (user_id, subject_id, score)
                   VALUES (?, ?, ?)''',
                   (user_id, subject_id, score))
    conn.commit()


def delete_score(user_id: int, subject_id: int):
    cursor.execute('DELETE FROM user_subjects WHERE subject_id = ? AND user_id = ?', (subject_id, user_id))
    conn.commit()


def view_all_scores(user_id):
    cursor.execute('''
        SELECT s.subject_name, us.score
        FROM user_subjects us
        JOIN subjects s ON us.subject_id = s.subject_id
        WHERE us.user_id = ?
    ''', (user_id,))

    scores = cursor.fetchall()

    return scores


def get_subject_id_by_name(subject_name: str) -> int:
    cursor.execute(f'''
        SELECT subject_id
        FROM subjects
        WHERE subject_name LIKE '{subject_name}'
    ''')

    subject_id = cursor.fetchone()[0]

    return subject_id
