# diary-lab

DevOps-обвязка вокруг учебного ежедневника на **Flask** + **PostgreSQL**.  
Деплой на серверы — через **Ansible**.

Инфраструктуру VM/сети в Yandex Cloud поднимает отдельный репозиторий:  
[diary-lab-yc](https://github.com/KopteloF/diary-lab-yc) (OpenTofu).

---

## Схема

| Хост | Роль |
|------|------|
| **bastion** | пульт: сюда clone Ansible, отсюда `ansible-playbook` |
| **app** | Flask-приложение |
| **db** | PostgreSQL |

Типичная схема в YC (как сейчас на стенде):

- у **bastion** есть **публичный IP** — чтобы зайти по SSH с ноутбука;
- у **app** и **db** публичного IP нет — SSH только с bastion (или ProxyJump);
- выход в интернет у app/db (apt и т.п.) — через **NAT gateway** в VPC (это сервис Yandex Cloud, **не** «трафик через VM bastion»);
- белый IP bastion и NAT gateway — **разные** вещи: первое для входа к тебе на пульт, второе — калитка наружу для машин без белого IP.

---

## Что нужно до Ansible

1. Живые VM + сеть (в YC — из [diary-lab-yc](https://github.com/KopteloF/diary-lab-yc): `tofu init` → поправить `terraform.tfvars` → `tofu apply`).
2. С bastion должен быть SSH на app и db (ключ, user `ubuntu` на образах YC).
3. У app/db должен работать выход в интернет (иначе `apt` в playbook упадёт).

OpenTofu сейчас удобно гонять с ноутбука; позже можно с control host / CI — это отдельный шаг.

---

## Быстрый старт (на bastion)

```bash
git clone https://github.com/KopteloF/diary-lab.git
cd diary-lab/ansible

cp inventory/group_vars/all/secrets.yml.example inventory/group_vars/all/secrets.yml
nano inventory/group_vars/all/secrets.yml   # postgres_password

# inventory/hosts — IP app/db и ansible_user (на YC обычно ubuntu)
# (позже IP можно будет подставлять из tofu output автоматически)

ansible all -m ping
ansible-playbook site.yml

curl -s http://<APP_INTERNAL_IP>:8000/health
```

Ожидание health: что-то вроде `{"db":"ok","status":"ok"}`.

---

## Секреты

- Рабочий файл: `ansible/inventory/group_vars/all/secrets.yml`
- В git его **нет** (gitignore). В репо только `secrets.yml.example`.
- Не коммить пароли.

---

## Грабли (уже ловили)

1. **SSH user ≠ DB user.** На YC по SSH часто `ubuntu`, а роль в Postgres может остаться `roman` (`postgres_user`) — это разные этажи.
2. **`pg_conf_dir`** зависит от версии PostgreSQL на ОС (на Ubuntu 24.04 часто `/etc/postgresql/16/main`, не `18` с другой лабы).
3. Без интернета у app/db playbook падает на `apt` — нужен NAT gateway (или иной egress), одного белого IP на bastion мало.
4. Если сменился VPN/белый IP ноутбука — в OpenTofu обновить `my_ssh_cidr` в `terraform.tfvars` и `tofu apply` (правило SG), иначе SSH на bastion будет timeout.

---

## Структура

```text
ansible/
  site.yml
  inventory/
  roles/          # common, hardening, postgresql, app
  playbooks/      # bootstrap_ssh и др. (на YC ключи часто уже из cloud-init/tofu)
```

---

## Связанные репозитории

| Репо | Зачем |
|------|--------|
| [diary-lab](https://github.com/KopteloF/diary-lab) | Ansible: что поставить на VM |
| [diary-lab-yc](https://github.com/KopteloF/diary-lab-yc) | OpenTofu: какие VM/сети создать в YC |
