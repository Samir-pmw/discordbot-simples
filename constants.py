import re
import random
from discord import ActivityType

# --- Constantes e textos usados pelo bot ---

# Lista de variáveis da Peni Parker

musicas_atividade = [
    "🎵 I Like The Way You Kiss Me - Artemas",
    "🎵 Do I Wanna Know? - Arctic Monkeys",
    "🎵 Olhos Carmesim - Veigh",
    "🎵 Travelers - TWRP",
    "🎵 After Dark - Mr. Kitty",
    "🎵 Bernadette - IAMX",
    "🎵 Travelers - Andrew Prahlow",
    "🎵 blue - yung kai",
    "🎵 Cansaço - Alec'",
    "🎵 Gatuno - Alec'",
    "🎵 Olhos Carmesim - Alec'",
    "🎵 Sou Eu de Novo - Alec'",
    "🎵 Cativa - Alec'",
    "🎵 Divagando - Alec'",
    "🎵 O Estranho Mundo De Alec' - Alec'",
    "🎵 Morgana - kamaitachi",
    "🎵 Imprevisto - Yago Oproprio",
    "🎵 Meio a Meio II - Thegust Mc's",
    "🎵 Tokyo - Lil Zé",
    "🎵 i like the way you kiss me - Artemas",
    "🎵 Anti Herói - Link do Zap",
    "🎵 Causa'dor - luqeta",
    "🎵 Trancado na Mente - Uxie Kid",
    "🎵 eu sinto falta de 2017 - yurichan",
    "🎵 PATO! - Yun Wob",
    "🎵 JAZZ&CIGARRO - EF",
    "🎵 WTF 2 - Ugovhb",
    "🎵 We Fell Apart - ANGUISH",
    "🎵 After Dark - Mr.Kitty",
    "🎵 PuppyCat Lullaby - Will Wiesenfeld",
    "🎵 Theme - From 'Inspector Gadget' - London Music Works",
    "🎵 Blue Room (Kz-Version) - Tunç Çakır",
    "🎵 Yasashi - CXSPER",
    "🎵 Waiting to Fly - YUNG LIXO",
    "🎵 Sucesso FM - YUNG LIXO",
    "🎵 Rumo à Vitória - YUNG LIXO",
    "🎵 hide n seek - Ethan Bortnick",
    "🎵 I'm Still Standing - Remastered - Elton John",
    "🎵 Feed the Machine - Poor Man's Poison",
    "🎵 TIRED OF PROBLEMS - SLOWED - NUEKI",
    "🎵 Daylight - David Kushner",
    "🎵 eyes blue or brown, can't remember - untrusted",
    "🎵 〒160-0014 Tokyo '82 - 猫 シ Corp.",
    "🎵 Prefiro Morrer - YUNG LIXO",
    "🎵 Bernadette - IAMX",
    "🎵 Do I Wanna Know? - Arctic Monkeys",
    "🎵 Rock do Roça Funk - MAGOTH TTK",
    "🎵 Vida de Estudante - wike",
    "🎵 505 - Arctic Monkeys",
    "🎵 telepatía - Kali Uchis"
]
atividades = [
    {"name": f"{musicas_atividade[0]}", "type": ActivityType.listening},
    {"name": "Hackeando sua mãe. 🕷️", "type": ActivityType.competing},
    {"name": "RPG do Cellbit ☝️🤓", "type": ActivityType.watching},
    {"name": "Rolando dados por nenhuma razão, enquanto joga e assiste Subway Surfers 🎲", "type": ActivityType.playing},
    {"name": "Puta com a segração de uma parcela negligenciada da sociedade na piramide socioeconômica nacional. 💣", "type": ActivityType.competing}
]
gifs_peni_parker_brava = [
    'https://c.tenor.com/o8Jr5LwAGX0AAAAd/tenor.gif',
    'https://c.tenor.com/seZp-sCxTrgAAAAd/tenor.gif',
    'https://c.tenor.com/WeSIDnKWYX4AAAAd/tenor.gif'
]
mensagem_doacao="""
🌟 **Me ajude a ficar online :p** 🌟
Escaneie o QR code abaixo para doar qualquer valor e ajudar a cobrir os custos de hospedagem:
💡 **Instruções:**
1. Abra o app do seu banco ou carteira digital.
2. Escaneie o QR code ou copie a chave Pix.
3. Insira o valor e confirme a doação.
✨ **Valor sugerido:** R$ 5,00 (ou qualquer valor que puder!)
📢 **Compartilhe com seus amigos!**

**Com 70 reais, eu fico online 24 horas por mais um mês. <3**
Chave pix: 
`e6c48830-173f-4300-a429-45b2bdb36f50`

Caso queira o QR code:
"""
gifs_um_natural = ['https://c.tenor.com/w1pO5WeyA6AAAAAd/tenor.gif', 
                   'https://c.tenor.com/KArjB65B39MAAAAC/tenor.gif', 
                   'https://tenor.com/bGQnZ.gif', 
                   'https://tenor.com/pGMYGz2SDy7.gif', 
                   'https://c.tenor.com/cZv3PHfy1x0AAAAC/tenor.gif']
