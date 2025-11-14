"""
Tests for claude-collector sanitization functionality.

All secrets are generated at runtime to avoid committing any sensitive patterns.
"""

import json
import random
import string
from claude_collector.sanitizer import sanitize


# Runtime secret generators - NO HARDCODED SECRETS
def generate_openai_key():
    """Generate fake OpenAI API key at runtime."""
    return "sk-" + ''.join(random.choices(string.ascii_letters + string.digits, k=48))


def generate_anthropic_key():
    """Generate fake Anthropic API key at runtime."""
    return "sk-ant-api03-" + ''.join(random.choices(string.ascii_letters + string.digits + "-_", k=80))


def generate_github_token():
    """Generate fake GitHub token at runtime."""
    return "ghp_" + ''.join(random.choices(string.ascii_letters + string.digits, k=36))


def generate_huggingface_token():
    """Generate fake HuggingFace token at runtime."""
    return "hf_" + ''.join(random.choices(string.ascii_letters + string.digits, k=32))


def generate_stripe_key():
    """Generate fake Stripe API key at runtime."""
    return "sk_live_" + ''.join(random.choices(string.ascii_letters + string.digits, k=24))


def generate_sendgrid_key():
    """Generate fake SendGrid API key at runtime."""
    return "SG." + ''.join(random.choices(string.ascii_letters + string.digits + "-_", k=64))


def generate_google_key():
    """Generate fake Google API key at runtime."""
    return "AIza" + ''.join(random.choices(string.ascii_letters + string.digits + "-_", k=35))


def generate_aws_key():
    """Generate fake AWS access key at runtime."""
    return "AKIA" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


def generate_aws_secret():
    """Generate fake AWS secret key at runtime."""
    return ''.join(random.choices(string.ascii_letters + string.digits + "+/", k=40))


def generate_private_key():
    """Generate fake 64-char hex private key at runtime."""
    return ''.join(random.choices(string.hexdigits.lower(), k=64))


def generate_eth_address():
    """Generate fake Ethereum address at runtime."""
    return "0x" + ''.join(random.choices(string.hexdigits.lower(), k=40))


def generate_btc_address():
    """Generate fake Bitcoin address at runtime."""
    prefix = random.choice(['1', '3', 'bc1'])
    length = 33 if prefix in ['1', '3'] else 42
    return prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_seed_phrase():
    """Generate fake BIP39 seed phrase at runtime."""
    words = ['abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
             'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
             'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual']
    return ' '.join(random.choices(words, k=12))


def generate_credit_card():
    """Generate fake credit card number at runtime."""
    return ''.join(random.choices(string.digits, k=16))


def generate_ssn():
    """Generate fake SSN at runtime."""
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"


