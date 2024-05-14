
import string
import random


try:
    # Inspired by
    # https://github.com/django/django/blob/master/django/utils/crypto.py
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

def generate_random_string(length, using_digits=False, using_ascii_letters=False, using_punctuation=False):
    """
    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+50)^50) ~= 334 bit strength.
    """
    if not using_sysrandom:
        return None

    symbols = []
    if using_digits:
        symbols += string.digits
    if using_ascii_letters:
        symbols += string.ascii_letters
    if using_punctuation:
        all_punctuation = set(string.punctuation)
        # These symbols can cause issues in environment variables
        unsuitable = {"'", '"', "\\", "$"}
        suitable = all_punctuation.difference(unsuitable)
        symbols += "".join(suitable)
    return "".join([random.choice(symbols) for _ in range(length)])


def generate_random_user():
    return generate_random_string(length=32, using_ascii_letters=True)

def gen_django_secret_key():
    secret = generate_random_string(length=64, using_digits=True, using_ascii_letters=True, using_punctuation=True)
    print(f"DJANGO_SECRET_KEY={secret}")

def gen_django_admin_url():
    secret = generate_random_string(length=32, using_digits=True, using_ascii_letters=True)
    print(f"DJANGO_ADMIN_URL={secret}")

def gen_postgres_password():
    password = generate_random_string(length=64, using_digits=True, using_ascii_letters=True)
    print(f"POSTGRES_PASSWORD={password}")

def gen_postgres_user():
    user = generate_random_string(length=16, using_digits=True, using_ascii_letters=True)
    print(f"POSTGRES_USER={user}")

def gen_celery_flower_user():
    user = generate_random_user()
    print(f"CELERY_FLOWER_USER={user}")

def gen_celery_flower_password():
    password = generate_random_string(length=64, using_digits=True, using_ascii_letters=True)
    print(f"CELERY_FLOWER_PASSWORD={password}")

def gen_telegram_webhook_salt():
    salt = generate_random_string(length=16, using_digits=True, using_ascii_letters=True)
    print(f"TELEGRAM_WEBHOOK_SALT={salt}")


if __name__ == "__main__":
    gen_django_secret_key()
    gen_django_admin_url()
    gen_postgres_user()
    gen_postgres_password()
    gen_celery_flower_user()
    gen_celery_flower_password()
    gen_telegram_webhook_salt()
    