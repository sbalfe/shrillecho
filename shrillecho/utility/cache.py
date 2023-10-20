import os.path


class Cache:

    def __init__(self, folder, reader, writer):
        self.__folder = folder
        self.__reader = reader
        self.__writer = writer
        self.__setup_folder()
        self.__root = f'cache/{self.__folder}'

    def __setup_folder(self) -> None:
        if not os.path.exists(f'cache/{self.__folder}'):
            os.makedirs(f'cache/{self.__folder}')

    def fetch(self, file, *args) -> bool:
        check_path = os.path.join(f'{self.__root}', file)
        if os.path.exists(check_path):
            with open(check_path, 'r') as cache:
                self.__reader(cache, *args)
            return True
        with open(check_path, 'w') as cache:
            self.__writer(cache, *args)
        return False

    def delete(self, file) -> None:
        check_path = os.path.join(f'{self.__root}', file)
        if os.path.exists(check_path):
            os.remove(check_path)



