"""Symmetric encryption helpers for secrets stored at rest.

Primarily used to encrypt OpenViking user credentials before persisting
them in the database. The Fernet key comes from ``settings.ov_credential_key``
(a urlsafe-base64-encoded 32-byte key, e.g. ``Fernet.generate_key()``).

The Fernet instance is built lazily on each call rather than cached so that a
settings reset in tests (``app.config._settings = None``) takes effect without
a process restart.
"""

from cryptography.fernet import Fernet, InvalidToken

class CredentialEncryptionError(RuntimeError):
    """Raised when secrets cannot be encrypted or decrypted.

    Covers a missing/invalid encryption key and corrupt ciphertext.
    """


class InvalidEncryptionKeyError(CredentialEncryptionError):
    """The *key* is missing or malformed — a deployment fault, not bad data.

    Distinct from corrupt ciphertext because the right reactions are
    opposite: an unreadable stored credential can be re-provisioned, but a
    bad key makes every credential unreadable and every new one unwritable,
    so re-provisioning would rotate upstream keys it can never store.
    """


def _fernet(key: str) -> Fernet:
    if not key:
        raise InvalidEncryptionKeyError(
            "Encryption key is not provided — cannot encrypt/decrypt. "
            "Generate a key with Fernet.generate_key()."
        )
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except (ValueError, TypeError) as exc:
        raise InvalidEncryptionKeyError(
            "Given key is not a valid Fernet key "
            "(expected urlsafe-base64-encoded 32 bytes)."
        ) from exc


def validate_key(key: str) -> None:
    """Raise ``InvalidEncryptionKeyError`` unless ``key`` is a usable Fernet key."""
    _fernet(key)


def encrypt_secret(plaintext: str, key: str) -> str:
    """Encrypt a secret and return a urlsafe Fernet token (str)."""
    return _fernet(key).encrypt(plaintext.encode()).decode()


def decrypt_secret(token: str, key: str) -> str:
    """Decrypt a Fernet token produced by :func:`encrypt_secret`."""
    try:
        return _fernet(key).decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise CredentialEncryptionError(
            "Stored credential could not be decrypted — the ciphertext is corrupt "
            "or the encryption key has changed."
        ) from exc
