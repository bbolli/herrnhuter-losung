# How to convert a GIF into a `data:` URL

```bash
printf 'data:image/gif;base64,%s\n' "$(base64 <$1 | tr -d ' \t\r\n')"
```
