# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Yes     |

## Reporting a Vulnerability

If you discover a security vulnerability in Bookly, please **do not** open a public GitHub issue.

Instead, report it privately by:
- Opening a private security advisory on the [GitHub repository](https://github.com/ompandey07/HMS)
- Or contacting the maintainer directly through GitHub

We will respond as quickly as possible and work to resolve the issue promptly.

## Security Best Practices for Deployment

- Always set `DEBUG=False` in production
- Use a strong, unique `SECRET_KEY`
- Never commit your `.env` file
- Use environment variables for all sensitive credentials
- Keep Django and all dependencies up to date
- Use HTTPS in production
- Restrict `ALLOWED_HOSTS` to your actual domain