# Como usar API

Para iniciar a API:

```
docker compose up --build
```

Envie uma requisição POST para:

```
curl -X POST http://localhost:5000/upload \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"

```

Com um arquivo PDF ou DOCX e receba o resumo do conteúdo.

Envie uma url para resumo do conteúdo

```
curl -X POST http://localhost:5000/summarize-url \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/sample.pdf"}'
```


Resposta da API:

```
{
    "summary": "Este é o resumo do conteúdo do documento..."
}
```