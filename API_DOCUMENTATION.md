# UFRJ Move - Documentação de Integração da API (Frontend)

Esta documentação detalha todos os endpoints da API do **UFRJ Move**, os formatos de dados para envio (Request) e recebimento (Response), e como estruturar a integração no frontend.

* **URL Base de Produção:** `https://ufrj-move.onrender.com`
* **URL Base de Desenvolvimento:** `http://localhost:5000`

---

## 1. Autenticação & Cadastro

### 1.1 Cadastro de Usuário (`POST /api/auth/register`)
Cria uma nova conta para o estudante.
* **Corpo da Requisição (JSON):**
  ```json
  {
    "name": "João Silva",
    "email": "joao@ufrj.br",
    "cpf": "123.456.789-09",
    "password": "senha_segura_123"
  }
  ```
  *Nota: O CPF pode ser enviado formatado (com pontos e traço) ou contendo apenas os 11 números. O backend limpa e armazena apenas números.*
* **Resposta de Sucesso (201 Created):**
  ```json
  {
    "message": "Usuário cadastrado com sucesso",
    "user": {
      "id": 1,
      "name": "João Silva",
      "email": "joao@ufrj.br",
      "cpf": "12345678909",
      "created_at": "2026-06-08T15:00:00"
    }
  }
  ```
* **Respostas de Erro:**
  * **400 Bad Request:** Dados incompletos ou senha com menos de 6 caracteres.
  * **409 Conflict:** E-mail ou CPF já cadastrados.

### 1.2 Login de Usuário (`POST /api/auth/login`)
Autentica o usuário e retorna o token JWT necessário para rotas protegidas.
* **Corpo da Requisição (JSON):**
  ```json
  {
    "email": "joao@ufrj.br",
    "password": "senha_segura_123"
  }
  ```
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "message": "Login realizado com sucesso",
    "token": "eyJhbGciOiJIUzI1NiIsIn...",
    "user": {
      "id": 1,
      "name": "João Silva",
      "email": "joao@ufrj.br",
      "cpf": "12345678909",
      "created_at": "2026-06-08T15:00:00"
    }
  }
  ```
  *Importante: O token retornado deve ser guardado (ex: `localStorage`) e enviado no cabeçalho das requisições protegidas como `Authorization: Bearer <token>`.*
* **Resposta de Erro (401 Unauthorized):**
  ```json
  {
    "error": "E-mail ou senha inválidos"
  }
  ```

---

## 2. Perfil do Usuário

### 2.1 Obter Perfil (`GET /api/user/profile`) (Protegido)
Retorna os dados do usuário autenticado.
* **Cabeçalho:** `Authorization: Bearer <SEU_TOKEN_JWT>`
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "id": 1,
    "name": "João Silva",
    "email": "joao@ufrj.br",
    "cpf": "12345678909",
    "created_at": "2026-06-08T15:00:00"
  }
  ```

---

## 3. Linhas, Pontos e Localizações de Ônibus

### 3.1 Listar Rotas Circulares (`GET /api/bus/routes`)
Busca todas as rotas circulares oficiais cadastradas e seus respectivos pontos de ônibus ordenados. Útil para montar seletores de rotas no frontend.
* **Resposta de Sucesso (200 OK):**
  ```json
  [
    {
      "id": 1,
      "name": "Circular Interno 1",
      "description": "Via Alojamento Estudantil. CT -> CCS -> EEFD -> Alojamento -> CT",
      "active": true,
      "stops": [
        {
          "id": 1,
          "route_id": 1,
          "bus_stop_id": 1,
          "sequence_order": 1,
          "bus_stop": {
            "id": 1,
            "name": "Centro de Tecnologia (CT)",
            "latitude": -22.8239,
            "longitude": -43.2302
          }
        },
        {
          "id": 2,
          "route_id": 1,
          "bus_stop_id": 8,
          "sequence_order": 2,
          "bus_stop": {
            "id": 8,
            "name": "Prédio da Coppe (Bloco I/J)",
            "latitude": -22.8251,
            "longitude": -43.2325
          }
        }
      ]
    }
  ]
  ```

### 3.2 Transmitir Localização ("Modo Ônibus") (`POST /api/bus/location`) (Protegido)
Atualiza a localização atual do usuário que está a bordo de um ônibus. Deve ser chamado **a cada 5 segundos** pelo frontend enquanto o rastreamento estiver ativo.
* **Cabeçalho:** `Authorization: Bearer <SEU_TOKEN_JWT>`
* **Corpo da Requisição (JSON):**
  ```json
  {
    "route_id": 1,
    "latitude": -22.82392,
    "longitude": -43.23021
  }
  ```
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "message": "Localização atualizada",
    "data": {
      "id": 5,
      "user_id": 1,
      "user_name": "João Silva",
      "route_id": 1,
      "route_name": "Circular Interno 1",
      "latitude": -22.8239,
      "longitude": -43.2302,
      "active": true,
      "updated_at": "2026-06-08T15:45:00"
    }
  }
  ```

### 3.3 Parar Transmissão (`DELETE /api/bus/location`) (Protegido)
Informa ao backend que o usuário encerrou a viagem ou desligou o rastreamento, removendo a sua localização ativa do mapa.
* **Cabeçalho:** `Authorization: Bearer <SEU_TOKEN_JWT>`
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "message": "Transmissão interrompida com sucesso"
  }
  ```

### 3.4 Listar Ônibus Ativos (Consolidados) (`GET /api/bus/locations`)
Lista os ônibus em circulação no momento. O backend processa todas as transmissões ativas dos últimos 30 segundos e aplica um algoritmo de agrupamento (*clustering*) para consolidar múltiplos reportes na mesma rota em um único ônibus.
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "count": 1,
    "buses": [
      {
        "route_id": 1,
        "route_name": "Circular Interno 1",
        "latitude": -22.8239,
        "longitude": -43.2302,
        "validation_count": 2,
        "status": "validated",
        "updated_at": "2026-06-08T15:45:10Z",
        "next_stop": {
          "stop_id": 8,
          "name": "Prédio da Coppe (Bloco I/J)",
          "sequence_order": 2,
          "distance_meters": 350,
          "eta_minutes": 1.2
        },
        "stops_eta": [
          {
            "stop_id": 1,
            "name": "Centro de Tecnologia (CT)",
            "sequence_order": 1,
            "distance_meters": 15,
            "eta_minutes": 0.0
          },
          {
            "stop_id": 8,
            "name": "Prédio da Coppe (Bloco I/J)",
            "sequence_order": 2,
            "distance_meters": 350,
            "eta_minutes": 1.2
          }
        ]
      }
    ],
    "raw_locations": [
      {
        "id": 5,
        "user_id": 1,
        "user_name": "João Silva",
        "route_id": 1,
        "route_name": "Circular Interno 1",
        "latitude": -22.82392,
        "longitude": -43.23021,
        "active": true,
        "updated_at": "2026-06-08T15:45:10"
      }
    ]
  }
  ```
  * **Significado dos Campos Principais:**
    * `validation_count`: Quantos estudantes distintos estão atualmente transmitindo o sinal a partir deste ônibus.
    * `status`: `"validated"` se houver 2 ou mais pessoas reportando (alerta confiável) ou `"pending"` se houver apenas 1 pessoa.
    * `next_stop`: O ponto de ônibus mais próximo onde o veículo se encontra (ou está prestes a chegar).
    * `stops_eta`: Array ordenado com o tempo estimado de chegada (`eta_minutes`) e distância (`distance_meters`) do ônibus até **cada um** dos pontos do circular.
    * `raw_locations`: Histórico bruto individual dos reportes (útil para fins de debug).
