# UFRJ Move - Backend

Este é o backend do projeto **UFRJ Move**, um aplicativo colaborativo de monitoramento de transporte interno (ônibus) da UFRJ no Fundão.

Desenvolvido com **Python**, **Flask**, **Flask-SQLAlchemy**, **Flask-JWT-Extended** e **Flask-CORS**.

## Estrutura do Projeto

* `app.py`: Arquivo principal de inicialização do servidor.
* `config.py`: Configurações de ambiente, chave secreta e banco de dados.
* `models.py`: Definição do banco de dados (Tabelas `User` e `BusLocation`).
* `routes/`: Contém os controladores (endpoints) divididos por domínio (auth, user, bus).
* `app.db` (gerado automaticamente): Banco de dados local em SQLite.

## Como Executar Localmente

### Pré-requisitos
* Python 3.8+ instalado.

### Passos

1. Abra o terminal (no diretório deste projeto).
2. É recomendável criar e ativar um ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute o servidor:
   ```bash
   python app.py
   ```
5. O servidor estará rodando em `http://localhost:5000`.

---

## Integração com Frontend (Axios)

Aqui estão exemplos práticos de como chamar a API pelo frontend usando a biblioteca **Axios**.

### Configuração do Axios

Você pode criar uma instância base do Axios no seu frontend:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api', // Ajuste para a URL de produção depois
});

// Interceptor para adicionar o token JWT em requisições automáticas
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ufrjMoveToken'); // Pega token salvo no login
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 1. Cadastro
```javascript
const handleRegister = async () => {
  try {
    const response = await api.post('/register', {
      name: "João Silva",
      email: "joao@ufrj.br",
      password: "senha_segura"
    });
    console.log("Cadastro com sucesso:", response.data);
  } catch (error) {
    console.error("Erro no cadastro:", error.response.data.error);
  }
};
```

### 2. Login
```javascript
const handleLogin = async () => {
  try {
    const response = await api.post('/login', {
      email: "joao@ufrj.br",
      password: "senha_segura"
    });
    
    // Salva o token localmente
    localStorage.setItem('ufrjMoveToken', response.data.token);
    console.log("Login com sucesso, token e dados:", response.data);
  } catch (error) {
    console.error("Erro no login:", error.response.data.error);
  }
};
```

### 3. Obter Perfil
```javascript
const getProfile = async () => {
  try {
    const response = await api.get('/profile');
    console.log("Dados do perfil:", response.data);
  } catch (error) {
    console.error("Erro ao obter perfil. Token pode ser inválido.", error);
  }
};
```

### 4. Modo Ônibus (Transmitindo) - Chamar a cada 5 segundos
```javascript
let broadcastInterval = null;

const startBroadcasting = () => {
  // Configura um intervalo para rodar a cada 5 segundos (5000ms)
  broadcastInterval = setInterval(async () => {
    try {
      // Usa as APIs nativas de Geolocation do celular/navegador
      const location = await getCurrentGPSLocation(); // função fictícia
      
      const response = await api.post('/bus/location', {
        latitude: location.lat,
        longitude: location.lng,
        route: "Circular Interno"
      });
      console.log("Localização atualizada:", response.data);
    } catch (error) {
      console.error("Erro ao enviar localização", error);
    }
  }, 5000);
};
```

### 5. Parar Transmissão
```javascript
const stopBroadcasting = async () => {
  if (broadcastInterval) {
    clearInterval(broadcastInterval);
    broadcastInterval = null;
  }
  
  try {
    await api.delete('/bus/location');
    console.log("Transmissão parada com sucesso.");
  } catch (error) {
    console.error("Erro ao parar transmissão", error);
  }
};
```

### 6. Mapa (Buscar Ônibus Ativos)
```javascript
// O Mapa do frontend pode chamar essa rota para plotar pinos
const fetchBusLocations = async () => {
  try {
    const response = await api.get('/bus/locations');
    const { count, locations } = response.data;
    
    console.log(`Recebidos ${count} ônibus ativos`, locations);
    // Para cada location, plote no Google Maps:
    // locations.forEach(bus => renderMarker(bus.latitude, bus.longitude, bus.route));
  } catch (error) {
    console.error("Erro ao buscar localizações", error);
  }
};
```