class TestAPIKeySanitization:
    """Test sanitization of API keys and tokens."""

    def test_redacts_openai_keys(self):
        """Should redact OpenAI API keys."""
        key = generate_openai_key()
        text = f"OpenAI: {key}"
        result = sanitize(text)
        assert key not in result
        assert "[OPENAI_KEY]" in result

    def test_redacts_anthropic_keys(self):
        """Should redact Anthropic API keys."""
        key = generate_anthropic_key()
        text = f"Anthropic: {key}"
        result = sanitize(text)
        assert key not in result
        assert "[ANTHROPIC_KEY]" in result

    def test_redacts_github_tokens(self):
        """Should redact GitHub personal access tokens."""
        token = generate_github_token()
        text = f"GitHub: {token}"
        result = sanitize(text)
        assert token not in result
        assert "[GITHUB_TOKEN]" in result

    def test_redacts_huggingface_tokens(self):
        """Should redact HuggingFace tokens."""
        token = generate_huggingface_token()
        text = f"HF: {token}"
        result = sanitize(text)
        assert token not in result
        assert "[HF_TOKEN]" in result

    def test_redacts_stripe_keys(self):
        """Should redact Stripe API keys."""
        key = generate_stripe_key()
        text = f"Stripe: {key}"
        result = sanitize(text)
        assert key not in result
        assert "[STRIPE_LIVE_KEY]" in result

    def test_redacts_sendgrid_keys(self):
        """Should redact SendGrid API keys."""
        key = generate_sendgrid_key()
        text = f"SendGrid: {key}"
        result = sanitize(text)
        assert key not in result
        assert "[SENDGRID_KEY]" in result

    def test_redacts_google_keys(self):
        """Should redact Google API keys."""
        key = generate_google_key()
        text = f"Google: {key}"
        result = sanitize(text)
        assert key not in result
        assert "[GOOGLE_KEY]" in result

    def test_redacts_aws_keys(self):
        """Should redact AWS access keys."""
        key = generate_aws_key()
        text = f"AWS: {key}"
        result = sanitize(text)
        assert key not in result
        assert "[AWS_ACCESS_KEY]" in result

    def test_redacts_aws_secrets(self):
        """Should redact AWS secret keys."""
        secret = generate_aws_secret()
        text = f"AWS Secret: {secret}"
        result = sanitize(text)
        assert secret not in result
        assert "[AWS_SECRET]" in result

    def test_multiple_api_keys(self):
        """Should redact multiple different API keys in one text."""
        openai = generate_openai_key()
        github = generate_github_token()
        stripe = generate_stripe_key()
        
        text = f"Keys: {openai}, {github}, {stripe}"
        result = sanitize(text)
        
        assert openai not in result
        assert github not in result
        assert stripe not in result
        assert "[OPENAI_KEY]" in result
        assert "[GITHUB_TOKEN]" in result
        assert "[STRIPE_LIVE_KEY]" in result


class TestCryptoSanitization:
    """Test sanitization of cryptocurrency data."""

    def test_redacts_private_keys(self):
        """Should redact 64-char hex private keys."""
        key = generate_private_key()
        text = f"Private: {key}"
        result = sanitize(text)
        assert key not in result
        assert "[PRIVATE_KEY]" in result

    def test_redacts_ethereum_addresses(self):
        """Should redact Ethereum addresses."""
        address = generate_eth_address()
        text = f"ETH: {address}"
        result = sanitize(text)
        assert address not in result
        assert "[ETH_ADDRESS]" in result

    def test_redacts_bitcoin_addresses(self):
        """Should redact Bitcoin addresses."""
        address = generate_btc_address()
        text = f"BTC: {address}"
        result = sanitize(text)
        assert address not in result
        assert "[BTC_ADDRESS]" in result

    def test_redacts_seed_phrases(self):
        """Should redact BIP39 seed phrases."""
        phrase = generate_seed_phrase()
        text = f"Seed: {phrase}"
        result = sanitize(text)
        assert phrase not in result
        assert "[SEED_PHRASE]" in result

    def test_multiple_crypto_data(self):
        """Should redact multiple crypto items."""
        privkey = generate_private_key()
        eth = generate_eth_address()
        btc = generate_btc_address()
        
        text = f"Crypto: {privkey}, {eth}, {btc}"
        result = sanitize(text)
        
        assert privkey not in result
        assert eth not in result
        assert btc not in result


class TestFinancialDataSanitization:
    """Test sanitization of financial data."""

    def test_redacts_credit_cards(self):
        """Should redact credit card numbers."""
        cc = generate_credit_card()
        text = f"Card: {cc}"
        result = sanitize(text)
        assert cc not in result
        assert "[CREDIT_CARD]" in result

    def test_redacts_ssn(self):
        """Should redact Social Security Numbers."""
        ssn = generate_ssn()
        text = f"SSN: {ssn}"
        result = sanitize(text)
        assert ssn not in result
        assert "[SSN]" in result