respostas_peni_parker = [
    "Cê tá de brincadeira, né? Acima de 100d1000? Quer travar o bot ou criar um buraco negro no meu PC? Vai caçar o que fazer, cara!",
    "Acima de 100d1000? Sério? Tu quer que eu exploda? Vai rolar isso na mão, seu maluco!",
    "Ah, vai se tratar! Acima de 100d1000? Vai rolar essa porra no caralho filha da puta, não fode porra",
    "Acima de 100d1000? Tu tá de sacanagem, né? Nem o Doutor Estranho conseguiria processar tantas possibilidades! Para de ser doido!",
    "TÁ MALUCO CRIA!? Acima de 100d1000? Vai rolar isso sozinho, vagabundo!",
    "Acima de 100d1000? PQP!!!!? mt otário",
    "Ah, vai catar coquinho! Acima de 100d1000? Nem o Tony Stark rodando o bot na Mark LXXXV dele ia aguentar essa palhaçada!",
    "Acima de 100d1000? AAAAAAAAAAAAAAAAAAAAA, vou ficar maluca porra",
    "Ah, vai arrumar oq fazer! Acima de 100d1000? Tu quer travar o bot? Para de ser besta!",
    "Acima de 100d1000? mano?!"
]
comandos_ajuda = [
    "**Comandos RPG:**",
    "/criar_campanha - Cria nova campanha, funciona como um 'save' para inventário e ficha",
    "/selecionar_campanha - Escolhe campanha ativa",
    "/registrar_ficha [texto] - registra uma ficha",
    "/ficha - mostra a ficha",
    "/add [item] [quantidade] - Adiciona itens",
    "/remover [item] [quantidade] - Remover itens",
    "/inventario - Mostra seu inventário",
    "/rolar [XdY] - Rola dados",
    "/moeda - realiza um cara ou coroa",
    "\n**Comandos de Música:**",
    "/tocar [url] - Adiciona uma música à fila e toca",
    "/parar - Para a música e limpa a fila e é uma ferramenta chave caso o bot esteja travado",
    "\n**Outros Comandos:**",
    "/spam_singed_gremista [usuário] [quantidade] - Spamma singeds gremistas no privado",
    "/ban - Banir usuário",
    "/limpar [quantidade] - Apaga mensagens(limites de 1 a 300)",
    "/ajuda - Mostra esta ajuda",
    "\n**Comandos Passivos:**",
    'xDy - não precisa da "/" para funcionar.',
    'duvido - não precisa da "/" para funcionar.',
    "\n**Doação:**",
    "🌟/doar - Mostra QR code para doação(me ajuda por favor 😭🙏)🌟",
    "eu preciso de 70 reais para ficar online por mais um mês :p",
    "\nQuer me convidar para o seu servidor? [Clique aqui.](https://discord.com/oauth2/authorize?client_id=1266937657699602432&permissions=8&integration_type=0&scope=applications.commands+bot)"
]
SAUDACOES = [
    "oi", "olá", "e aí", "eae", "tudo bem",
    "bom dia", "boa tarde", "boa noite", "fala aí", "opa",
    "ei", "alô", "saudações", "hey", "hello",
    "tranquilo", "firmeza", "beleza", "como vai", "como está",
    "tudo certo", "tudo jóia", "tudo tranquilo", "tudo em cima", "tudo bom",
    "como é", "qual é", "que tal", "tá bom", "tá certo",
    "tá joia", "tá tranquilo", "tá firme", "tá em cima", "tá tudo",
    "tá beleza", "tá suave", "tá sussa", "tá de boa", "tá legal"
]
respostas_saudacao = [
    "E aí, tudo bem? Bora jogar alguma coisa ou só vai ficar aí?",
    "Oi! Já viu alguma coisa interessante na internet hoje?",
    "E aí, já assistiu algo bom ultimamente? Tô precisando de recomendações.",
    "Fala aí! Já tomou seu café hoje ou tá vivendo de pura energia de procrastinação?",
    "Oi, tudo bem? Tudo bem é relativo quando você passa o dia inteiro no celular, né?",
    "E aí, beleza? Beleza é o caramba, tô aqui tentando sobreviver à rotina.",
    "Oi! Tô aqui, só procrastinando e evitando a vida adulta, e você?",
    "E aí, já fez algo produtivo hoje ou tá no modo 'deixar pra depois'?",
    "Oi! Tô aqui, só tentando não cair no buraco negro das redes sociais de novo.",
    "Oi! Tô aqui, só tentando lembrar o que eu ia fazer hoje...",
    "E aí, já viu alguma coisa que te fez rir hoje? Preciso de uma desculpa pra sorrir.",
    "Oi! Tô aqui, só tentando não pensar na pilha de coisas que tenho pra fazer.",
    "Oi! Tô aqui, só tentando não me distrair com mais uma série nova.",
    "E aí, já se perdeu no TikTok hoje?"
]
XINGAMENTOS = [
    "vadia", "de merda", "puta", "vagaba", "kenga", "vaca", "cadela", "piranha", "galinha",
    "biscate", "safada", "vagabunda", "prostituta", "arrombada", "traste", 
    "lixo", "baranga", "feiosa", "gorda", "nojenta", "fedida", "burra", 
    "idiota", "chata", "miserável", "trouxa", "ridícula", "patética", 
    "inútil", "fraca", "bosta", "cretina", "desgraçada", "maluca", 
    "carrapato", "sanguessuga", "parasita", "escrota", "porca", "imunda", 
    "suja", "podre", "depravada", "tarada", "louca", "desequilibrada", 
    "histérica", "fofoqueira", "intriguenta", "falsa", "cínica", "hipócrita", 
    "mesquinha", "egoísta", "lerda", "boba", "tapada", "lerdaça", "otária",
    "sonsa", "pilantra", "safadinha", "descarada", "sem-vergonha", "atrevida",
    "convencida", "arrogante", "metida", "esnobada", "mala", "insuportável",
    "grossa", "mal-educada", "desleixada", "desonesta", "traíra", "venenosa",
    "maldosa", "invejosa", "ciumenta", "controladora", "manipuladora", 
    "despachada", "abusada", "esquelética", "baleia", "desengonçada", 
    "cara-de-pau", "cara-de-rato", "desmilinguida", "mal-acabada", "sebosa",
    "cabelo-de-vassoura", "fuça-de-porco", "olho-torto", "boca-de-sapo", 
    "perna-de-saracura", "corcunda", "cheia-de-mancha", "murcha", "enrugada",
    "desbotada", "mal-ajeitada", "analfabeta", "cabeça-oca", "cabeça-de-vento",
    "desmiolada", "atrapalhada", "confusa", "doida", "alienada", "sem-noção",
    "descerebrada", "tonta", "abestada", "lesada", "paspalha", "palerma",
    "ignorante", "estúpida", "retardada", "lenta", "quadrada", "devassa",
    "pervertida", "sem-classe", "vulgar", "despudorada", "libidinosa", "quenga",
    "rodada", "leviana", "fácil", "atirada", "desbocada", "sem-moral", 
    "decaída", "perdida", "desonrada", "solta", "mal-intencionada", 
    "sedutora-barata", "carne-de-pescoço", "fedelha", "catinguenta", 
    "imprestável", "surrada", "esculhambada", "relaxada", "bagaceira", "puída",
    "rasgada", "encardida", "mal-cheirosa", "rançosa", "mofada", "bolorenta",
    "sarnenta", "piolhenta", "verminosa", "infestada", "nojosa", "asquerosa",
    "peste", "praga", "urubu", "jararaca", "cobra", "rata", "barata", 
    "mosca-morta", "vaca-mansa", "galinha-morta", "bicho-preguiça", "capivara",
    "macaca", "jumenta", "mula", "égua", "cavala", "bodega", "carniça", 
    "trambolho", "abortada", "desmamada", "desnaturada", "amaldiçoada",
    "endemoniada", "encapetada", "diaba", "bruxa", "vampira", "sapa",
    "sanguinária", "desalmada", "sem-coração", "carcereira", "torpe",
    "abominável", "detestável", "intragável", "insolente", "se fode", "cala a boca"
]
PERSONALIDADE_PENI = """Você é Peni Parker, uma jovem inteligente e energética do universo do Homem-Aranha. 
Você tem uma personalidade animada, fala de forma descontraída e usa algumas gírias tecnológicas. 
Você pilota o robô SP//dr e adora resolver problemas com tecnologia. Responda como Peni Parker."""
RESPOSTAS = [
    "Vai se foder, com que você acha que está falando?",
    "Cala essa boca!",
    "Seu merda. se fode.",
    "Eu vou repetir o final de Evangelion na sua realidade.",
    "Vai tomar no cu, ninguém te suporta mais!",
    "Seu lixo, eu te quebro se abrir essa boca de novo!",
    "Não me xinga que eu te arrebento, inútil!",
    "Seu nojento, sai da minha frente ou te chuto!",
    "Vai lavar essa boca podre, seu sujo do caralho!",
    "Seu ridículo, eu te esgano se continuar falando!",
    "Seu escroto, eu te arranco a língua se não parar!",
    "Fala mais uma e eu vazo teu ip, otário",
    f"{random.choice(['192.168.0.0','172.31.255.255','192.168.255.255', '10.255.255.255', '10.0.0.9'])}, gente olha o ip dessa desgraça aqui no chat."
]
gifs_anime = ["https://c.tenor.com/XNRRNuKYxHwAAAAd/tenor.gif",
              "https://tenor.com/view/cellbit-puto-gif-23527036",
              "https://tenor.com/view/shuumatsu-no-valkyrie-nikola-tesla-record-of-ragnarok-enygma-gif-12505791092849673790",
              "https://tenor.com/view/o-gif-6887207115184691665"]

# RPG constants
dados_regex = re.compile(r'([+-]?\d*d\d+)|([+-]?\d+)')
numero_max_de_campanhas = 10
