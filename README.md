# Candor

Weekly team feedback and retrospective tool.

## Accounts

There is no email backend anywhere in this project — no verification, no
password reset. A user who forgets their password is reset by an
administrator:

```bash
uv run manage.py changepassword <username>
```