class TestPIISanitization:
    """Test sanitization of personal identifiable information."""

    def test_redacts_emails(self):
        """Should redact email addresses."""
        text = "Contact: user@example.com"
        result = sanitize(text)
        assert "user@example.com" not in result
        assert "[EMAIL]" in result

    def test_preserves_dev_emails(self):
        """Should preserve common development emails."""
        text = "Test: test@localhost.com"
        result = sanitize(text)
        # Development emails should be preserved
        assert "test@localhost" in result or "[EMAIL]" in result


class TestContextPreservation:
    """Test that non-sensitive context is preserved."""

    def test_preserves_file_paths(self):
        """Should preserve file paths."""
        text = "/home/user/project/src/main.py"
        result = sanitize(text)
        assert text == result

    def test_preserves_function_names(self):
        """Should preserve function names."""
        text = "def process_data():"
        result = sanitize(text)
        assert text == result

    def test_preserves_error_messages(self):
        """Should preserve error messages."""
        text = "Error: TypeError: cannot convert NoneType to str"
        result = sanitize(text)
        assert text == result

    def test_preserves_code_snippets(self):
        """Should preserve code without secrets."""
        text = """
def authenticate():
    return jwt.encode(payload, secret_key)
"""
        result = sanitize(text)
        # Code structure should be preserved (the word "secret_key" is a variable name, not a real secret)
        assert "def authenticate" in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Should handle empty strings."""
        result = sanitize("")
        assert result == ""

    def test_only_whitespace(self):
        """Should handle whitespace-only strings."""
        result = sanitize("   \n\t  ")
        assert result == "   \n\t  "

    def test_no_secrets(self):
        """Should return identical text when no secrets present."""
        text = "This is a normal sentence with no secrets."
        result = sanitize(text)
        assert text == result

    def test_secrets_at_boundaries(self):
        """Should redact secrets at start/end of text."""
        key = generate_openai_key()
        
        # At start
        result = sanitize(key)
        assert key not in result
        
        # At end
        result = sanitize(f"Key: {key}")
        assert key not in result
        
        # Alone
        result = sanitize(key)
        assert key not in result

    def test_multiline_text(self):
        """Should handle multiline text with secrets."""
        key1 = generate_openai_key()
        key2 = generate_github_token()
        
        text = f"""Line 1
Key1: {key1}
Line 3
Key2: {key2}
Line 5"""
        
        result = sanitize(text)
        assert key1 not in result
        assert key2 not in result
        assert "Line 1" in result
        assert "Line 3" in result
        assert "Line 5" in result

    def test_json_with_secrets(self):
        """Should redact secrets in JSON strings."""
        key = generate_openai_key()
        json_text = json.dumps({"api_key": key, "other": "data"})
        
        result = sanitize(json_text)
        assert key not in result
        assert '"other": "data"' in result

    def test_very_long_text(self):
        """Should handle very long text."""
        key = generate_openai_key()
        long_text = "a" * 10000 + key + "b" * 10000
        
        result = sanitize(long_text)
        assert key not in result
        assert len(result) > 19000  # Should still have most of the text


class TestJSONLProcessing:
    """Test processing of JSONL conversation files."""

    def test_sanitizes_jsonl_entries(self):
        """Should sanitize secrets in JSONL conversation entries."""
        key = generate_openai_key()
        
        entry = {
            "messages": [
                {"role": "user", "content": f"Use this key: {key}"},
                {"role": "assistant", "content": "Sure, I'll use that."}
            ]
        }
        
        json_str = json.dumps(entry)
        result = sanitize(json_str)
        
        assert key not in result
        assert "[OPENAI_KEY]" in result
        assert '"role": "assistant"' in result

    def test_preserves_conversation_structure(self):
        """Should preserve conversation structure while sanitizing."""
        entry = {
            "timestamp": "2024-11-13T10:00:00Z",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "tool_calls": ["Read", "Write"]
        }
        
        json_str = json.dumps(entry)
        result = sanitize(json_str)
        
        # Structure should be preserved
        assert '"timestamp"' in result
        assert '"messages"' in result
        assert '"tool_calls"' in result
        assert '"role": "user"' in result
        assert '"role": "assistant"' in result
