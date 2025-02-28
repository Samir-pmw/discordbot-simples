# Peni Parker Bot

Peni Parker Bot é um bot multifuncional para Discord, desenvolvido para auxiliar em sessões de RPG, tocar música, e interagir com os usuários de forma divertida e dinâmica. Inspirado na personagem Peni Parker do universo do Homem-Aranha, o bot possui uma personalidade única e oferece uma variedade de comandos para entreter e ajudar os usuários.

## Funcionalidades

### Comandos de RPG
- **/criar_campanha**: Cria uma nova campanha de RPG.
- **/selecionar_campanha**: Seleciona uma campanha para uso.
- **/registrar_ficha**: Registra uma ficha de personagem.
- **/ficha**: Exibe a ficha de personagem atual.
- **/add**: Adiciona itens ao inventário.
- **/remover**: Remove itens do inventário.
- **/inventario**: Exibe o inventário da campanha.
- **/rolar**: Rola dados no formato XdY+Z.
- **/moeda**: Joga uma moeda (cara ou coroa).

### Comandos de Música
- **/tocar**: Toca uma música ou playlist do YouTube ou Spotify.
- **/parar**: Para a música e limpa a fila de reprodução.

### Outros Comandos
- **/spam_singed_gremista**: Envia uma imagem do Singed Gremista no privado de um usuário.
- **/ban**: Bane um usuário do servidor (requer permissões).
- **/limpar**: Apaga mensagens do canal (requer permissões).
- **/ajuda**: Exibe uma lista de comandos disponíveis.

### Comandos Passivos
- **xDy**: Rola dados automaticamente sem necessidade de comando.
- **Saudações**: Responde a saudações como "oi", "bom dia", etc.
- **Xingamentos**: Responde a xingamentos de forma humorística.

## Configuração

### Pré-requisitos
- Python 3.8 ou superior.
- Bibliotecas Python: `discord.py`, `yt-dlp`, `spotipy`, `python-dotenv`, `openai`.

### Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/peni-parker-bot.git
   cd peni-parker-bot

2.Instale as dependências:
pip install -r requirements.txt  

3.Crie um arquivo .env na raiz do projeto e adicione as seguintes variáveis de ambiente:
DISCORD_TOKEN=seu_token_do_discord  
OPENAI_TOKEN=seu_token_da_openai  
SPOTIFY_TOKEN=seu_token_do_spotify

4.Execute o bot:  
python bot.py  

Uso
Comandos Básicos
/ajuda: Exibe uma lista de todos os comandos disponíveis.

/rolar 1d20: Rola um dado de 20 lados.

/tocar <url>: Toca uma música ou playlist do YouTube ou Spotify.

Exemplos de Uso
Rolagem de Dados:/rolar 2d6+3
Resultado: Rola dois dados de 6 lados e soma 3 ao resultado.

Tocar Música:/tocar https://www.youtube.com/watch?v=dQw4w9WgXcQ
Resultado: Adiciona a música à fila e começa a tocar.

Adicionar Item ao Inventário:/add Espada 1
Resultado: Adiciona uma espada ao inventário da campanha selecionada.

Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

Quer me falar comigo? [Clique aqui](https://konect.gg/vezkalin) :)


### Explicação do README.md

1. **Título e Descrição**: Introduz o bot e sua inspiração.
2. **Funcionalidades**: Lista os principais comandos e funcionalidades.
3. **Configuração**: Explica como configurar o ambiente e executar o bot.
4. **Uso**: Fornece exemplos de como usar os comandos.
5. **Contribuição**: Convida outros a contribuir para o projeto.
6. **Licença**: Informa sobre a licença do projeto.
7. **Contato**: Fornece informações de contato para dúvidas ou sugestões.

Esse `README.md` é um guia básico para quem deseja usar ou contribuir com o seu bot. Você pode personalizá-lo conforme necessário!
