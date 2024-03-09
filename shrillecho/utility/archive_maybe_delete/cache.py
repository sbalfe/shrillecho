import os.path


class Cache:

    def __init__(self, folder, reader, writer):
        self._folder = folder
        self._reader = reader
        self._writer = writer
        self._setup_folder()
        self._root = f'cache/{self._folder}'

    def _setup_folder(self) -> None:
        if not os.path.exists(f'cache/{self._folder}'):
            os.makedirs(f'cache/{self._folder}')

    def fetch(self, file, *args) -> bool:
        check_path = os.path.join(f'{self._root}', file)
        if os.path.exists(check_path):
            with open(check_path, 'r') as cache:
                self._reader(cache, *args)
            return True
        with open(check_path, 'w') as cache:
            self._writer(cache, *args)
        return False

    def delete(self, file) -> None:
        check_path = os.path.join(f'{self._root}', file)
        if os.path.exists(check_path):
            os.remove(check_path)



