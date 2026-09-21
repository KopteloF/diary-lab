# diary-lab

Ansible-деплой учебного ежедневника: Flask + PostgreSQL на трёх машинах.

Инфраструктура VM и сети в Yandex Cloud: отдельный репозиторий
[diary-lab-yc](https://github.com/KopteloF/diary-lab-yc) (OpenTofu).

## Роли хостов

| Хост | Назначение |
|------|------------|
| bastion | точка входа: отсюда SSH и `ansible-playbook` |
| app | Flask-приложение (systemd), порт 8000 |
| db | PostgreSQL |

В Yandex Cloud обычно так:

- у bastion есть публичный IP для SSH с ноутбука
- у app и db публичного IP нет; SSH только через bastion (ProxyJump)
- интернет для app/db (apt и т.п.) идёт через NAT gateway VPC. Это не «трафик через VM bastion»
- белый IP bastion и NAT gateway решают разные задачи

## Перед Ansible

1. Подняты VM и сеть ([diary-lab-yc](https://github.com/KopteloF/diary-lab-yc): `tofu init`, правки `terraform.tfvars`, `tofu apply`).
2. С bastion есть SSH на app и db (на образах YC часто пользователь `ubuntu`).
3. У app/db есть egress в интернет, иначе `apt` в playbook упадёт.

## Быстрый старт (с bastion)

```bash
git clone https://github.com/KopteloF/diary-lab.git
cd diary-lab/ansible

cp inventory/group_vars/all/secrets.yml.example inventory/group_vars/all/secrets.yml
# задать postgres_password в secrets.yml

# inventory/hosts: IP app/db и ansible_user
ansible all -m ping
ansible-playbook site.yml

curl -s http://<APP_INTERNAL_IP>:8000/health
```

Ожидание: JSON вида `{"db":"ok","status":"ok"}`.

## Секреты

Рабочий файл: `ansible/inventory/group_vars/all/secrets.yml`  
В git не коммитится. В репозитории только `secrets.yml.example`.

## Типовые грабли

1. SSH-пользователь ОС и роль PostgreSQL это разные вещи (например `ubuntu` и `roman`).
2. Путь конфигов Postgres зависит от версии пакета на ОС (на Ubuntu 24.04 часто 16-й major).
3. Без NAT gateway у app/db playbook падает на установке пакетов.
4. Смена VPN/белого IP ноутбука: обновить `my_ssh_cidr` в OpenTofu и применить SG.

## Структура

```text
ansible/
  ansible.cfg
  site.yml
  inventory/
  roles/
```

## Связка с OpenTofu

После `tofu apply` внутренние IP и публичный IP bastion можно подставить в inventory и ssh config скриптом из diary-lab-yc (см. README там). Playbook сам облако не создаёт.
