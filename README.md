[//]: # (# TeleHealth)

[//]: # (-cài đặt python)

[//]: # (-cài đặt get-pip)

[//]: # (-cài đặt postgreSQL)

[//]: # (-cài đặt PgAdmin4 )

[//]: # (-setting bằng PgAdmin4 với dbname=TeleHealth, password=123456)

[//]: # (-pull code trên git về)

[//]: # (-pip install requirement.txt)

[//]: # (-python3 manage.py makemigrations)

[//]: # (-python3 manage.py migrate)

[//]: # (-tạo superuser)

[//]: # (-python3 manage.py createsuperuser)

[//]: # (-python3 manage.py shell)

[//]: # (+dùng truy vấn bằng shell và dùng hàm set_password để set password cho superuser)

[//]: # (-python3 manage.py runserver )

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Install Python3 at [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Install get-pip at [https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/)
3. Install PostgreSql at [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
4. Install PgAdmin4 at [https://www.pgadmin.org/download/](https://www.pgadmin.org/download/)
5. Setting using PgAdmin4 with the following information for example: dbname:TeleHealth, password: 12345678
6. Clone the repo
   ```sh
      git clone https://github.com/anhquoc1301/TeleHealth.git
   ```
7. Install Package
   ```sh
    pip install requirement.txt
   ```
8. Run makemigrations
   ```sh
    python3 manage.py makemigrations
   ```
9. Run migrate
   ```sh
    python3 manage.py migrate
   ```
10. Create Superuser
   ```sh
    python3 manage.py createsuperuser
   ```
- Following information:
  + Username: Admin
  + Password: 12345678

11. Setting Password for Superuser
    ```sh
     python3 manage.py shell
    ```
12. Run project
    ```sh
     python3 manage.py runserver
    ```