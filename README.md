# Lain Bot
<p align="center">
  <img src="https://i.pinimg.com/736x/6c/ef/fb/6ceffb9310699f63aa4cfe58b67bf2dc.jpg" width="30%" />
</p>
Lain Bot é um bot multifuncional para Discord, desenvolvido para auxiliar em sessões de RPG, tocar música, e interagir com os usuários de forma divertida e dinâmica. 

## Funcionalidades

### Comandos de RPG
- **/painel_rpg** - Mostra um layout para te ajudar a gerenciar ficha e inventário.
- **/rolar [XdY]** - Rola dados
- **/moeda** - realiza um cara ou coroa

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
- FFmpeg instalado e presente no PATH (necessário para tocar áudio).
- Bibliotecas Python listadas em `requirements.txt` (inclui `PyNaCl`, obrigatório para voz).

#### Instalando o FFmpeg no Windows
1. Baixe o pacote estático em [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (ou diretamente pela [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) – use a *release full*).
2. Extraia o `.zip` em uma pasta sem espaços, por exemplo `C:\ffmpeg`.
3. Adicione o diretório `bin` do FFmpeg à variável de ambiente `Path` do Windows (o nome é exatamente `Path`, com P maiúsculo). O caminho vai depender da pasta em que você extraiu o pacote. Exemplos válidos:
   - `C:\ffmpeg\bin` (se você renomeou a pasta para algo simples)
   - `C:\ffmpeg-2025-11-17-git-e94439e49b-essentials_build\bin` (nome completo criado pelo zip recém-baixado)

   Passo a passo para editar o `Path`:
   - Abra o menu Iniciar, digite **"variáveis de ambiente"** e clique em `Editar as variáveis de ambiente do sistema`.
   - Na janela que abrir, clique em **"Variáveis de Ambiente"**.
   - Selecione `Path` em **Variáveis do sistema** (ou do usuário) e clique em **Editar** → **Novo**.
   - Cole o caminho completo do `bin` (por exemplo `C:\ffmpeg-2025-11-17-git-e94439e49b-essentials_build\bin`), confirme tudo com **OK** e feche as janelas.
4. Feche e reabra o terminal (PowerShell/CMD) e confirme com `ffmpeg -version`.

> Se preferir usar um gerenciador de pacotes, `choco install ffmpeg` (Chocolatey) ou `scoop install ffmpeg` também funcionam.

##### Definindo o caminho manualmente
Se mesmo após editar o `Path` o bot não localizar o executável, você pode informar o caminho diretamente nas variáveis de ambiente:

```
PENIBOT_FFMPEG=C:\ffmpeg-2025-11-17-git-e94439e49b-essentials_build\bin\ffmpeg.exe
PENIBOT_FFPROBE=C:\ffmpeg-2025-11-17-git-e94439e49b-essentials_build\bin\ffprobe.exe
```

Basta adicionar essas linhas ao seu `.env` (ou às variáveis de usuário do Windows) e reiniciar o bot. O código prioriza esses caminhos explícitos antes de procurar no `Path`.

> Observação: em arquivos `.env`, use barras duplas (`\\`) ou barras normais (`/`) para evitar que sequências como `\n` sejam interpretadas pelo loader. Exemplos válidos: `C:\\ffmpeg\\bin\\ffmpeg.exe` ou `C:/ffmpeg/bin/ffmpeg.exe`.

Ao iniciar o bot, procure no console/log a mensagem `FFmpeg detectado em '...'`. Se ela não aparecer (ou vier uma advertência dizendo que não encontrou), revise os caminhos informados.

### Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/peni-parker-bot.git
   cd peni-parker-bot

2. Instale as dependências (inclui PyNaCl e os extras de voz do discord.py):
```bash
pip install -r requirements.txt
```

> Se você já tinha o ambiente configurado antes e está vendo o erro `PyNaCl library needed in order to use voice`, execute novamente o comando acima ou rode `pip install PyNaCl discord.py[voice]` para garantir que a biblioteca de voz está presente.

3. Crie um arquivo `.env` na raiz do projeto e adicione as variáveis necessárias (veja o exemplo abaixo).

4.Execute o bot:  
python bot.py  

#### Exemplo seguro de `.env`

```env
DISCORD_TOKEN=coloque_seu_token_do_discord_aqui
OPENAI_TOKEN=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
TENOR_TOKEN=sua_chave_do_tenor
GOOGLE_DRIVE_FOLDER_ID=opcional

PENIBOT_FFMPEG=C:\\ffmpeg-2025-11-17-git-e94439e49b-essentials_build\\bin\\ffmpeg.exe
PENIBOT_FFPROBE=C:\\ffmpeg-2025-11-17-git-e94439e49b-essentials_build\\bin\\ffprobe.exe
```

> Nunca versione o seu `.env`. O arquivo real contém credenciais sensíveis e já está listado no `.gitignore`.

### Onde ficam os arquivos gerados

- Todos os arquivos temporários (músicas, fichas, inventários e logs) são criados dentro de `%APPDATA%\PeniBot`.
- Se você usar a versão do Python distribuída pela Microsoft Store, o Windows virtualiza essa pasta. O conteúdo real ficará em `C:\Users\SEU_USUARIO\AppData\Local\Packages\PythonSoftwareFoundation.Python.<versão>\LocalCache\Roaming\PeniBot`.
- Assim que o bot inicia, ele registra (no console e no log) o caminho detectado. Se houver virtualização, a mensagem mostra explicitamente onde os arquivos estão.
- Você também pode navegar manualmente pelo Explorador de Arquivos até o caminho da `LocalCache` indicado acima para visualizar todos os dados gerados.

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

Quer falar comigo? [Clique aqui](https://papiro.dev/) :)


### Explicação do README.md

1. **Título e Descrição**: Introduz o bot e sua inspiração.
2. **Funcionalidades**: Lista os principais comandos e funcionalidades.
3. **Configuração**: Explica como configurar o ambiente e executar o bot.
4. **Uso**: Fornece exemplos de como usar os comandos.
5. **Contribuição**: Convida outros a contribuir para o projeto.
6. **Licença**: Informa sobre a licença do projeto.
7. **Contato**: Fornece informações de contato para dúvidas ou sugestões.

Esse `README.md` é um guia básico para quem deseja usar ou contribuir com o seu bot. Você pode personalizá-lo conforme necessário!
