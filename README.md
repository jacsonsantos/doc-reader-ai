# Como usar API

Para iniciar a API:

```
cp .env.example .env
docker compose --env-file=.env up --build
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

# Autenticação

Instale a biblioteca `flask-jwt-extended`
Adicione a dependência no arquivo `requirements.txt`

```
flask-jwt-extended
```

**Inicializando o JWT**
No arquivo app.py, importe e configure o JWT:

```
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Inicialize o JWT
app.config['JWT_SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Substitua por uma chave secreta forte
jwt = JWTManager(app)
```

**Criando um endpoint para login e geração do token JWT**
Adicione um endpoint de login para gerar o token de acesso JWT. No exemplo abaixo, um token é criado se o nome de usuário e senha forem válidos:

```
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Substitua por sua lógica de autenticação (ex: verificar usuário e senha no banco de dados)
    if username != 'admin' or password != 'senha123':
        return jsonify({"msg": "Credenciais inválidas"}), 401

    # Crie um token de acesso (JWT)
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200
```

**Protegendo endpoints com o JWT**
Use o decorador @jwt_required() para proteger qualquer rota que precise de autenticação:

```
@app.route('/upload', methods=['POST'])
@jwt_required()  # Protege o endpoint
def upload_file():
    current_user = get_jwt_identity()  # Obtém o usuário autenticado
    # O restante do código permanece igual
```

Você também pode proteger o novo endpoint de URL da mesma maneira:

```
@app.route('/summarize-url', methods=['POST'])
@jwt_required()
def summarize_url():
    current_user = get_jwt_identity()
    # O restante do código permanece igual
```

**Como testar com curl**
Primeiro, faça login para obter o token JWT:

```
curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "senha123"}'
```

Isso retornará um token JWT como:

```
{
  "access_token": "seu_token_jwt_aqui"
}
```

Agora, use o token JWT para autenticar a requisição aos endpoints protegidos:

```
curl -X POST http://localhost:5000/upload \
     -H "Authorization: Bearer seu_token_jwt_aqui" \
     -F "file=@document.pdf"
```