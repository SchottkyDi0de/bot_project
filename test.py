class User:
    name: str = 'Jonson'
    age: int = 18
    email: str = 'qo8oH@example.com'

    def del_user_data(self):
        del self.name
        del self.age
        del self.email

    def check_user_data(self) -> bool:
        print(self.name)
        print(self.age)
        print(self.email)
        return True

def checl_user(user):
    return user.check_user_data()


def list_finc() -> list[int]:
    return [1, 2, 3]

some_val = list_finc()

for i in some_val:
    i.