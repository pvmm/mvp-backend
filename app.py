from flask import Flask, request
from flask_cors import CORS
#from flask_swagger import swagger
from flask import jsonify
from flasgger import Swagger

import sqlite3


app = Flask(__name__)
CORS(app)

template = {
  "swagger": "2.0",
  "info": {
    "title": "Pedro's API",
    "description": "Pedro's blog engine demonstration",
    "contact": {
      "responsibleOrganization": "ME",
      "responsibleDeveloper": "Me",
      "name": "Pedro de Medeiros",
      "email": "pedro.medeiros@gmail.com",
      "url": ""
    },
    "version": "0.0.1"
  },
  "basePath": "/",  # base bash for blueprint registration
  "schemes": [ "http" ],
  "operationId": "getmyData"
}
swagger = Swagger(app, template=template)

# Configuração do banco de dados SQLite
DATABASE = 'database.db'

def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Criação da tabela se ela não existir
    cursor.execute('''CREATE TABLE IF NOT EXISTS blog
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       title TEXT NOT NULL,
                       body TEXT NOT NULL,
                       author TEXT NOT NULL,
                       date DATETIME NOT NULL default CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


@app.route('/posts', methods=['GET'])
def list_posts():
    """
    Retorna a lista de artigos de blog salvos.
    ---
    responses:
      200:
        description: Lista de artigos de blog retornada com sucesso.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: ID do artigo de blog.
              title:
                type: string
                description: título do artigo de blog.
              date:
                type: string
                description: data de criação do artigo de blog.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Recuperando todos os usuários do banco de dados
    cursor.execute("SELECT id, title, author, date FROM blog")
    rows = cursor.fetchall()
    conn.close()

    blog = []
    for row in rows:
        post = { 'id': row[0], 'title': row[1], 'author':  row[2], 'date': row[3] }
        blog.append(post)

    return jsonify(blog)


@app.route('/blog/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    Retorna um blog post pelo ID.
    ---
    parameters:
      - name: post_id
        in: path
        description: ID do blog post
        required: true
        type: integer
    responses:
      200:
        description: dados do blog post
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: ID do blog post
                title:
                  type: string
                  description: título do blog post
                date:
                  type: string
                  format: date-time
                  description: data e hora do blog post
      404:
        description: não encontrado
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: mensagem de erro
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Recuperando um artigo específico pelo ID
    cursor.execute("SELECT * FROM blog WHERE id=?", (post_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        result = {
            'id':    row[0],
            'title': row[1],
            'body':  row[2],
            'date':  row[3]
        }
        return jsonify(result)
    else:
        return jsonify({'message': 'não encontrado.'}), 404


@app.route('/blog/add', methods=['POST'])
def add_post():
    """
    Adiciona um novo blog post ao banco de dados.
    ---
    parameters:
      - name: body
        in: formData
        type: string
        required: true
        description: corpo do artigo de blog.
      - name: title
        in: formData
        type: string
        required: true
        description: título do artigo do blog.
      - name: author
        in: formData
        type: string
        required: true
        description: nome do autor do artigo de blog.
    responses:
      201:
        description: artigo de blog adicionado com sucesso.
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID do artigo de blog adicionado.
            title:
              type: string
              description: título do artigo de blog adicionado.
            body:
              type: string
              description: corpo do artigo de blog adicionado.
      400:
        description: Dados inválidos fornecidos.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Descrição do erro.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    title = request.form['title']
    body = request.form['body']
    author = request.form['author']

    # Inserindo um novo usuário no banco de dados
    cursor.execute("INSERT INTO blog (title, body, author) VALUES (?, ?, ?)", (title, body, author))
    pid = cursor.lastrowid

    conn.commit()
    conn.close()

    new_post = {
        'id': pid,
        'title': title,
        'body': body,
        'author': author,
    }
    return jsonify(new_post), 201


if __name__ == '__main__':
    create_database()
    app.run(debug=True, port=5000)
