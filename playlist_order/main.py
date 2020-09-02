import enum

import inquirer
from pydantic import ValidationError

from deezer.auth import DeezerAuthenticator
from deezer.client import DeezerClient
from deezer.settings import DeezerSettings


class DeezerOptions(str, enum.Enum):
    AUTH = 'Авторизация'
    USER_INFO = 'Информация о пользователе'
    PLAYLIST_INFO = 'Информация о плейлисте'


def main():
    try:
        settings = DeezerSettings()
    except ValidationError:
        settings = DeezerSettings(_env_file='.env')

    deezer_auth = DeezerAuthenticator(settings)
    client = DeezerClient(settings=settings, authenticator=deezer_auth)

    mapping = {
        DeezerOptions.AUTH: lambda: deezer_auth.token,
        DeezerOptions.USER_INFO: deezer_auth.user_info,
        DeezerOptions.PLAYLIST_INFO: lambda: playlist_info(client),
    }

    while True:
        option = inquirer.list_input(message='Deezer', choices=list(DeezerOptions) + [None])
        if not option:
            return

        func = mapping[option]
        print(func())


def playlist_info(client: DeezerClient):
    playlists = client.get_playlist_list()
    target = inquirer.list_input('Which one?', choices=[p.title for p in playlists])
    client.get_playlist_info(target)


if __name__ == '__main__':
    main()
