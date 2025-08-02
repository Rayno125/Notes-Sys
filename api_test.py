import requests
import time

BASE_URL = 'http://localhost:5000'  # Адрес твоего локального сервера Flask

def test_registration_and_refresh(email, username, password):
    print('--- Регистрация пользователя ---')
    register_resp = requests.post(f'{BASE_URL}/register', json={
        'email': email,
        'username': username,
        'password': password
    })

    if register_resp.status_code not in (200, 201):
        print('Ошибка регистрации:', register_resp.json())
        return

    tokens = register_resp.json()
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    print('Регистрация успешна')
    print('Access Token:', access_token)
    print('Refresh Token:', refresh_token)

    print('\n--- Запрос заметок с access token ---')
    notes_resp = requests.get(f'{BASE_URL}/notes', headers={
        'Authorization': f'Bearer {access_token}'
    })

    print('Статус:', notes_resp.status_code)
    print('Данные:', notes_resp.json())

    print('\n--- Ждем пока access token истечет (примерно 65 секунд) ---')
    time.sleep(65)

    print('\n--- Запрос с истекшим токеном ---')
    expired_resp = requests.get(f'{BASE_URL}/notes', headers={
        'Authorization': f'Bearer {access_token}'
    })

    print('Статус:', expired_resp.status_code)  # Ожидается 401
    print('Ответ:', expired_resp.json())

    print('\n--- Обновление access token через refresh token ---')
    refresh_resp = requests.post(f'{BASE_URL}/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })

    if refresh_resp.status_code != 200:
        print('Ошибка обновления токена:', refresh_resp.json())
        return

    new_tokens = refresh_resp.json()
    new_access_token = new_tokens.get('access_token')
    print('Новый Access Token:', new_access_token)

    print('\n--- Запрос заметок с новым access token ---')
    new_notes_resp = requests.get(f'{BASE_URL}/notes', headers={
        'Authorization': f'Bearer {new_access_token}'
    })

    print('Статус:', new_notes_resp.status_code)
    print('Данные:', new_notes_resp.json())

if __name__ == '__main__':
    test_registration_and_refresh('user@example.com', 'testuser', 'pass123')
